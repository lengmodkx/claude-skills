#!/usr/bin/env python3
"""
月度报表可视化图表生成器
根据日记文件生成 ECharts 图表并截图保存为 PNG
"""

import argparse
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
import http.server
import socketserver
import threading
import time

# 导入图表模板
from chart_templates import (
    SLEEP_CHART_TEMPLATE,
    BLOOD_SUGAR_CHART_TEMPLATE,
    SPENDING_CHART_TEMPLATE,
    OKR_CHART_TEMPLATE,
    DASHBOARD_TEMPLATE,
)


def find_diary_files(base_dir: str, year: int, month: int) -> list:
    """查找指定年月的所有日记文件"""
    diary_dir = Path(base_dir) / "日记" / str(year) / f"{month}月"
    if not diary_dir.exists():
        print(f"日记目录不存在: {diary_dir}")
        return []

    # 查找所有 YYYY-MM-DD.md 格式的文件
    pattern = re.compile(rf"^{year}-{month:02d}-(\d{{2}})\.md$")
    files = []

    for file_path in diary_dir.rglob("*.md"):
        if pattern.match(file_path.name):
            files.append(file_path)

    return sorted(files)


def parse_sleep_data(content: str) -> dict:
    """解析睡眠质量数据"""
    sleep_match = re.search(r'[🌙😴]\s*睡眠质量[：:]\s*(差|一般|好)', content)
    if sleep_match:
        return {"quality": sleep_match.group(1)}
    return None


def parse_blood_sugar(content: str) -> dict:
    """解析血糖数据"""
    data = {}

    # 空腹血糖
    fasting_match = re.search(r'空腹.*?[：:]\s*(\d+\.?\d*)', content)
    if fasting_match:
        data['fasting'] = float(fasting_match.group(1))

    # 餐后2h血糖
    postprandial_match = re.search(r'餐后2h.*?[：:]\s*(\d+\.?\d*)', content)
    if postprandial_match:
        data['postprandial'] = float(postprandial_match.group(1))

    # 睡前血糖
    bedtime_match = re.search(r'睡前.*?[：:]\s*(\d+\.?\d*)', content)
    if bedtime_match:
        data['bedtime'] = float(bedtime_match.group(1))

    return data if data else None


def parse_spending(content: str) -> dict:
    """解析消费数据"""
    data = {}

    # 总支出
    total_match = re.search(r'总支出.*?[💰\*]*\s*[*\[]*([\d,]+\.?\d*)', content)
    if total_match:
        data['total'] = float(total_match.group(1).replace(',', ''))

    # 消费笔数
    count_match = re.search(r'消费笔数.*?([\d]+)\s*笔', content)
    if count_match:
        data['count'] = int(count_match.group(1))

    # 最大支出
    max_match = re.search(r'最大支出.*?([\d,]+\.?\d*)\s*元', content)
    if max_match:
        data['max'] = float(max_match.group(1).replace(',', ''))

    # 主要类别
    category_match = re.search(r'主要类别[：:]\s*(\S+)', content)
    if category_match:
        data['category'] = category_match.group(1)

    return data if data else None


def parse_okr(content: str) -> dict:
    """解析 OKR 数据"""
    data = {
        'todo': {'total': 0, 'completed': 0},
        'temp': {'total': 0, 'completed': 0},
        'kr': {'total': 0, 'completed': 0, 'in_progress': 0, 'cancelled': 0},
        'priority': {'P0': {'total': 0, 'completed': 0},
                    'P1': {'total': 0, 'completed': 0},
                    'P2': {'total': 0, 'completed': 0}}
    }

    # 检查是否有日OKR管理部分
    if '日OKR管理' not in content and '关键结果' not in content:
        return None

    # 提取今日待办
    todo_section = re.search(r'今日待办事项[\s\S]*?(?=临时任务|####|$)', content)
    if todo_section:
        todo_text = todo_section.group(0)
        # 统计待办总数和已完成
        todo_items = re.findall(r'- \[([ x])\]', todo_text)
        data['todo']['total'] = len(todo_items)
        data['todo']['completed'] = todo_items.count('x')

    # 提取临时任务
    temp_section = re.search(r'临时任务[\s\S]*?(?=####|$)', content)
    if temp_section:
        temp_text = temp_section.group(0)
        temp_items = re.findall(r'- \[([ x])\]', temp_text)
        data['temp']['total'] = len(temp_items)
        data['temp']['completed'] = temp_items.count('x')

    # 提取 KR 表格数据
    kr_rows = re.findall(r'\|\s*KR\d+\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*(P\d)\s*\|\s*(已完成|进行中|已 canceled)\s*\|', content)
    for row in kr_rows:
        task, okr_link, priority, status = row
        data['kr']['total'] += 1
        if '已完成' in status:
            data['kr']['completed'] += 1
        elif '进行中' in status:
            data['kr']['in_progress'] += 1
        elif '已取消' in status or 'canceled' in status:
            data['kr']['cancelled'] += 1

        # 统计优先级
        if priority in data['priority']:
            data['priority'][priority]['total'] += 1
            if '已完成' in status:
                data['priority'][priority]['completed'] += 1

    return data


def collect_statistics(files: list) -> dict:
    """收集所有统计数据"""
    stats = {
        'sleep': {'差': 0, '一般': 0, '好': 0},
        'blood_sugar': {
            'fasting': [],
            'postprandial': [],
            'bedtime': []
        },
        'spending': {
            'total': 0,
            'count': 0,
            'max': 0,
            'daily': [],
            'categories': {}
        },
        'okr': {
            'todo': {'total': 0, 'completed': 0},
            'temp': {'total': 0, 'completed': 0},
            'kr': {'total': 0, 'completed': 0, 'in_progress': 0, 'cancelled': 0},
            'priority': {'P0': {'total': 0, 'completed': 0},
                        'P1': {'total': 0, 'completed': 0},
                        'P2': {'total': 0, 'completed': 0}}
        },
        'days_count': len(files)
    }

    for file_path in files:
        content = file_path.read_text(encoding='utf-8')

        # 解析睡眠数据
        sleep = parse_sleep_data(content)
        if sleep and sleep['quality'] in stats['sleep']:
            stats['sleep'][sleep['quality']] += 1

        # 解析血糖数据
        bs = parse_blood_sugar(content)
        if bs:
            if 'fasting' in bs:
                stats['blood_sugar']['fasting'].append(bs['fasting'])
            if 'postprandial' in bs:
                stats['blood_sugar']['postprandial'].append(bs['postprandial'])
            if 'bedtime' in bs:
                stats['blood_sugar']['bedtime'].append(bs['bedtime'])

        # 解析消费数据
        spending = parse_spending(content)
        if spending:
            if 'total' in spending:
                stats['spending']['daily'].append(spending['total'])
                stats['spending']['total'] += spending['total']
            if 'count' in spending:
                stats['spending']['count'] += spending['count']
            if 'max' in spending:
                stats['spending']['max'] = max(stats['spending']['max'], spending['max'])
            if 'category' in spending:
                cat = spending['category']
                stats['spending']['categories'][cat] = stats['spending']['categories'].get(cat, 0) + 1

        # 解析 OKR 数据
        okr = parse_okr(content)
        if okr:
            for key in ['todo', 'temp']:
                stats['okr'][key]['total'] += okr[key]['total']
                stats['okr'][key]['completed'] += okr[key]['completed']

            for key in ['total', 'completed', 'in_progress', 'cancelled']:
                stats['okr']['kr'][key] += okr['kr'][key]

            for p in ['P0', 'P1', 'P2']:
                stats['okr']['priority'][p]['total'] += okr['priority'][p]['total']
                stats['okr']['priority'][p]['completed'] += okr['priority'][p]['completed']

    return stats


def calculate_summary(stats: dict, year: int, month: int) -> dict:
    """计算汇总数据"""
    summary = {
        'year': year,
        'month': month,
        'total_days': stats['days_count'],

        # 睡眠
        'sleep_bad': stats['sleep']['差'],
        'sleep_average': stats['sleep']['一般'],
        'sleep_good': stats['sleep']['好'],
        'sleep_good_rate': round(stats['sleep']['好'] / stats['days_count'] * 100, 1) if stats['days_count'] > 0 else 0,

        # 血糖
        'fasting_values': stats['blood_sugar']['fasting'],
        'postprandial_values': stats['blood_sugar']['postprandial'],
        'bedtime_values': stats['blood_sugar']['bedtime'],

        # 消费
        'total_spending': stats['spending']['total'],
        'daily_avg': round(stats['spending']['total'] / stats['days_count'], 2) if stats['days_count'] > 0 else 0,
        'transaction_count': stats['spending']['count'],
        'max_daily': stats['spending']['max'],
        'categories': stats['spending']['categories'],

        # OKR
        'okr': stats['okr']
    }

    # 计算血糖统计
    if summary['fasting_values']:
        summary['fasting_avg'] = round(sum(summary['fasting_values']) / len(summary['fasting_values']), 2)
        summary['fasting_min'] = min(summary['fasting_values'])
        summary['fasting_max'] = max(summary['fasting_values'])
        summary['fasting_normal_count'] = sum(1 for x in summary['fasting_values'] if 3.9 <= x <= 6.1)
        summary['fasting_rate'] = round(summary['fasting_normal_count'] / len(summary['fasting_values']) * 100, 1)
    else:
        summary['fasting_avg'] = 0
        summary['fasting_min'] = 0
        summary['fasting_max'] = 0
        summary['fasting_rate'] = 0

    if summary['postprandial_values']:
        summary['postprandial_avg'] = round(sum(summary['postprandial_values']) / len(summary['postprandial_values']), 2)
        summary['postprandial_min'] = min(summary['postprandial_values'])
        summary['postprandial_max'] = max(summary['postprandial_values'])
        summary['postprandial_normal_count'] = sum(1 for x in summary['postprandial_values'] if 4.4 <= x <= 7.8)
        summary['postprandial_rate'] = round(summary['postprandial_normal_count'] / len(summary['postprandial_values']) * 100, 1)
    else:
        summary['postprandial_avg'] = 0
        summary['postprandial_min'] = 0
        summary['postprandial_max'] = 0
        summary['postprandial_rate'] = 0

    # 消费类别金额（估算）
    total_cats = sum(summary['categories'].values())
    if total_cats > 0:
        summary['top_category'] = max(summary['categories'], key=summary['categories'].get)
        # 根据频次估算金额
        summary['food_amount'] = round(summary['total_spending'] * summary['categories'].get('餐饮', 0) / total_cats)
        summary['shopping_amount'] = round(summary['total_spending'] * summary['categories'].get('购物', 0) / total_cats)
        summary['transport_amount'] = round(summary['total_spending'] * summary['categories'].get('交通', 0) / total_cats)
        summary['entertainment_amount'] = round(summary['total_spending'] * summary['categories'].get('娱乐', 0) / total_cats)
        summary['other_amount'] = summary['total_spending'] - summary['food_amount'] - summary['shopping_amount'] - summary['transport_amount'] - summary['entertainment_amount']
    else:
        summary['top_category'] = '餐饮'
        summary['food_amount'] = round(summary['total_spending'] * 0.45)
        summary['shopping_amount'] = round(summary['total_spending'] * 0.20)
        summary['transport_amount'] = round(summary['total_spending'] * 0.15)
        summary['entertainment_amount'] = round(summary['total_spending'] * 0.10)
        summary['other_amount'] = summary['total_spending'] - summary['food_amount'] - summary['shopping_amount'] - summary['transport_amount'] - summary['entertainment_amount']

    # OKR 统计
    okr = summary['okr']
    summary['todo_total'] = okr['todo']['total']
    summary['todo_completed'] = okr['todo']['completed']
    summary['todo_rate'] = round(okr['todo']['completed'] / okr['todo']['total'] * 100, 1) if okr['todo']['total'] > 0 else 0

    summary['temp_total'] = okr['temp']['total']
    summary['temp_completed'] = okr['temp']['completed']
    summary['temp_rate'] = round(okr['temp']['completed'] / okr['temp']['total'] * 100, 1) if okr['temp']['total'] > 0 else 0

    summary['kr_total'] = okr['kr']['total']
    summary['kr_completed'] = okr['kr']['completed']
    summary['kr_rate'] = round(okr['kr']['completed'] / okr['kr']['total'] * 100, 1) if okr['kr']['total'] > 0 else 0

    summary['p0_total'] = okr['priority']['P0']['total']
    summary['p0_completed'] = okr['priority']['P0']['completed']
    summary['p0_rate'] = round(okr['priority']['P0']['completed'] / okr['priority']['P0']['total'] * 100, 1) if okr['priority']['P0']['total'] > 0 else 0

    summary['p1_total'] = okr['priority']['P1']['total']
    summary['p1_completed'] = okr['priority']['P1']['completed']
    summary['p1_rate'] = round(okr['priority']['P1']['completed'] / okr['priority']['P1']['total'] * 100, 1) if okr['priority']['P1']['total'] > 0 else 0

    summary['p2_total'] = okr['priority']['P2']['total']
    summary['p2_completed'] = okr['priority']['P2']['completed']
    summary['p2_rate'] = round(okr['priority']['P2']['completed'] / okr['priority']['P2']['total'] * 100, 1) if okr['priority']['P2']['total'] > 0 else 0

    summary['total_tasks'] = summary['todo_total'] + summary['temp_total'] + summary['kr_total']
    summary['overall_completed'] = summary['todo_completed'] + summary['temp_completed'] + summary['kr_completed']
    summary['overall_rate'] = round(summary['overall_completed'] / summary['total_tasks'] * 100, 1) if summary['total_tasks'] > 0 else 0

    summary['p0_pending'] = summary['p0_total'] - summary['p0_completed']

    # 血糖达标率（空腹）
    summary['blood_sugar_rate'] = summary['fasting_rate']

    # 生成时间
    summary['generate_time'] = datetime.now().strftime('%Y-%m-%d %H:%M')

    # CSS 样式类
    summary['fasting_class'] = 'warning' if summary['fasting_avg'] > 6.1 else 'success'
    summary['fasting_rate_class'] = 'warning' if summary['fasting_rate'] < 50 else 'success'
    summary['postprandial_class'] = 'warning' if summary['postprandial_avg'] > 7.8 else 'success'
    summary['postprandial_rate_class'] = 'warning' if summary['postprandial_rate'] < 50 else 'success'

    return summary


def generate_html_files(summary: dict, output_dir: str):
    """生成 HTML 图表文件"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    html_files = {}

    # 睡眠质量分布
    sleep_html = SLEEP_CHART_TEMPLATE.format(**summary)
    sleep_file = output_path / 'chart_sleep.html'
    sleep_file.write_text(sleep_html, encoding='utf-8')
    html_files['sleep'] = sleep_file

    # 血糖监测分析
    blood_sugar_html = BLOOD_SUGAR_CHART_TEMPLATE.format(**summary)
    blood_sugar_file = output_path / 'chart_blood_sugar.html'
    blood_sugar_file.write_text(blood_sugar_html, encoding='utf-8')
    html_files['blood_sugar'] = blood_sugar_file

    # 消费趋势分析
    spending_html = SPENDING_CHART_TEMPLATE.format(**summary)
    spending_file = output_path / 'chart_spending.html'
    spending_file.write_text(spending_html, encoding='utf-8')
    html_files['spending'] = spending_file

    # OKR完成情况
    okr_html = OKR_CHART_TEMPLATE.format(**summary)
    okr_file = output_path / 'chart_okr.html'
    okr_file.write_text(okr_html, encoding='utf-8')
    html_files['okr'] = okr_file

    # 综合数据看板
    dashboard_html = DASHBOARD_TEMPLATE.format(**summary)
    dashboard_file = output_path / 'charts_dashboard.html'
    dashboard_file.write_text(dashboard_html, encoding='utf-8')
    html_files['dashboard'] = dashboard_file

    return html_files


class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """简单的 HTTP 请求处理器"""
    def __init__(self, *args, directory=None, **kwargs):
        self.directory = directory
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, format, *args):
        # 静默日志
        pass


def start_http_server(directory: str, port: int = 8765):
    """启动 HTTP 服务器"""
    handler = lambda *args, **kwargs: SimpleHTTPRequestHandler(*args, directory=directory, **kwargs)
    httpd = socketserver.TCPServer(("", port), handler)
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    return httpd


def capture_screenshots(html_files: dict, output_dir: str, port: int = 8765):
    """使用 Playwright 截图"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("错误: 未安装 Playwright。请运行: pip install playwright && playwright install chromium")
        return None

    output_path = Path(output_dir)
    screenshots = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # 截图配置
        screenshot_configs = [
            ('sleep', '01_睡眠质量分布.png', 800, 600),
            ('blood_sugar', '02_血糖监测分析.png', 900, 700),
            ('spending', '03_消费趋势分析.png', 900, 600),
            ('okr', '04_OKR完成情况.png', 900, 600),
            ('dashboard', f'{summary["year"]}年{summary["month"]}月数据看板.png', 1400, 1000),
        ]

        for key, filename, width, height in screenshot_configs:
            if key in html_files:
                print(f"正在生成: {filename}...")
                page = browser.new_page(viewport={'width': width, 'height': height})
                page.goto(f'http://localhost:{port}/{html_files[key].name}')
                page.wait_for_timeout(2000)  # 等待图表渲染

                output_file = output_path / filename
                page.screenshot(path=str(output_file), full_page=True)
                screenshots[key] = output_file
                page.close()
                print(f"  ✓ 已保存: {output_file}")

        browser.close()

    return screenshots


def insert_images_to_report(summary: dict, base_dir: str, output_dir: str):
    """将图片插入到月报中"""
    report_path = Path(base_dir) / "日记" / str(summary['year']) / f"{summary['month']}月" / f"{summary['year']}年{summary['month']}月统计报表.md"

    if not report_path.exists():
        print(f"警告: 月报文件不存在: {report_path}")
        return False

    content = report_path.read_text(encoding='utf-8')

    # 图片引用路径（相对月报文件）
    img_prefix = f"../../../{output_dir}/"

    # 插入睡眠质量图
    if '## 😴 睡眠质量分析' in content:
        pattern = r'(## 😴 睡眠质量分析\n\n)(?!\!\[)'
        replacement = r'\1![睡眠质量分布]({}01_睡眠质量分布.png)\n\n'.format(img_prefix)
        content = re.sub(pattern, replacement, content)

    # 插入血糖监测图
    if '## 🩸 血糖监测分析' in content:
        pattern = r'(## 🩸 血糖监测分析\n\n)(?!\!\[)'
        replacement = r'\1![血糖监测分析]({}02_血糖监测分析.png)\n\n'.format(img_prefix)
        content = re.sub(pattern, replacement, content)

    # 插入消费趋势图
    if '## 💰 消费趋势分析' in content:
        pattern = r'(## 💰 消费趋势分析\n\n)(?!\!\[)'
        replacement = r'\1![消费趋势分析]({}03_消费趋势分析.png)\n\n'.format(img_prefix)
        content = re.sub(pattern, replacement, content)

    # 插入 OKR 图
    if '## 🎯 OKR目标完成情况' in content:
        pattern = r'(## 🎯 OKR目标完成情况\n\n)(?!\!\[)'
        replacement = r'\1![OKR完成情况]({}04_OKR完成情况.png)\n\n'.format(img_prefix)
        content = re.sub(pattern, replacement, content)

    report_path.write_text(content, encoding='utf-8')
    print(f"\n✓ 已更新月报: {report_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description='生成月度报表可视化图表')
    parser.add_argument('-y', '--year', type=int, default=datetime.now().year, help='年份')
    parser.add_argument('-m', '--month', type=int, default=datetime.now().month, help='月份')
    parser.add_argument('-b', '--base-dir', type=str, default='.', help='日记基础目录')
    parser.add_argument('-o', '--output', type=str, default='minimax-output', help='输出目录')
    parser.add_argument('--charts-only', action='store_true', help='仅生成图表，不插入月报')
    parser.add_argument('-p', '--port', type=int, default=8765, help='HTTP服务器端口')

    args = parser.parse_args()

    print(f"=" * 50)
    print(f"月度报表可视化生成器")
    print(f"=" * 50)
    print(f"年份: {args.year}")
    print(f"月份: {args.month}")
    print(f"基础目录: {args.base_dir}")
    print(f"输出目录: {args.output}")
    print(f"=" * 50)

    # 1. 查找日记文件
    print("\n1. 扫描日记文件...")
    files = find_diary_files(args.base_dir, args.year, args.month)
    if not files:
        print("未找到日记文件，请检查路径和日期")
        return 1
    print(f"  ✓ 找到 {len(files)} 个日记文件")

    # 2. 收集统计数据
    print("\n2. 统计数据...")
    stats = collect_statistics(files)
    print(f"  ✓ 睡眠记录: {sum(stats['sleep'].values())} 天")
    print(f"  ✓ 血糖记录: 空腹 {len(stats['blood_sugar']['fasting'])} 次, 餐后 {len(stats['blood_sugar']['postprandial'])} 次")
    print(f"  ✓ 消费记录: {stats['spending']['count']} 笔, 总计 ¥{stats['spending']['total']:.2f}")
    print(f"  ✓ OKR记录: 待办 {stats['okr']['todo']['total']} 项, KR {stats['okr']['kr']['total']} 项")

    # 3. 计算汇总
    print("\n3. 计算汇总数据...")
    global summary
    summary = calculate_summary(stats, args.year, args.month)
    print(f"  ✓ 完成")

    # 4. 生成 HTML 图表
    print("\n4. 生成 HTML 图表...")
    html_files = generate_html_files(summary, args.output)
    print(f"  ✓ 生成 {len(html_files)} 个图表文件")

    # 5. 启动 HTTP 服务器
    print("\n5. 启动 HTTP 服务器...")
    abs_output_dir = str(Path(args.output).absolute())
    httpd = start_http_server(abs_output_dir, args.port)
    print(f"  ✓ 服务器运行在 http://localhost:{args.port}")
    time.sleep(1)

    # 6. 截图
    print("\n6. 生成 PNG 截图...")
    screenshots = capture_screenshots(html_files, args.output, args.port)

    # 7. 关闭服务器
    httpd.shutdown()
    print("\n7. 关闭 HTTP 服务器")

    # 8. 插入月报（如果不只是生成图表）
    if not args.charts_only:
        print("\n8. 插入图片到月报...")
        insert_images_to_report(summary, args.base_dir, args.output)
    else:
        print("\n8. 跳过插入月报 (--charts-only)")

    print("\n" + "=" * 50)
    print("完成!")
    print("=" * 50)
    print(f"生成的图片:")
    for name, path in screenshots.items():
        print(f"  - {path}")
    print("=" * 50)

    return 0


if __name__ == '__main__':
    sys.exit(main())

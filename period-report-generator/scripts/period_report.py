#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
周期统计报表生成器
根据日记文件生成周/月统计报表，包括血糖变化、消费趋势、目标完成率
使用 ascii-chart-to-svg 技能生成SVG图表
"""

import re
import sys
import io
import argparse
import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# 设置标准输出为 UTF-8 编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def find_ascii_chart_script() -> Path:
    """查找 ascii-chart-to-svg 脚本路径"""
    skill_path = Path("C:/Users/Administrator/.claude/skills/ascii-chart-to-svg/scripts/chart_to_svg.py")
    if skill_path.exists():
        return skill_path

    # 尝试相对路径
    current_dir = Path(__file__).parent.parent.parent
    relative_path = current_dir / "ascii-chart-to-svg" / "scripts" / "chart_to_svg.py"
    if relative_path.exists():
        return relative_path

    return None


def generate_chart_svg(chart_type: str, title: str, data: dict,
                      output_path: Path, script_path: Path = None) -> bool:
    """
    使用 ascii-chart-to-svg 技能生成SVG图表

    Args:
        chart_type: 图表类型 (blood_sugar/consumption/task_completion)
        title: 图表标题
        data: 图表数据
        output_path: 输出路径
        script_path: chart_to_svg 脚本路径

    Returns:
        是否成功生成
    """
    if not script_path:
        print("⚠️  未找到 chart_to_svg 脚本")
        return False

    # 构建ASCII图表文本
    ascii_chart = build_ascii_chart(chart_type, title, data)

    try:
        print(f"📊 正在生成SVG图表: {title}")

        # 使用临时文件传递数据(避免Windows stdin编码问题)
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.txt', delete=False) as f:
            temp_file = f.name
            f.write(ascii_chart)

        try:
            # 调用 chart_to_svg 脚本,从临时文件读取
            with open(temp_file, 'r', encoding='utf-8') as input_file:
                result = subprocess.run(
                    [sys.executable, str(script_path), str(output_path)],
                    stdin=input_file,
                    capture_output=True,
                    text=True,
                    timeout=30  # 30秒超时
                )

            if result.returncode == 0 and output_path.exists():
                print(f"✅ SVG图表已生成: {output_path}")
                return True
            else:
                print(f"⚠️  SVG图表生成失败: {result.stderr}")
                return False
        finally:
            # 删除临时文件
            try:
                import os
                os.unlink(temp_file)
            except:
                pass

    except subprocess.TimeoutExpired:
        print("⚠️  SVG图表生成超时")
        return False
    except Exception as e:
        print(f"⚠️  SVG图表生成错误: {e}")
        return False


def build_ascii_chart(chart_type: str, title: str, data: dict) -> str:
    """
    根据图表数据构建ASCII格式图表文本

    Args:
        chart_type: 图表类型
        title: 图表标题
        data: 图表数据

    Returns:
        ASCII图表文本
    """
    if chart_type == "blood_sugar":
        return build_blood_sugar_ascii(title, data)
    elif chart_type == "consumption":
        return build_consumption_ascii(title, data)
    elif chart_type == "task_completion":
        return build_task_completion_ascii(title, data)
    else:
        return f"{title}:\n无数据"


def build_blood_sugar_ascii(title: str, data: dict) -> str:
    """构建血糖趋势图ASCII文本"""
    labels = data.get('labels', [])
    fasting_data = data.get('fasting', [])
    bedtime_data = data.get('bedtime', [])

    # 找出所有数据的最大值和最小值
    all_values = [v for v in fasting_data if v is not None] + [v for v in bedtime_data if v is not None]
    if not all_values:
        return f"{title}:\n无数据"

    max_val = max(all_values)
    min_val = min(all_values)

    # 向上取整到0.5的倍数
    y_max = int(max_val * 2 + 1) / 2
    y_min = int(min_val * 2) / 2
    y_min = max(0, y_min)

    # 确定Y轴刻度
    y_steps = 7
    y_range = y_max - y_min
    y_increment = y_range / (y_steps - 1) if y_steps > 1 else 1

    # 构建空腹血糖图表
    chart_lines = []
    chart_lines.append(f"{title}:")

    # Y轴刻度和数据
    for i in range(y_steps):
        y_val = y_max - (i * y_increment)
        y_label = f"{y_val:.1f}"

        # 空腹血糖数据点
        line = f"{y_label:5s} ┤"
        for j, val in enumerate(fasting_data):
            if val is not None and abs(val - y_val) < y_increment / 2:
                line += "  █"
            else:
                line += "  "

        chart_lines.append(line)

    # X轴
    chart_lines.append("     ┼" + "─" * (len(labels) * 3))
    chart_lines.append("      " + "  ".join(f"{l:2s}" for l in labels) + " (日期)")

    chart_lines.append("")

    # 构建睡前血糖图表
    chart_lines.append(f"睡前血糖趋势:")

    for i in range(y_steps):
        y_val = y_max - (i * y_increment)
        y_label = f"{y_val:.1f}"

        # 睡前血糖数据点
        line = f"{y_label:5s} ┤"
        for j, val in enumerate(bedtime_data):
            if val is not None and abs(val - y_val) < y_increment / 2:
                line += "  █"
            else:
                line += "  "

        chart_lines.append(line)

    # X轴
    chart_lines.append("     ┼" + "─" * (len(labels) * 3))
    chart_lines.append("      " + "  ".join(f"{l:2s}" for l in labels) + " (日期)")

    return "\n".join(chart_lines)


def build_consumption_ascii(title: str, data: dict) -> str:
    """构建消费趋势图ASCII文本"""
    labels = data.get('labels', [])
    values = data.get('values', [])

    # 过滤掉None值
    valid_values = [v for v in values if v is not None]

    if not valid_values:
        return f"{title}:\n无数据"

    max_val = max(valid_values)
    y_max = int(max_val / 50 + 1) * 50  # 向上取整到50的倍数

    # 确定Y轴刻度
    y_steps = 7
    y_increment = y_max / (y_steps - 1) if y_steps > 1 else 50

    # 构建图表
    chart_lines = []
    chart_lines.append(f"{title}:")

    for i in range(y_steps):
        y_val = y_max - (i * y_increment)
        y_label = f"{int(y_val)}"

        line = f"{y_label:>4s} ┤"
        for j, val in enumerate(values):
            if val is not None and abs(val - y_val) < y_increment / 2:
                line += "  █"
            else:
                line += "  "

        chart_lines.append(line)

    # X轴
    chart_lines.append("    0 ┼" + "─" * (len(labels) * 3))
    chart_lines.append("      " + "  ".join(f"{l:2s}" for l in labels) + " (日期)")

    return "\n".join(chart_lines)


def build_task_completion_ascii(title: str, data: dict) -> str:
    """构建任务完成率图ASCII文本"""
    labels = data.get('labels', [])
    planned_data = data.get('planned', [])
    work_data = data.get('work', [])

    # 找出所有数据的最大值和最小值
    all_values = [v for v in planned_data if v is not None] + [v for v in work_data if v is not None]
    if not all_values:
        return f"{title}:\n无数据"

    max_val = max(all_values)
    y_max = 100  # 百分比

    # 确定Y轴刻度
    y_steps = 6
    y_increment = y_max / (y_steps - 1)

    # 构建今日计划完成率图表
    chart_lines = []
    chart_lines.append(f"{title} - 今日计划:")

    for i in range(y_steps):
        y_val = y_max - (i * y_increment)
        y_label = f"{int(y_val)}"

        line = f"{y_label:>3s}% ┤"
        for j, val in enumerate(planned_data):
            if val is not None and abs(val - y_val) < y_increment / 2:
                line += "  █"
            else:
                line += "  "

        chart_lines.append(line)

    # X轴
    chart_lines.append("   0% ┼" + "─" * (len(labels) * 3))
    chart_lines.append("      " + "  ".join(f"{l:2s}" for l in labels) + " (日期)")

    chart_lines.append("")

    # 构建工作/学习完成率图表
    chart_lines.append(f"{title} - 工作/学习:")

    for i in range(y_steps):
        y_val = y_max - (i * y_increment)
        y_label = f"{int(y_val)}"

        line = f"{y_label:>3s}% ┤"
        for j, val in enumerate(work_data):
            if val is not None and abs(val - y_val) < y_increment / 2:
                line += "  █"
            else:
                line += "  "

        chart_lines.append(line)

    # X轴
    chart_lines.append("   0% ┼" + "─" * (len(labels) * 3))
    chart_lines.append("      " + "  ".join(f"{l:2s}" for l in labels) + " (日期)")

    return "\n".join(chart_lines)


def parse_blood_sugar(content: str) -> dict:
    """
    解析血糖数据

    Returns:
        {'fasting': float, 'post_meal': float, 'bedtime': float}
    """
    result = {'fasting': None, 'post_meal': None, 'bedtime': None}

    # 空腹血糖
    fasting_match = re.search(r'🌅 空腹[^:]+：.*?([\d.]+)(?:\s*$|\s*\n)', content)
    if fasting_match:
        result['fasting'] = float(fasting_match.group(1))

    # 餐后2h
    post_meal_match = re.search(r'🍚 餐后2h[^:]+：.*?([\d.]+)(?:\s*$|\s*\n)', content)
    if post_meal_match:
        result['post_meal'] = float(post_meal_match.group(1))

    # 睡前
    bedtime_match = re.search(r'🌙 睡前[^:]+：.*?([\d.]+)(?:\s*$|\s*\n)', content)
    if bedtime_match:
        result['bedtime'] = float(bedtime_match.group(1))

    return result


def parse_sleep_quality(content: str) -> dict:
    """
    解析睡眠质量数据

    Returns:
        {'quality': str}
    """
    result = {'quality': None}

    sleep_pattern = r'- 睡眠：.*?(?=\n-|\n##|\n###)'
    sleep_match = re.search(sleep_pattern, content, re.DOTALL)

    if not sleep_match:
        return result

    sleep_section = sleep_match.group(0)

    if re.search(r'- \[x\]\s*差', sleep_section):
        result['quality'] = '差'
    elif re.search(r'- \[x\]\s*一般', sleep_section):
        result['quality'] = '一般'
    elif re.search(r'- \[x\]\s*好', sleep_section):
        result['quality'] = '好'

    return result


def parse_consumption(content: str) -> dict:
    """
    解析今日消费统计数据

    Returns:
        {'count': int, 'total': float, 'max_amount': float, 'main_category': str}
    """
    result = {'count': 0, 'total': 0, 'max_amount': 0, 'main_category': ''}

    count_match = re.search(r'消费笔数.*?：\s*(\d+)', content)
    if count_match:
        result['count'] = int(count_match.group(1))

    total_match = re.search(r'总支出.*?：.*?\*\*(.+?)\*\*.*?元', content)
    if total_match:
        try:
            result['total'] = float(total_match.group(1))
        except ValueError:
            result['total'] = 0

    max_match = re.search(r'最大支出.*?：([\d.]+)', content)
    if max_match:
        result['max_amount'] = float(max_match.group(1))

    category_match = re.search(r'主要类别.*?：(.+?)（', content)
    if category_match:
        result['main_category'] = category_match.group(1).strip()

    return result


def parse_task_completion(content: str) -> dict:
    """
    解析任务完成情况

    Returns:
        {'planned': int, 'completed': int, 'work_completed': int, 'work_total': int}
    """
    result = {'planned': 0, 'completed': 0, 'work_completed': 0, 'work_total': 0}

    planned_tasks = re.findall(r'^- \[([ x])\]', content, re.MULTILINE)
    result['planned'] = len(planned_tasks)
    result['completed'] = sum(1 for t in planned_tasks if t == 'x')

    work_section = re.search(r'### 2\. 工作/学习\s*\n(.*?)(?=###|\n##)', content, re.DOTALL)
    if work_section:
        work_tasks = re.findall(r'- \[([ x])\]', work_section.group(1))
        result['work_total'] = len(work_tasks)
        result['work_completed'] = sum(1 for t in work_tasks if t == 'x')

    return result


def find_diary_files(base_dir: Path, year: int, month: int, week: int = None) -> list:
    """
    查找指定时间范围的日记文件

    Args:
        base_dir: 日记基础目录
        year: 年份
        month: 月份
        week: 周数（可选）

    Returns:
        日记文件路径列表
    """
    diary_files = []

    chinese_months = ['一月', '二月', '三月', '四月', '五月', '六月',
                      '七月', '八月', '九月', '十月', '十一月', '十二月']

    month_cn = chinese_months[month - 1] if 1 <= month <= 12 else f"{month}月"

    if week:
        week_dir_names = [
            f"第{week}周",
            f"第{week:02d}周",
            f"{week}周",
            f"{week:02d}周",
            "第一周" if week == 1 else f"第{week}周",
            "第二周" if week == 2 else f"第{week}周",
            "第三周" if week == 3 else f"第{week}周",
            "第四周" if week == 4 else f"第{week}周",
            "第五周" if week == 5 else f"第{week}周",
        ]

        week_dir_names = list(set(week_dir_names))

        for week_name in week_dir_names:
            week_dir = base_dir / f"日记/{year}年/{month_cn}/{week_name}"
            if week_dir.exists() and week_dir.is_dir():
                for md_file in week_dir.glob("*.md"):
                    if '统计报表' not in md_file.name and '周报' not in md_file.name:
                        diary_files.append(md_file)
                if diary_files:
                    break

        if not diary_files:
            for week_name in week_dir_names:
                week_dir = base_dir / f"日记/{year}年/{month}月/{week_name}"
                if week_dir.exists() and week_dir.is_dir():
                    for md_file in week_dir.glob("*.md"):
                        if '统计报表' not in md_file.name and '周报' not in md_file.name:
                            diary_files.append(md_file)
                    if diary_files:
                        break
    else:
        month_dirs = [
            base_dir / f"日记/{year}年/{month_cn}",
            base_dir / f"日记/{year}年/{month}月",
        ]

        for month_dir in month_dirs:
            if month_dir.exists() and month_dir.is_dir():
                for week_dir in month_dir.iterdir():
                    if week_dir.is_dir():
                        for md_file in week_dir.glob("*.md"):
                            if '统计报表' not in md_file.name and '周报' not in md_file.name:
                                diary_files.append(md_file)
                if diary_files:
                    break

    return sorted(diary_files)


def analyze_blood_sugar_trend(data: list) -> dict:
    """
    分析血糖趋势

    Args:
        data: 血糖数据列表

    Returns:
        统计分析结果
    """
    fasting_values = [d['fasting'] for d in data if d['fasting']]
    post_meal_values = [d['post_meal'] for d in data if d['post_meal']]
    bedtime_values = [d['bedtime'] for d in data if d['bedtime']]

    fasting_count = len(fasting_values)
    post_meal_count = len(post_meal_values)
    bedtime_count = len(bedtime_values)

    fasting_in_range = sum(1 for v in fasting_values if 3.9 <= v <= 6.1)
    post_meal_in_range = sum(1 for v in post_meal_values if 4.4 <= v <= 7.8)
    bedtime_in_range = sum(1 for v in bedtime_values if 4.4 <= v <= 7.8)

    result = {
        'fasting_avg': sum(fasting_values) / fasting_count if fasting_count > 0 else 0,
        'fasting_min': min(fasting_values) if fasting_count > 0 else 0,
        'fasting_max': max(fasting_values) if fasting_count > 0 else 0,
        'fasting_count': fasting_count,
        'fasting_in_range': fasting_in_range,
        'fasting_rate': (fasting_in_range / fasting_count * 100) if fasting_count > 0 else 0,
        'post_meal_avg': sum(post_meal_values) / post_meal_count if post_meal_count > 0 else 0,
        'post_meal_min': min(post_meal_values) if post_meal_count > 0 else 0,
        'post_meal_max': max(post_meal_values) if post_meal_count > 0 else 0,
        'post_meal_count': post_meal_count,
        'post_meal_in_range': post_meal_in_range,
        'post_meal_rate': (post_meal_in_range / post_meal_count * 100) if post_meal_count > 0 else 0,
        'bedtime_avg': sum(bedtime_values) / bedtime_count if bedtime_count > 0 else 0,
        'bedtime_min': min(bedtime_values) if bedtime_count > 0 else 0,
        'bedtime_max': max(bedtime_values) if bedtime_count > 0 else 0,
        'bedtime_count': bedtime_count,
        'bedtime_in_range': bedtime_in_range,
        'bedtime_rate': (bedtime_in_range / bedtime_count * 100) if bedtime_count > 0 else 0,
    }

    return result


def analyze_consumption_trend(data: list) -> dict:
    """
    分析消费趋势

    Args:
        data: 消费数据列表

    Returns:
        统计分析结果
    """
    has_consumption_data = any(d['total'] > 0 for d in data) if data else False

    if not has_consumption_data:
        return {
            'has_data': False,
            'total': 0,
            'avg_daily': 0,
            'total_transactions': 0,
            'days_with_expense': 0,
            'main_category': '无',
            'max_daily': 0,
        }

    total_consumption = sum(d['total'] for d in data)
    total_transactions = sum(d['count'] for d in data)
    avg_daily = total_consumption / len(data) if data else 0

    categories = defaultdict(int)
    for d in data:
        if d['main_category']:
            categories[d['main_category']] += 1

    main_category = max(categories, key=categories.get) if categories else '无'

    result = {
        'has_data': True,
        'total': total_consumption,
        'avg_daily': avg_daily,
        'total_transactions': total_transactions,
        'days_with_expense': sum(1 for d in data if d['count'] > 0),
        'main_category': main_category,
        'max_daily': max(d['total'] for d in data) if data else 0,
    }

    return result


def analyze_goal_completion(data: list) -> dict:
    """
    分析目标完成率

    Args:
        data: 任务数据列表

    Returns:
        统计分析结果
    """
    total_planned = sum(d['planned'] for d in data)
    total_completed = sum(d['completed'] for d in data)
    total_work = sum(d['work_total'] for d in data)
    total_work_completed = sum(d['work_completed'] for d in data)

    result = {
        'planned_rate': total_completed / total_planned if total_planned > 0 else 0,
        'work_rate': total_work_completed / total_work if total_work > 0 else 0,
        'total_planned': total_planned,
        'total_completed': total_completed,
        'total_work': total_work,
        'total_work_completed': total_work_completed,
    }

    return result


def analyze_sleep_quality(data: list) -> dict:
    """
    分析睡眠质量趋势

    Args:
        data: 睡眠质量数据列表

    Returns:
        统计分析结果
    """
    quality_counts = {'差': 0, '一般': 0, '好': 0}

    for d in data:
        quality = d.get('quality')
        if quality in quality_counts:
            quality_counts[quality] += 1

    total_days = sum(quality_counts.values())

    quality_values = []
    for d in data:
        quality = d.get('quality')
        if quality == '差':
            quality_values.append(1)
        elif quality == '一般':
            quality_values.append(2)
        elif quality == '好':
            quality_values.append(3)

    avg_quality = sum(quality_values) / len(quality_values) if quality_values else 0

    most_common = max(quality_counts, key=quality_counts.get) if total_days > 0 else '无'

    good_sleep_rate = (quality_counts['好'] + quality_counts['一般']) / total_days if total_days > 0 else 0

    result = {
        'total_days': total_days,
        'bad_days': quality_counts['差'],
        'normal_days': quality_counts['一般'],
        'good_days': quality_counts['好'],
        'avg_quality': avg_quality,
        'most_common': most_common,
        'good_sleep_rate': good_sleep_rate,
        'bad_rate': quality_counts['差'] / total_days if total_days > 0 else 0,
    }

    return result


def generate_charts_svg(blood_sugar_data: list, consumption_data: list,
                       task_data: list, year: int, month: int, week: int,
                       report_type: str, output_dir: Path,
                       script_path: Path = None) -> dict:
    """
    使用 ascii-chart-to-svg 生成SVG图表并保存

    Returns:
        图表文件路径字典
    """
    chart_paths = {}

    # 提取日期标签
    date_labels = [d['date'].split('-')[-1] if '-' in d['date'] else d['date']
                   for d in blood_sugar_data]

    # 1. 血糖趋势图
    blood_data = {
        'labels': date_labels,
        'fasting': [d['fasting'] for d in blood_sugar_data],
        'bedtime': [d['bedtime'] for d in blood_sugar_data]
    }

    blood_chart_path = output_dir / f'blood_sugar_trend_{year}_{month:02d}_w{week if week else 0}.svg'
    if generate_chart_svg('blood_sugar', '血糖监测趋势', blood_data, blood_chart_path, script_path):
        chart_paths['blood_sugar_trend'] = str(blood_chart_path)

    # 2. 消费柱状图
    consumption_values = [d['total'] for d in consumption_data]
    if any(v > 0 for v in consumption_values):
        consumption_data_dict = {
            'labels': date_labels,
            'values': consumption_values
        }

        consumption_chart_path = output_dir / f'consumption_trend_{year}_{month:02d}_w{week if week else 0}.svg'
        if generate_chart_svg('consumption', '每日消费趋势', consumption_data_dict, consumption_chart_path, script_path):
            chart_paths['consumption_trend'] = str(consumption_chart_path)

    # 3. 任务完成率图
    planned_rates = [(d['completed'] / d['planned'] * 100) if d['planned'] > 0 else 0
                     for d in task_data]
    work_rates = [(d['work_completed'] / d['work_total'] * 100) if d['work_total'] > 0 else 0
                  for d in task_data]

    task_data_dict = {
        'labels': date_labels,
        'planned': planned_rates,
        'work': work_rates
    }

    task_chart_path = output_dir / f'task_completion_rate_{year}_{month:02d}_w{week if week else 0}.svg'
    if generate_chart_svg('task_completion', '任务完成率趋势', task_data_dict, task_chart_path, script_path):
        chart_paths['task_completion_rate'] = str(task_chart_path)

    return chart_paths


def generate_weekly_report(year: int, month: int, week: int, data: list,
                           output_path: Path, use_ai_charts: bool = False):
    """
    生成周报表
    """
    blood_sugar_data = [{'date': d['date'], **parse_blood_sugar(d['content'])} for d in data]
    consumption_data = [parse_consumption(d['content']) for d in data]
    task_data = [parse_task_completion(d['content']) for d in data]
    sleep_data = [parse_sleep_quality(d['content']) for d in data]

    blood_analysis = analyze_blood_sugar_trend(blood_sugar_data)
    consumption_analysis = analyze_consumption_trend(consumption_data)
    goal_analysis = analyze_goal_completion(task_data)
    sleep_analysis = analyze_sleep_quality(sleep_data)

    # 生成图表
    chart_paths = {}
    charts_section = ''

    if use_ai_charts:
        # 查找 ascii-chart-to-svg 脚本
        script_path = find_ascii_chart_script()
        output_dir = output_path.parent

        if script_path:
            print(f"📊 使用 ascii-chart-to-svg 生成SVG图表...")
            chart_paths = generate_charts_svg(
                blood_sugar_data, consumption_data, task_data,
                year, month, week, 'week', output_dir, script_path
            )

        # 构建图表引用
        if chart_paths:
            charts_section = '\n## 📈 趋势图表\n\n'
            if 'blood_sugar_trend' in chart_paths:
                charts_section += f'### 血糖监测趋势\n\n![血糖趋势]({Path(chart_paths["blood_sugar_trend"]).name})\n\n'
            if 'consumption_trend' in chart_paths:
                charts_section += f'### 每日消费趋势\n\n![消费趋势]({Path(chart_paths["consumption_trend"]).name})\n\n'
            if 'task_completion_rate' in chart_paths:
                charts_section += f'### 任务完成率趋势\n\n![任务完成率]({Path(chart_paths["task_completion_rate"]).name})\n\n'

    # 开始构建报表
    report = f"""---
title: 第{week}周统计报表
type: 统计报表
created: {datetime.now().strftime('%Y-%m-%d')}
period: {year}年{month}月第{week}周
---

# 第{week}周统计报表 ({year}年{month}月)

## 📊 概览

- **统计周期**: {year}年{month}月 第{week}周
- **记录天数**: {len(data)} 天
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 😴 睡眠质量分析

- **睡眠质量分布**: 差 {sleep_analysis['bad_days']} 天 | 一般 {sleep_analysis['normal_days']} 天 | 好 {sleep_analysis['good_days']} 天
- **平均睡眠质量**: {sleep_analysis['avg_quality']:.1f}/3.0
- **最常见质量**: {sleep_analysis['most_common']}
- **良好睡眠率**: {sleep_analysis['good_sleep_rate']*100:.1f}%

## 🩸 血糖监测分析

### 空腹血糖 (正常范围: 3.9-6.1 mmol/L)
- **平均值**: {blood_analysis['fasting_avg']:.2f} mmol/L
- **最小值**: {blood_analysis['fasting_min']:.2f} mmol/L
- **最大值**: {blood_analysis['fasting_max']:.2f} mmol/L
- **达标率**: {blood_analysis['fasting_in_range']}/{blood_analysis['fasting_count']} ({blood_analysis['fasting_rate']:.1f}%)

### 餐后2h血糖 (正常范围: 4.4-7.8 mmol/L)
- **平均值**: {blood_analysis['post_meal_avg']:.2f} mmol/L
- **最小值**: {blood_analysis['post_meal_min']:.2f} mmol/L
- **最大值**: {blood_analysis['post_meal_max']:.2f} mmol/L
- **达标率**: {blood_analysis['post_meal_in_range']}/{blood_analysis['post_meal_count']} ({blood_analysis['post_meal_rate']:.1f}%)

### 睡前血糖 (正常范围: 4.4-7.8 mmol/L)
- **平均值**: {blood_analysis['bedtime_avg']:.2f} mmol/L
- **最小值**: {blood_analysis['bedtime_min']:.2f} mmol/L
- **最大值**: {blood_analysis['bedtime_max']:.2f} mmol/L
- **达标率**: {blood_analysis['bedtime_in_range']}/{blood_analysis['bedtime_count']} ({blood_analysis['bedtime_rate']:.1f}%)

"""

    if consumption_analysis['has_data']:
        report += f"""## 💰 消费趋势分析

- **总支出**: 💰 {consumption_analysis['total']:.2f} 元
- **日均消费**: {consumption_analysis['avg_daily']:.2f} 元
- **消费笔数**: {consumption_analysis['total_transactions']} 笔
- **有消费天数**: {consumption_analysis['days_with_expense']} 天
- **单日最高**: {consumption_analysis['max_daily']:.2f} 元
- **主要消费类别**: {consumption_analysis['main_category']}

"""

    report += f"""## 🎯 目标完成情况

### 今日计划完成率
- **计划总数**: {goal_analysis['total_planned']} 项
- **已完成**: {goal_analysis['total_completed']} 项
- **完成率**: {goal_analysis['planned_rate']*100:.1f}%

### 工作/学习任务完成率
- **任务总数**: {goal_analysis['total_work']} 项
- **已完成**: {goal_analysis['total_work_completed']} 项
- **完成率**: {goal_analysis['work_rate']*100:.1f}%

{charts_section}
## 💡 建议与总结

### 健康建议
"""

    if sleep_analysis['bad_rate'] >= 0.5:
        report += f"- 睡眠质量需要改善，本周{sleep_analysis['bad_days']}天睡眠较差，建议调整作息时间\n"
    elif sleep_analysis['bad_rate'] > 0.2:
        report += f"- 本周有{sleep_analysis['bad_days']}天睡眠较差，注意休息和压力管理\n"
    elif sleep_analysis['good_days'] == sleep_analysis['total_days'] and sleep_analysis['total_days'] > 0:
        report += "- 本周每天睡眠质量都很好，继续保持！\n"
    elif sleep_analysis['avg_quality'] >= 2:
        report += f"- 平均睡眠质量{sleep_analysis['avg_quality']:.1f}分（满分3分），整体表现良好\n"

    if blood_analysis['fasting_avg'] > 6.1:
        report += "- 空腹血糖偏高，建议控制晚餐和夜间饮食\n"
    elif blood_analysis['fasting_avg'] > 0:
        report += f"- 空腹血糖平均值 {blood_analysis['fasting_avg']:.2f} mmol/L，"
        if blood_analysis['fasting_avg'] <= 6.1:
            report += "在正常范围内，继续保持\n"

    if blood_analysis['post_meal_avg'] > 7.8:
        report += "- 餐后血糖偏高，建议减少碳水化合物摄入\n"
    elif blood_analysis['post_meal_avg'] > 0:
        report += f"- 餐后血糖平均值 {blood_analysis['post_meal_avg']:.2f} mmol/L，"
        if blood_analysis['post_meal_avg'] <= 7.8:
            report += "在正常范围内\n"

    if blood_analysis['bedtime_avg'] > 7.8:
        report += "- 睡前血糖偏高，建议控制晚间饮食\n"
    elif blood_analysis['bedtime_avg'] > 0:
        report += f"- 睡前血糖平均值 {blood_analysis['bedtime_avg']:.2f} mmol/L，"
        if blood_analysis['bedtime_avg'] <= 7.8:
            report += "在正常范围内\n"

    if consumption_analysis['has_data']:
        report += "\n### 消费建议\n"
        if consumption_analysis['avg_daily'] > 100:
            report += f"- 日均消费 {consumption_analysis['avg_daily']:.2f} 元，建议适当控制支出\n"
        report += f"- 主要消费类别为 {consumption_analysis['main_category']}，可关注该类别的支出优化\n"

    report += "\n### 目标达成建议\n"
    if goal_analysis['planned_rate'] < 0.8:
        report += f"- 今日计划完成率 {goal_analysis['planned_rate']*100:.1f}%，建议合理规划每日任务\n"
    if goal_analysis['work_rate'] < 0.8:
        report += f"- 工作学习完成率 {goal_analysis['work_rate']*100:.1f}%，建议调整工作节奏\n"

    if goal_analysis['planned_rate'] >= 0.8 and goal_analysis['work_rate'] >= 0.8:
        report += "- 各项任务完成情况良好，继续保持！\n"

    report += "\n---\n*本报表由周期统计报表生成器自动生成*"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ 周报表已生成: {output_path}")


def generate_monthly_report(year: int, month: int, data: list,
                            output_path: Path, use_ai_charts: bool = False):
    """
    生成月报表
    """
    blood_sugar_data = [{'date': d['date'], **parse_blood_sugar(d['content'])} for d in data]
    consumption_data = [parse_consumption(d['content']) for d in data]
    task_data = [parse_task_completion(d['content']) for d in data]
    sleep_data = [parse_sleep_quality(d['content']) for d in data]

    blood_analysis = analyze_blood_sugar_trend(blood_sugar_data)
    consumption_analysis = analyze_consumption_trend(consumption_data)
    goal_analysis = analyze_goal_completion(task_data)
    sleep_analysis = analyze_sleep_quality(sleep_data)

    # 生成图表
    chart_paths = {}
    charts_section = ''

    if use_ai_charts:
        script_path = find_ascii_chart_script()
        output_dir = output_path.parent

        if script_path:
            print(f"📊 使用 ascii-chart-to-svg 生成SVG图表...")
            chart_paths = generate_charts_svg(
                blood_sugar_data, consumption_data, task_data,
                year, month, None, 'month', output_dir, script_path
            )

        if chart_paths:
            charts_section = '\n## 📈 趋势图表\n\n'
            if 'blood_sugar_trend' in chart_paths:
                charts_section += f'### 血糖监测趋势\n\n![血糖趋势]({Path(chart_paths["blood_sugar_trend"]).name})\n\n'
            if 'consumption_trend' in chart_paths:
                charts_section += f'### 每日消费趋势\n\n![消费趋势]({Path(chart_paths["consumption_trend"]).name})\n\n'
            if 'task_completion_rate' in chart_paths:
                charts_section += f'### 任务完成率趋势\n\n![任务完成率]({Path(chart_paths["task_completion_rate"]).name})\n\n'

    report = f"""---
title: {year}年{month}月统计报表
type: 统计报表
created: {datetime.now().strftime('%Y-%m-%d')}
period: {year}年{month}月
---

# {year}年{month}月统计报表

## 📊 概览

- **统计周期**: {year}年{month}月
- **记录天数**: {len(data)} 天
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 😴 睡眠质量分析

- **睡眠质量分布**: 差 {sleep_analysis['bad_days']} 天 | 一般 {sleep_analysis['normal_days']} 天 | 好 {sleep_analysis['good_days']} 天
- **平均睡眠质量**: {sleep_analysis['avg_quality']:.1f}/3.0
- **最常见质量**: {sleep_analysis['most_common']}
- **良好睡眠率**: {sleep_analysis['good_sleep_rate']*100:.1f}%

## 🩸 血糖监测分析

### 空腹血糖 (正常范围: 3.9-6.1 mmol/L)
- **平均值**: {blood_analysis['fasting_avg']:.2f} mmol/L
- **最小值**: {blood_analysis['fasting_min']:.2f} mmol/L
- **最大值**: {blood_analysis['fasting_max']:.2f} mmol/L
- **达标率**: {blood_analysis['fasting_in_range']}/{blood_analysis['fasting_count']} ({blood_analysis['fasting_rate']:.1f}%)

### 餐后2h血糖 (正常范围: 4.4-7.8 mmol/L)
- **平均值**: {blood_analysis['post_meal_avg']:.2f} mmol/L
- **最小值**: {blood_analysis['post_meal_min']:.2f} mmol/L
- **最大值**: {blood_analysis['post_meal_max']:.2f} mmol/L
- **达标率**: {blood_analysis['post_meal_in_range']}/{blood_analysis['post_meal_count']} ({blood_analysis['post_meal_rate']:.1f}%)

### 睡前血糖 (正常范围: 4.4-7.8 mmol/L)
- **平均值**: {blood_analysis['bedtime_avg']:.2f} mmol/L
- **最小值**: {blood_analysis['bedtime_min']:.2f} mmol/L
- **最大值**: {blood_analysis['bedtime_max']:.2f} mmol/L
- **达标率**: {blood_analysis['bedtime_in_range']}/{blood_analysis['bedtime_count']} ({blood_analysis['bedtime_rate']:.1f}%)

"""

    if consumption_analysis['has_data']:
        report += f"""## 💰 消费趋势分析

- **总支出**: 💰 {consumption_analysis['total']:.2f} 元
- **日均消费**: {consumption_analysis['avg_daily']:.2f} 元
- **消费笔数**: {consumption_analysis['total_transactions']} 笔
- **有消费天数**: {consumption_analysis['days_with_expense']} 天
- **单日最高**: {consumption_analysis['max_daily']:.2f} 元
- **主要消费类别**: {consumption_analysis['main_category']}

"""

    report += f"""## 🎯 目标完成情况

### 今日计划完成率
- **计划总数**: {goal_analysis['total_planned']} 项
- **已完成**: {goal_analysis['total_completed']} 项
- **完成率**: {goal_analysis['planned_rate']*100:.1f}%

### 工作/学习任务完成率
- **任务总数**: {goal_analysis['total_work']} 项
- **已完成**: {goal_analysis['total_work_completed']} 项
- **完成率**: {goal_analysis['work_rate']*100:.1f}%

{charts_section}
## 💡 建议与总结

### 健康建议
"""

    if sleep_analysis['bad_rate'] >= 0.5:
        report += f"- 睡眠质量需要改善，本月{sleep_analysis['bad_days']}天睡眠较差，建议调整作息时间\n"
    elif sleep_analysis['bad_rate'] > 0.2:
        report += f"- 本月有{sleep_analysis['bad_days']}天睡眠较差，注意休息和压力管理\n"
    elif sleep_analysis['good_days'] == sleep_analysis['total_days'] and sleep_analysis['total_days'] > 0:
        report += "- 本月每天睡眠质量都很好，继续保持！\n"
    elif sleep_analysis['avg_quality'] >= 2:
        report += f"- 平均睡眠质量{sleep_analysis['avg_quality']:.1f}分（满分3分），整体表现良好\n"

    if blood_analysis['fasting_avg'] > 6.1:
        report += "- 空腹血糖偏高，建议控制晚餐和夜间饮食\n"
    elif blood_analysis['fasting_avg'] > 0:
        report += f"- 空腹血糖平均值 {blood_analysis['fasting_avg']:.2f} mmol/L，"
        if blood_analysis['fasting_avg'] <= 6.1:
            report += "在正常范围内，继续保持\n"

    if blood_analysis['post_meal_avg'] > 7.8:
        report += "- 餐后血糖偏高，建议减少碳水化合物摄入\n"
    elif blood_analysis['post_meal_avg'] > 0:
        report += f"- 餐后血糖平均值 {blood_analysis['post_meal_avg']:.2f} mmol/L，"
        if blood_analysis['post_meal_avg'] <= 7.8:
            report += "在正常范围内\n"

    if blood_analysis['bedtime_avg'] > 7.8:
        report += "- 睡前血糖偏高，建议控制晚间饮食\n"
    elif blood_analysis['bedtime_avg'] > 0:
        report += f"- 睡前血糖平均值 {blood_analysis['bedtime_avg']:.2f} mmol/L，"
        if blood_analysis['bedtime_avg'] <= 7.8:
            report += "在正常范围内\n"

    if consumption_analysis['has_data']:
        report += "\n### 消费建议\n"
        if consumption_analysis['avg_daily'] > 100:
            report += f"- 日均消费 {consumption_analysis['avg_daily']:.2f} 元，建议适当控制支出\n"
        report += f"- 主要消费类别为 {consumption_analysis['main_category']}，可关注该类别的支出优化\n"
        report += f"- 本月总支出 {consumption_analysis['total']:.2f} 元\n"

    report += "\n### 目标达成建议\n"
    if goal_analysis['planned_rate'] < 0.8:
        report += f"- 今日计划完成率 {goal_analysis['planned_rate']*100:.1f}%，建议合理规划每日任务\n"
    if goal_analysis['work_rate'] < 0.8:
        report += f"- 工作学习完成率 {goal_analysis['work_rate']*100:.1f}%，建议调整工作节奏\n"

    if goal_analysis['planned_rate'] >= 0.8 and goal_analysis['work_rate'] >= 0.8:
        report += "- 各项任务完成情况良好，继续保持！\n"

    report += "\n---\n*本报表由周期统计报表生成器自动生成*"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ 月报表已生成: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='周期统计报表生成器')
    parser.add_argument('--type', '-t', choices=['week', 'month'], required=True,
                        help='报表类型: week-周报, month-月报')
    parser.add_argument('--year', '-y', type=int, default=datetime.now().year,
                        help='年份 (默认为当前年)')
    parser.add_argument('--month', '-m', type=int, default=datetime.now().month,
                        help='月份 (默认为当前月)')
    parser.add_argument('--week', '-w', type=int,
                        help='周数 (周报时必需)')
    parser.add_argument('--base-dir', '-b', default='.', help='日记基础目录')
    parser.add_argument('--output', '-o', help='输出文件路径 (可选)')
    parser.add_argument('--ai-charts', action='store_true',
                        help='使用 ascii-chart-to-svg 技能生成SVG图表')

    args = parser.parse_args()

    if args.type == 'week' and not args.week:
        print("❌ 生成周报时必须指定 --week 参数")
        sys.exit(1)

    base_dir = Path(args.base_dir)

    diary_files = find_diary_files(base_dir, args.year, args.month, args.week)

    if not diary_files:
        print(f"❌ 未找到 {args.year}年{args.month}月", end='')
        if args.week:
            print(f"第{args.week}周 的日记文件")
        else:
            print(" 的日记文件")
        sys.exit(1)

    print(f"📖 找到 {len(diary_files)} 个日记文件")

    data = []
    for file_path in diary_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            date = file_path.stem
            data.append({'date': date, 'content': content})
        except Exception as e:
            print(f"⚠️  读取文件失败 {file_path}: {e}")

    if not data:
        print("❌ 没有可用的数据")
        sys.exit(1)

    if args.output:
        output_path = Path(args.output)
    else:
        if args.type == 'week':
            week_dir = diary_files[0].parent
            output_path = week_dir / f"第{args.week}周统计报表.md"
        else:
            month_dir = diary_files[0].parent.parent
            output_path = month_dir / f"{args.year}年{args.month}月统计报表.md"

    if args.type == 'week':
        generate_weekly_report(args.year, args.month, args.week, data, output_path, args.ai_charts)
    else:
        generate_monthly_report(args.year, args.month, data, output_path, args.ai_charts)


if __name__ == '__main__':
    main()

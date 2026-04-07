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
    elif chart_type == "okr_completion":
        return build_okr_completion_ascii(title, data)
    elif chart_type == "okr_priority":
        return build_okr_priority_ascii(title, data)
    else:
        return f"{title}:\n无数据"


def build_blood_sugar_ascii(title: str, data: dict) -> str:
    """构建血糖趋势图ASCII文本（数据表格格式）"""
    labels = data.get('labels', [])
    fasting_data = data.get('fasting', [])
    bedtime_data = data.get('bedtime', [])

    # 找出所有数据的最大值和最小值
    all_values = [v for v in fasting_data if v is not None] + [v for v in bedtime_data if v is not None]
    if not all_values:
        return f"{title}:\n无数据"

    chart_lines = [f"{title}:", ""]

    # 表头
    header = "日期    │"
    for label in labels:
        day = label.split('-')[-1] if '-' in label else label
        header += f" {day:>5s} │"
    chart_lines.append(header)
    chart_lines.append("────────┼" + "───────┼" * len(labels))

    # 空腹血糖数据行
    fasting_line = "空腹    │"
    for val in fasting_data:
        if val is not None:
            fasting_line += f" {val:>5.1f} │"
        else:
            fasting_line += "   -   │"
    chart_lines.append(fasting_line)

    # 睡前血糖数据行
    bedtime_line = "睡前    │"
    for val in bedtime_data:
        if val is not None:
            bedtime_line += f" {val:>5.1f} │"
        else:
            bedtime_line += "   -   │"
    chart_lines.append(bedtime_line)

    return "\n".join(chart_lines)


def build_consumption_ascii(title: str, data: dict) -> str:
    """构建消费趋势图ASCII文本（数据表格格式）"""
    labels = data.get('labels', [])
    values = data.get('values', [])

    # 过滤掉None值
    valid_values = [v for v in values if v is not None]

    if not valid_values:
        return f"{title}:\n无数据"

    chart_lines = [f"{title}:", ""]

    # 表头 - 日期行
    header = "日期    │"
    for label in labels:
        day = label.split('-')[-1] if '-' in label else label
        header += f" {day:>6s} │"
    chart_lines.append(header)
    chart_lines.append("────────┼" + "────────┼" * len(labels))

    # 消费金额数据行
    amount_line = "金额(元)│"
    for val in values:
        if val is not None and val > 0:
            amount_line += f" {val:>6.1f} │"
        else:
            amount_line += "      - │"
    chart_lines.append(amount_line)

    return "\n".join(chart_lines)


def build_task_completion_ascii(title: str, data: dict) -> str:
    """构建OKR完成率图ASCII文本"""
    labels = data.get('labels', [])
    todo_rates = data.get('todo_rates', [])
    temp_rates = data.get('temp_rates', [])
    kr_rates = data.get('kr_rates', [])

    if not labels:
        return f"{title}:\n无数据"

    chart_lines = [f"{title}", "=" * 40]

    # 构建今日待办完成率图表
    chart_lines.append("")
    chart_lines.append("📋 今日待办完成率")
    for i, label in enumerate(labels):
        rate = todo_rates[i] if i < len(todo_rates) else 0
        bar_len = int(rate * 25)
        bar = "█" * bar_len + "░" * (25 - bar_len)
        chart_lines.append(f"{label:6} │{bar} {rate*100:5.1f}%")

    chart_lines.append("")
    chart_lines.append("⚡ 临时任务完成率")
    for i, label in enumerate(labels):
        rate = temp_rates[i] if i < len(temp_rates) else 0
        bar_len = int(rate * 25)
        bar = "█" * bar_len + "░" * (25 - bar_len)
        chart_lines.append(f"{label:6} │{bar} {rate*100:5.1f}%")

    chart_lines.append("")
    chart_lines.append("🎯 KR关键结果完成率")
    for i, label in enumerate(labels):
        rate = kr_rates[i] if i < len(kr_rates) else 0
        bar_len = int(rate * 25)
        bar = "█" * bar_len + "░" * (25 - bar_len)
        chart_lines.append(f"{label:6} │{bar} {rate*100:5.1f}%")

    chart_lines.append("=" * 40)
    return "\n".join(chart_lines)


def build_okr_completion_ascii(title: str, data: dict) -> str:
    """构建OKR完成率趋势ASCII文本（数据表格格式）"""
    labels = data.get('labels', [])
    todo_rates = data.get('todo_rates', [])
    temp_rates = data.get('temp_rates', [])
    kr_rates = data.get('kr_rates', [])

    if not labels:
        return f"{title}:\n无数据"

    chart_lines = [f"{title}:", ""]

    # 表头 - 日期行
    header = "类型      │"
    for label in labels:
        day = label.split('-')[-1] if '-' in label else label
        header += f" {day:>6s} │"
    chart_lines.append(header)
    chart_lines.append("──────────┼" + "────────┼" * len(labels))

    # 今日待办完成率行
    todo_line = "📋待办(%) │"
    for rate in todo_rates:
        if rate is not None:
            todo_line += f" {rate*100:>6.1f} │"
        else:
            todo_line += "      - │"
    chart_lines.append(todo_line)

    # 临时任务完成率行
    temp_line = "⚡临时(%) │"
    for rate in temp_rates:
        if rate is not None:
            temp_line += f" {rate*100:>6.1f} │"
        else:
            temp_line += "      - │"
    chart_lines.append(temp_line)

    # KR完成率行
    kr_line = "🎯KR(%)   │"
    for rate in kr_rates:
        if rate is not None:
            kr_line += f" {rate*100:>6.1f} │"
        else:
            kr_line += "      - │"
    chart_lines.append(kr_line)

    return "\n".join(chart_lines)


def build_okr_priority_ascii(title: str, data: dict) -> str:
    """构建KR按优先级完成率图ASCII文本（数据表格格式）"""
    kr_by_priority = data.get('kr_by_priority', {})

    if not kr_by_priority or all(p['total'] == 0 for p in kr_by_priority.values()):
        return f"{title}:\n无KR数据"

    chart_lines = [f"{title}:", ""]
    chart_lines.append("优先级 │ 总数 │ 已完成 │ 完成率 │")
    chart_lines.append("───────┼──────┼────────┼────────┤")

    # 按P0、P1、P2顺序显示
    priority_names = {'P0': '🔴 P0', 'P1': '🟡 P1', 'P2': '🟢 P2'}

    for p in ['P0', 'P1', 'P2']:
        if p in kr_by_priority:
            stats = kr_by_priority[p]
            total = stats['total']
            completed = stats['completed']
            rate = (completed / total * 100) if total > 0 else 0
            chart_lines.append(f"{priority_names[p]}  │ {total:>4d} │ {completed:>6d} │ {rate:>5.1f}% │")

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

    total_match = re.search(r'总支出.*?：.*?[💰\*]*\s*([\d.]+)\s*\*?\*?.*?元', content)
    if total_match:
        try:
            result['total'] = float(total_match.group(1))
        except ValueError:
            result['total'] = 0

    max_match = re.search(r'最大支出.*?：([\d.]+)', content)
    if max_match:
        result['max_amount'] = float(max_match.group(1))

    category_match = re.search(r'主要类别.*?：(.+?)(?=\（|\n|$)', content)
    if category_match:
        result['main_category'] = category_match.group(1).strip()

    return result


def parse_okr_data(content: str) -> dict:
    """
    解析日OKR管理数据

    Args:
        content: 日记文件内容

    Returns:
        解析后的OKR数据字典，包含Objective、待办事项、临时任务、KR等统计信息
    """
    result = {
        'objective_set': False,
        'objective_content': '',
        'todo_total': 0,
        'todo_completed': 0,
        'temp_total': 0,
        'temp_completed': 0,
        'kr_total': 0,
        'kr_completed': 0,
        'kr_in_progress': 0,
        'kr_cancelled': 0,
        'kr_by_priority': {
            'P0': {'total': 0, 'completed': 0},
            'P1': {'total': 0, 'completed': 0},
            'P2': {'total': 0, 'completed': 0}
        },
        'kr_by_month_okr': {},
        'total_tasks': 0,
        'total_completed': 0
    }

    # 提取日OKR管理部分 - 匹配从 "### 1. 日OKR管理" 到下一个 "### " 或 "## " 之间的内容
    okr_section_match = re.search(
        r'###\s*1\.\s*日OKR管理\s*\n(.*?)(?=\n###\s|\n##\s|$)',
        content,
        re.DOTALL
    )

    if not okr_section_match:
        return result

    okr_section = okr_section_match.group(1)

    # 提取Objective - 匹配 "#### 🎯 Objective：内容"
    objective_match = re.search(
        r'####\s*🎯\s*Objective\s*[：:]?\s*(.*?)(?=\n####|\n###|\n##|\*\*|$)',
        okr_section,
        re.DOTALL
    )
    if objective_match:
        objective_content = objective_match.group(1).strip()
        # 更严格的空内容检查 - 去除可能的冒号前缀
        objective_content = objective_content.lstrip(':').strip()
        if objective_content and objective_content not in ('::', ':', ''):
            result['objective_set'] = True
            result['objective_content'] = objective_content

    # 提取今日待办事项 - 匹配 "##### 今日待办事项" 部分
    todo_section_match = re.search(
        r'#####\s*今日待办事项\s*\n(.*?)(?=#####|\n####|\n###|\n##|$)',
        okr_section,
        re.DOTALL
    )
    if todo_section_match:
        todo_section = todo_section_match.group(1)
        # 统计复选框 - [ ] 和 - [x]
        todo_tasks = re.findall(r'^- \[([ x])\]', todo_section, re.MULTILINE)
        result['todo_total'] = len(todo_tasks)
        result['todo_completed'] = sum(1 for t in todo_tasks if t == 'x')

    # 提取临时任务 - 匹配 "#### 临时任务" 部分
    temp_section_match = re.search(
        r'####\s*临时任务.*?\n(.*?)(?=####|\n###|\n##|$)',
        okr_section,
        re.DOTALL
    )
    if temp_section_match:
        temp_section = temp_section_match.group(1)
        # 统计复选框
        temp_tasks = re.findall(r'^- \[([ x])\]', temp_section, re.MULTILINE)
        result['temp_total'] = len(temp_tasks)
        result['temp_completed'] = sum(1 for t in temp_tasks if t == 'x')

    # 提取KR表格 - 匹配表格格式
    # 表格格式：| 序号 | 关键任务 | 关联月OKR | 优先级 | 状态 |
    kr_table_match = re.search(
        r'\|\s*序号\s*\|.*?\|\s*状态\s*\|\s*\n\|[-:\s|]+\|\s*\n((?:\|[^\n]*\|\s*\n?)+)',
        okr_section,
        re.DOTALL
    )

    if kr_table_match:
        kr_table_content = kr_table_match.group(1)
        # 解析每一行
        kr_rows = re.findall(
            r'\|\s*([\w\d]+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(P\d+)\s*\|\s*(已完成|进行中|已取消)\s*\|',
            kr_table_content
        )

        for row in kr_rows:
            kr_id, task, month_okr, priority, status = row
            result['kr_total'] += 1

            # 统计状态
            if status == '已完成':
                result['kr_completed'] += 1
            elif status == '进行中':
                result['kr_in_progress'] += 1
            elif status == '已取消':
                result['kr_cancelled'] += 1

            # 按优先级统计
            if priority in result['kr_by_priority']:
                result['kr_by_priority'][priority]['total'] += 1
                if status == '已完成':
                    result['kr_by_priority'][priority]['completed'] += 1

            # 按关联月OKR统计 - 提取链接文本如 [[2026-03月OKR|月OKR]] 或纯文本
            month_okr_clean = month_okr.strip()
            # 处理Wiki链接格式 [[链接|显示文本]] 或 [[链接]]
            # 使用贪婪匹配来正确解析 [[link|display]] 格式
            wiki_link_match = re.search(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', month_okr_clean)
            if wiki_link_match:
                # 使用显示文本（如果有）或链接本身
                month_okr_key = wiki_link_match.group(2).strip() if wiki_link_match.group(2) else wiki_link_match.group(1).strip()
            else:
                month_okr_key = month_okr_clean

            if month_okr_key:
                if month_okr_key not in result['kr_by_month_okr']:
                    result['kr_by_month_okr'][month_okr_key] = {
                        'total': 0,
                        'completed': 0,
                        'in_progress': 0,
                        'cancelled': 0
                    }
                result['kr_by_month_okr'][month_okr_key]['total'] += 1
                if status == '已完成':
                    result['kr_by_month_okr'][month_okr_key]['completed'] += 1
                elif status == '进行中':
                    result['kr_by_month_okr'][month_okr_key]['in_progress'] += 1
                elif status == '已取消':
                    result['kr_by_month_okr'][month_okr_key]['cancelled'] += 1

    # 计算总任务数和总完成数
    result['total_tasks'] = result['todo_total'] + result['temp_total'] + result['kr_total']
    result['total_completed'] = result['todo_completed'] + result['temp_completed'] + result['kr_completed']

    return result


def parse_task_completion(content: str) -> dict:
    """
    解析任务完成情况（适配新版日OKR管理格式）

    Returns:
        {
            'planned': int,           # 今日待办总数
            'completed': int,         # 今日待办完成数
            'work_total': int,        # 总任务数（临时+KR）
            'work_completed': int,    # 总完成数（临时+KR完成）
            'okr_data': dict          # 完整的OKR数据（来自parse_okr_data）
        }
    """
    # 调用新的OKR解析函数
    okr_data = parse_okr_data(content)

    # 构建兼容旧版的数据结构
    result = {
        'planned': okr_data['todo_total'],
        'completed': okr_data['todo_completed'],
        'work_total': okr_data['temp_total'] + okr_data['kr_total'],
        'work_completed': okr_data['temp_completed'] + okr_data['kr_completed'],
        'okr_data': okr_data  # 保留完整OKR数据供后续使用
    }

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
    分析OKR目标完成情况

    Args:
        data: 任务数据列表（包含okr_data字段）

    Returns:
        统计分析结果
    """
    # 汇总所有OKR数据
    total_todo = sum(d['okr_data']['todo_total'] for d in data if 'okr_data' in d)
    total_todo_completed = sum(d['okr_data']['todo_completed'] for d in data if 'okr_data' in d)

    total_temp = sum(d['okr_data']['temp_total'] for d in data if 'okr_data' in d)
    total_temp_completed = sum(d['okr_data']['temp_completed'] for d in data if 'okr_data' in d)

    total_kr = sum(d['okr_data']['kr_total'] for d in data if 'okr_data' in d)
    total_kr_completed = sum(d['okr_data']['kr_completed'] for d in data if 'okr_data' in d)
    total_kr_in_progress = sum(d['okr_data']['kr_in_progress'] for d in data if 'okr_data' in d)
    total_kr_cancelled = sum(d['okr_data']['kr_cancelled'] for d in data if 'okr_data' in d)

    # 汇总优先级统计
    kr_by_priority = {'P0': {'total': 0, 'completed': 0},
                     'P1': {'total': 0, 'completed': 0},
                     'P2': {'total': 0, 'completed': 0}}

    for d in data:
        if 'okr_data' not in d:
            continue
        for p in ['P0', 'P1', 'P2']:
            kr_by_priority[p]['total'] += d['okr_data']['kr_by_priority'][p]['total']
            kr_by_priority[p]['completed'] += d['okr_data']['kr_by_priority'][p]['completed']

    # 汇总月OKR统计
    kr_by_month_okr = {}
    for d in data:
        if 'okr_data' not in d:
            continue
        for okr_name, stats in d['okr_data']['kr_by_month_okr'].items():
            if okr_name not in kr_by_month_okr:
                kr_by_month_okr[okr_name] = {'total': 0, 'completed': 0, 'in_progress': 0, 'cancelled': 0}
            kr_by_month_okr[okr_name]['total'] += stats['total']
            kr_by_month_okr[okr_name]['completed'] += stats['completed']
            kr_by_month_okr[okr_name]['in_progress'] += stats['in_progress']
            kr_by_month_okr[okr_name]['cancelled'] += stats['cancelled']

    # 计算完成率
    total_tasks = total_todo + total_temp + total_kr
    total_completed = total_todo_completed + total_temp_completed + total_kr_completed

    result = {
        # 兼容旧字段
        'planned_rate': total_todo_completed / total_todo if total_todo > 0 else 0,
        'work_rate': (total_temp_completed + total_kr_completed) / (total_temp + total_kr) if (total_temp + total_kr) > 0 else 0,
        'total_planned': total_todo,
        'total_completed': total_todo_completed,
        'total_work': total_temp + total_kr,
        'total_work_completed': total_temp_completed + total_kr_completed,

        # 新的OKR统计字段
        'todo_total': total_todo,
        'todo_completed': total_todo_completed,
        'todo_rate': total_todo_completed / total_todo if total_todo > 0 else 0,

        'temp_total': total_temp,
        'temp_completed': total_temp_completed,
        'temp_rate': total_temp_completed / total_temp if total_temp > 0 else 0,

        'kr_total': total_kr,
        'kr_completed': total_kr_completed,
        'kr_in_progress': total_kr_in_progress,
        'kr_cancelled': total_kr_cancelled,
        'kr_rate': total_kr_completed / total_kr if total_kr > 0 else 0,

        'kr_by_priority': kr_by_priority,
        'kr_by_month_okr': kr_by_month_okr,

        'total_tasks': total_tasks,
        'overall_rate': total_completed / total_tasks if total_tasks > 0 else 0
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


def generate_daily_blood_sugar_details(blood_sugar_data: list) -> str:
    """生成逐日血糖数据明细表格"""
    # 过滤出有数据的日期
    valid_data = []
    for d in blood_sugar_data:
        date = d.get('date', '')
        fasting = d.get('fasting')
        if fasting is not None:
            valid_data.append((date, fasting))

    if not valid_data:
        return ""

    # 构建表格
    lines = ["\n**每日空腹血糖记录：**\n"]

    # 表头
    header = "| 日期 |"
    for date, _ in valid_data:
        day = date.split('-')[-1] if '-' in date else date
        header += f" {day} |"
    lines.append(header)

    # 分隔符
    separator = "|------|"
    for _ in valid_data:
        separator += "-------|"
    lines.append(separator)

    # 数据行
    data_row = "| 血糖 |"
    for _, fasting in valid_data:
        data_row += f" {fasting} |"
    lines.append(data_row)

    lines.append("\n> 单位：mmol/L")

    return "\n".join(lines)


def generate_blood_sugar_conclusion(analysis: dict, report_type: str = "本周") -> str:
    """生成血糖趋势分析结论"""
    conclusions = []

    # 空腹血糖分析
    if analysis['fasting_count'] > 0:
        if analysis['fasting_avg'] > 6.1:
            high_days = analysis['fasting_count'] - analysis['fasting_in_range']
            conclusions.append(f"- ⚠️ **空腹血糖**: {report_type}{high_days}天偏高, 平均值{analysis['fasting_avg']:.2f}超正常范围, 建议控制晚餐和夜宵")
        elif analysis['fasting_rate'] >= 80:
            conclusions.append(f"- ✅ **空腹血糖**: 平均值{analysis['fasting_avg']:.2f}在正常范围, 达标率{analysis['fasting_rate']:.1f}%, 表现良好")
        else:
            conclusions.append(f"- ✅ **空腹血糖**: 平均值{analysis['fasting_avg']:.2f}在正常范围, 达标率{analysis['fasting_rate']:.1f}%")

    # 餐后血糖分析
    if analysis['post_meal_count'] > 0:
        if analysis['post_meal_avg'] > 7.8:
            conclusions.append(f"- ⚠️ **餐后血糖**: 平均值{analysis['post_meal_avg']:.2f}偏高, 建议减少碳水摄入")
        else:
            conclusions.append(f"- ✅ **餐后血糖**: 平均值{analysis['post_meal_avg']:.2f}在正常范围")
    else:
        conclusions.append(f"- ℹ️ **餐后2h血糖**: {report_type}未记录, 建议开始监测餐后血糖")

    # 睡前血糖分析
    if analysis['bedtime_count'] > 0:
        if analysis['bedtime_avg'] > 7.8:
            conclusions.append(f"- ❌ **睡前血糖**: 全部{analysis['bedtime_count']}天均偏高, 平均值{analysis['bedtime_avg']:.2f}远超正常范围, 需要重点关注!")
            conclusions.append(f"  - 建议晚餐后适当散步运动")
            conclusions.append(f"  - 检查晚餐饮食结构, 减少高碳水食物")
            conclusions.append(f"  - 咨询医生是否需要调整用药方案")
        else:
            conclusions.append(f"- ✅ **睡前血糖**: 平均值{analysis['bedtime_avg']:.2f}在正常范围")

    return "\n".join(conclusions) if conclusions else ""


def analyze_consumption_categories(consumption_data: list, total_transactions: int) -> dict:
    """分析消费类别分布"""
    categories = defaultdict(lambda: {'count': 0, 'amount': 0})

    for d in consumption_data:
        category = d.get('main_category', '')
        count = d.get('count', 0)
        total = d.get('total', 0)
        if category and count > 0:
            categories[category]['count'] += count
            categories[category]['amount'] += total

    result = {}
    for cat, data in categories.items():
        result[cat] = {
            'count': data['count'],
            'amount': data['amount'],
            'percentage': (data['count'] / total_transactions * 100) if total_transactions > 0 else 0
        }

    return result


def generate_daily_consumption_details(consumption_data: list, blood_sugar_data: list) -> tuple:
    """生成逐日消费明细"""
    lines = ["\n### 逐日消费明细\n"]
    lines.append("| 日期 | 星期 | 消费笔数 | 总支出 | 主要消费 |")
    lines.append("|:---:|:---:|:---:|:---:|:---|")

    weekdays = ['一', '二', '三', '四', '五', '六', '日']

    # 创建日期映射
    date_map = {}
    for d in blood_sugar_data:
        date_map[d['date']] = d

    for i, d in enumerate(consumption_data):
        date = date_map.get(d['date'], {}).get('date', f'第{i+1}天')
        date_str = date[-5:] if len(date) > 5 else date  # 取 MM-DD 部分

        # 计算星期
        try:
            from datetime import datetime
            dt = datetime.strptime(date, '%Y-%m-%d')
            weekday = weekdays[dt.weekday()]
        except:
            weekday = '-'

        count = d.get('count', 0)
        total = d.get('total', 0)
        category = d.get('main_category', '无')

        lines.append(f"| {date_str} | {weekday} | {count} 笔 | {total:.2f}元 | {category} |")

    return "\n".join(lines), len(consumption_data)


def generate_consumption_analysis(consumption_data: list, categories: dict) -> str:
    """生成消费详细分析"""
    lines = ["\n### 消费分析\n"]

    # 找出大额支出
    large_expenses = []
    for d in consumption_data:
        total = d.get('total', 0)
        if total > 100:  # 单日超过100元视为大额支出
            date = d.get('date', '')
            large_expenses.append((date, total))

    if large_expenses:
        lines.append("**大额支出**:")
        for date, amount in sorted(large_expenses, key=lambda x: x[1], reverse=True)[:5]:
            lines.append(f"  - {date}: {amount:.2f}元")
        lines.append("")

    # 餐饮消费分析
    dining_data = categories.get('餐饮', {})
    if dining_data.get('count', 0) > 0:
        dining_amount = dining_data.get('amount', 0)
        lines.append(f"**餐饮消费**: 本周餐饮{dining_data['count']}笔, 共约{dining_amount:.0f}元, 日均餐饮{dining_amount/7:.0f}元")
        lines.append("")

    # 建议部分
    lines.append("**建议**:")
    avg_daily = sum(d.get('total', 0) for d in consumption_data) / len(consumption_data) if consumption_data else 0

    if avg_daily > 150:
        lines.append(f"  - 日均消费{avg_daily:.2f}元偏高, 建议适当控制非必要支出")
    else:
        lines.append(f"  - 日均消费{avg_daily:.2f}元合理, 继续保持")

    main_category = max(categories.items(), key=lambda x: x[1]['count'])[0] if categories else '无'
    lines.append(f"  - 主要消费类别为{main_category}, 可关注该类别的支出优化")

    return "\n".join(lines)


def extract_task_achievements(task_data: list, blood_sugar_data: list) -> dict:
    """提取主要成就和未完成任务"""
    completed = []
    uncompleted = []

    # 创建日期映射
    date_map = {}
    for d in blood_sugar_data:
        date_map[d['date']] = d

    for i, d in enumerate(task_data):
        work_completed = d.get('work_completed', 0)
        work_total = d.get('work_total', 0)
        date = date_map.get(d.get('date', ''), {}).get('date', f'第{i+1}天')

        if work_total > 0 and work_completed == work_total:
            completed.append(date)
        elif work_completed < work_total:
            uncompleted.append(date)

    return {'completed_days': completed, 'uncompleted_days': uncompleted}


def generate_line_chart_svg(title: str, labels: list, datasets: list, y_max: float = None) -> str:
    """
    生成SVG折线图

    Args:
        title: 图表标题
        labels: X轴标签列表
        datasets: 数据集列表，每个数据集为 {'name': str, 'values': list, 'color': str}
        y_max: Y轴最大值，None则自动计算

    Returns:
        SVG字符串
    """
    width = 800
    height = 400
    margin_left = 60
    margin_right = 40
    margin_top = 50
    margin_bottom = 60

    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom

    # 计算Y轴范围
    all_values = [v for ds in datasets for v in ds['values'] if v is not None]
    if not all_values:
        return f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg"><text x="{width/2}" y="{height/2}" text-anchor="middle">无数据</text></svg>'

    if y_max is None:
        y_max = max(all_values) * 1.1 if max(all_values) > 0 else 100
    y_min = 0

    def x_pos(i):
        return margin_left + (i / max(1, len(labels) - 1)) * chart_width

    def y_pos(val):
        if val is None:
            return None
        return margin_top + chart_height - (val / y_max) * chart_height

    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <style>
    .title {{ font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; fill: #333; }}
    .axis-label {{ font-family: Arial, sans-serif; font-size: 12px; fill: #666; }}
    .legend-label {{ font-family: Arial, sans-serif; font-size: 12px; fill: #333; }}
    .grid-line {{ stroke: #e0e0e0; stroke-width: 1; stroke-dasharray: 4,4; }}
    .axis-line {{ stroke: #999; stroke-width: 1; }}
    .data-line {{ fill: none; stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; }}
    .data-point {{ r: 5; stroke: white; stroke-width: 2; }}
    .data-point:hover {{ r: 7; }}
  </style>
  <rect width="{width}" height="{height}" fill="white"/>
  <text x="{width/2}" y="30" text-anchor="middle" class="title">{title}</text>
'''

    # Y轴刻度和网格线
    y_steps = 5
    for i in range(y_steps + 1):
        y_val = y_max * i / y_steps
        y = margin_top + chart_height - (i / y_steps) * chart_height
        svg += f'  <line x1="{margin_left}" y1="{y}" x2="{width - margin_right}" y2="{y}" class="grid-line"/>\n'
        svg += f'  <text x="{margin_left - 10}" y="{y + 4}" text-anchor="end" class="axis-label">{y_val:.1f}</text>\n'

    # X轴线
    svg += f'  <line x1="{margin_left}" y1="{margin_top + chart_height}" x2="{width - margin_right}" y2="{margin_top + chart_height}" class="axis-line"/>\n'

    # X轴标签
    for i, label in enumerate(labels):
        x = x_pos(i)
        svg += f'  <text x="{x}" y="{height - margin_bottom + 20}" text-anchor="middle" class="axis-label">{label}</text>\n'

    # 绘制每个数据集
    legend_x = width - margin_right - 150
    for ds_idx, ds in enumerate(datasets):
        color = ds.get('color', '#4CAF50')
        values = ds['values']

        # 构建路径
        path_d = ""
        for i, val in enumerate(values):
            y = y_pos(val)
            if y is not None:
                x = x_pos(i)
                if path_d == "":
                    path_d = f"M {x} {y}"
                else:
                    path_d += f" L {x} {y}"

        if path_d:
            svg += f'  <path d="{path_d}" class="data-line" stroke="{color}"/>\n'

        # 绘制数据点
        for i, val in enumerate(values):
            y = y_pos(val)
            if y is not None:
                x = x_pos(i)
                svg += f'  <circle cx="{x}" cy="{y}" class="data-point" fill="{color}"><title>{labels[i]}: {val:.1f}</title></circle>\n'

        # 图例
        svg += f'  <line x1="{legend_x}" y1="{margin_top + ds_idx * 20}" x2="{legend_x + 20}" y2="{margin_top + ds_idx * 20}" stroke="{color}" stroke-width="3"/>\n'
        svg += f'  <text x="{legend_x + 30}" y="{margin_top + ds_idx * 20 + 4}" class="legend-label">{ds["name"]}</text>\n'

    svg += '</svg>'
    return svg


def generate_charts_svg_inline(blood_sugar_data: list, consumption_data: list,
                                task_data: list, goal_analysis: dict) -> str:
    """
    生成SVG折线图并内嵌到Markdown中

    Returns:
        Markdown图表文本（包含SVG）
    """
    import base64
    charts_section = "\n## 📈 趋势图表\n"

    # 提取日期标签
    date_labels = [d['date'].split('-')[-1] if '-' in d['date'] else d['date']
                   for d in blood_sugar_data]

    # 1. 血糖趋势图
    fasting_values = [d.get('fasting') for d in blood_sugar_data]
    bedtime_values = [d.get('bedtime') for d in blood_sugar_data]

    if any(v is not None for v in fasting_values + bedtime_values):
        charts_section += "\n### 血糖监测趋势\n\n"
        datasets = []
        if any(v is not None for v in fasting_values):
            datasets.append({'name': '空腹', 'values': fasting_values, 'color': '#FF6B6B'})
        if any(v is not None for v in bedtime_values):
            datasets.append({'name': '睡前', 'values': bedtime_values, 'color': '#4ECDC4'})

        svg = generate_line_chart_svg("血糖监测趋势", date_labels, datasets, y_max=12)
        # 将SVG转为base64嵌入
        svg_encoded = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
        charts_section += f'<img src="data:image/svg+xml;base64,{svg_encoded}" alt="血糖趋势"/>\n'

    # 2. 消费趋势图
    consumption_values = [d['total'] for d in consumption_data]
    if any(v > 0 for v in consumption_values):
        charts_section += "\n### 每日消费趋势\n\n"
        datasets = [{'name': '消费金额', 'values': consumption_values, 'color': '#4CAF50'}]
        max_val = max(v for v in consumption_values if v > 0)

        svg = generate_line_chart_svg("每日消费趋势", date_labels, datasets, y_max=max_val * 1.2)
        svg_encoded = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
        charts_section += f'<img src="data:image/svg+xml;base64,{svg_encoded}" alt="消费趋势"/>\n'

    # 3. OKR完成率趋势图
    okr_labels = [d['date'].split('-')[-1] if '-' in d['date'] else d['date']
                  for d in task_data]
    todo_rates = []
    temp_rates = []
    kr_rates = []

    for d in task_data:
        okr = d.get('okr_data', {})

        todo_total = okr.get('todo_total', 0)
        todo_completed = okr.get('todo_completed', 0)
        todo_rates.append(todo_completed / todo_total * 100 if todo_total > 0 else 0)

        temp_total = okr.get('temp_total', 0)
        temp_completed = okr.get('temp_completed', 0)
        temp_rates.append(temp_completed / temp_total * 100 if temp_total > 0 else 0)

        kr_total = okr.get('kr_total', 0)
        kr_completed = okr.get('kr_completed', 0)
        kr_rates.append(kr_completed / kr_total * 100 if kr_total > 0 else 0)

    charts_section += "\n### OKR任务完成率趋势\n\n"
    datasets = [
        {'name': '📋待办', 'values': todo_rates, 'color': '#2196F3'},
        {'name': '⚡临时', 'values': temp_rates, 'color': '#FF9800'},
        {'name': '🎯KR', 'values': kr_rates, 'color': '#9C27B0'}
    ]
    svg = generate_line_chart_svg("OKR任务完成率趋势", okr_labels, datasets, y_max=100)
    svg_encoded = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    charts_section += f'<img src="data:image/svg+xml;base64,{svg_encoded}" alt="OKR完成率"/>\n'

    # 4. KR优先级完成率 - 使用柱状图
    kr_by_priority = goal_analysis.get('kr_by_priority', {})
    if kr_by_priority and any(p['total'] > 0 for p in kr_by_priority.values()):
        charts_section += "\n### KR按优先级完成率\n\n"
        charts_section += "| 优先级 | 总数 | 已完成 | 完成率 |\n"
        charts_section += "|:---|:---:|:---:|:---:|\n"

        for p in ['P0', 'P1', 'P2']:
            if p in kr_by_priority:
                stats = kr_by_priority[p]
                total = stats['total']
                completed = stats['completed']
                rate = f"{completed/total*100:.1f}%" if total > 0 else "0.0%"
                emoji = {'P0': '🔴', 'P1': '🟡', 'P2': '🟢'}.get(p, '')
                charts_section += f"| {emoji} {p} | {total} | {completed} | {rate} |\n"

    return charts_section


def generate_weekly_report(year: int, month: int, week: int, data: list,
                           output_path: Path, use_ai_charts: bool = False):
    """
    生成周报表
    """
    # 为每个数据项添加 date 字段
    enriched_data = []
    for d in data:
        d_copy = d.copy()
        # 确保 blood_sugar_data 也有 date 字段
        enriched_data.append(d_copy)

    blood_sugar_data = [{'date': d['date'], **parse_blood_sugar(d['content'])} for d in enriched_data]
    consumption_data = []
    for d in enriched_data:
        parsed = parse_consumption(d['content'])
        parsed['date'] = d['date']
        consumption_data.append(parsed)
    task_data = []
    for d in enriched_data:
        parsed = parse_task_completion(d['content'])
        parsed['date'] = d['date']
        task_data.append(parsed)
    sleep_data = [parse_sleep_quality(d['content']) for d in enriched_data]

    blood_analysis = analyze_blood_sugar_trend(blood_sugar_data)
    consumption_analysis = analyze_consumption_trend(consumption_data)
    goal_analysis = analyze_goal_completion(task_data)
    sleep_analysis = analyze_sleep_quality(sleep_data)

    # 生成详细分析内容
    daily_blood_sugar = generate_daily_blood_sugar_details(blood_sugar_data)
    blood_sugar_conclusion = generate_blood_sugar_conclusion(blood_analysis, "本周")
    consumption_categories = analyze_consumption_categories(consumption_data, consumption_analysis['total_transactions'])
    daily_consumption, consumption_days = generate_daily_consumption_details(consumption_data, blood_sugar_data)
    consumption_detailed_analysis = generate_consumption_analysis(consumption_data, consumption_categories)
    task_achievements = extract_task_achievements(task_data, blood_sugar_data)

    # 生成图表
    charts_section = ''

    if use_ai_charts:
        print(f"📊 生成SVG折线图...")
        charts_section = generate_charts_svg_inline(
            blood_sugar_data, consumption_data, task_data, goal_analysis
        )

    # 构建消费类别分布表格
    category_dist_section = ""
    if consumption_categories:
        category_dist_section = "\n### 消费类别分布\n\n"
        category_dist_section += "| 类别 | 笔数 | 占比 |\n"
        category_dist_section += "|:---:|:---:|:---:|\n"
        for cat, info in sorted(consumption_categories.items(), key=lambda x: x[1]['count'], reverse=True):
            category_dist_section += f"| {cat} | {info['count']} 笔 | {info['percentage']:.1f}% |\n"

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

---

## 🩸 血糖监测分析

### 空腹血糖 (正常范围: 3.9-6.1 mmol/L)

| 指标 | 数值 |
|:---|:---:|
| 📊 平均值 | **{blood_analysis['fasting_avg']:.2f}** mmol/L |
| ⬇️ 最小值 | {blood_analysis['fasting_min']:.2f} mmol/L |
| ⬆️ 最大值 | {blood_analysis['fasting_max']:.2f} mmol/L |
| ✅ 达标率 | **{blood_analysis['fasting_rate']:.1f}%** ({blood_analysis['fasting_in_range']}/{blood_analysis['fasting_count']}天)
{daily_blood_sugar}

### 餐后2h血糖 (正常范围: 4.4-7.8 mmol/L)

| 指标 | 数值 |
|:---|:---:|
| 📊 平均值 | **{blood_analysis['post_meal_avg']:.2f}** mmol/L |
| ⬇️ 最小值 | {blood_analysis['post_meal_min']:.2f} mmol/L |
| ⬆️ 最大值 | {blood_analysis['post_meal_max']:.2f} mmol/L |
| ✅ 达标率 | **{blood_analysis['post_meal_rate']:.1f}%** ({blood_analysis['post_meal_in_range']}/{blood_analysis['post_meal_count']}天)

### 睡前血糖 (正常范围: 4.4-7.8 mmol/L)

| 指标 | 数值 |
|:---|:---:|
| 📊 平均值 | **{blood_analysis['bedtime_avg']:.2f}** mmol/L |
| ⬇️ 最小值 | {blood_analysis['bedtime_min']:.2f} mmol/L |
| ⬆️ 最大值 | {blood_analysis['bedtime_max']:.2f} mmol/L |
| ✅ 达标率 | **{blood_analysis['bedtime_rate']:.1f}%** ({blood_analysis['bedtime_in_range']}/{blood_analysis['bedtime_count']}天)

### 血糖趋势分析结论

{blood_sugar_conclusion}

---

## 💰 消费趋势分析

### 消费总览

| 指标 | 数值 |
|:---|:---:|
| 💵 总支出 | **{consumption_analysis['total']:.2f}** 元 |
| 📊 日均消费 | **{consumption_analysis['avg_daily']:.2f}** 元 |
| 📝 消费笔数 | {consumption_analysis['total_transactions']} 笔 |
| 📅 有消费天数 | {consumption_analysis['days_with_expense']} 天 |
| 🔝 单日最高 | {consumption_analysis['max_daily']:.2f} 元 |
{daily_consumption}
{category_dist_section}
{consumption_detailed_analysis}

---

## 😴 睡眠质量分析

- **睡眠质量分布**: 差 {sleep_analysis['bad_days']} 天 | 一般 {sleep_analysis['normal_days']} 天 | 好 {sleep_analysis['good_days']} 天
- **平均睡眠质量**: {sleep_analysis['avg_quality']:.1f}/3.0
- **最常见质量**: {sleep_analysis['most_common']}
- **良好睡眠率**: {sleep_analysis['good_sleep_rate']*100:.1f}%

---

## 🎯 OKR目标完成情况

### 任务完成概览

| 任务类型 | 总数 | 已完成 | 进行中 | 已取消 | 完成率 |
|:---|:---:|:---:|:---:|:---:|:---:|
| 📋 今日待办 | {goal_analysis['todo_total']} 项 | {goal_analysis['todo_completed']} 项 | - | - | **{goal_analysis['todo_rate']*100:.1f}%** |
| ⚡ 临时任务 | {goal_analysis['temp_total']} 项 | {goal_analysis['temp_completed']} 项 | - | - | **{goal_analysis['temp_rate']*100:.1f}%** |
| 🎯 关键结果(KR) | {goal_analysis['kr_total']} 项 | {goal_analysis['kr_completed']} 项 | {goal_analysis['kr_in_progress']} 项 | {goal_analysis['kr_cancelled']} 项 | **{goal_analysis['kr_rate']*100:.1f}%** |
| **总计** | {goal_analysis['total_tasks']} 项 | {goal_analysis['total_completed']} 项 | {goal_analysis['kr_in_progress']} 项 | {goal_analysis['kr_cancelled']} 项 | **{goal_analysis['overall_rate']*100:.1f}%** |

### KR按优先级统计

| 优先级 | 总数 | 已完成 | 完成率 |
|:---|:---:|:---:|:---:|
| 🔴 P0(最高) | {goal_analysis['kr_by_priority']['P0']['total']} 项 | {goal_analysis['kr_by_priority']['P0']['completed']} 项 | **{goal_analysis['kr_by_priority']['P0']['completed']/goal_analysis['kr_by_priority']['P0']['total']*100 if goal_analysis['kr_by_priority']['P0']['total'] > 0 else 0:.1f}%** |
| 🟡 P1(高) | {goal_analysis['kr_by_priority']['P1']['total']} 项 | {goal_analysis['kr_by_priority']['P1']['completed']} 项 | **{goal_analysis['kr_by_priority']['P1']['completed']/goal_analysis['kr_by_priority']['P1']['total']*100 if goal_analysis['kr_by_priority']['P1']['total'] > 0 else 0:.1f}%** |
| 🟢 P2(中) | {goal_analysis['kr_by_priority']['P2']['total']} 项 | {goal_analysis['kr_by_priority']['P2']['completed']} 项 | **{goal_analysis['kr_by_priority']['P2']['completed']/goal_analysis['kr_by_priority']['P2']['total']*100 if goal_analysis['kr_by_priority']['P2']['total'] > 0 else 0:.1f}%** |
"""

    # 添加按关联月OKR分组统计
    if goal_analysis['kr_by_month_okr']:
        report += "\n### KR按关联月OKR分组统计\n\n"
        for okr_name, stats in goal_analysis['kr_by_month_okr'].items():
            rate = stats['completed'] / stats['total'] * 100 if stats['total'] > 0 else 0
            display_name = okr_name.replace('[[', '').replace(']]', '').replace('|月OKR', '').replace('|季度', '')
            report += f"#### 📌 {display_name}\n\n"
            report += "| 指标 | 数值 |\n"
            report += "|:---|:---: |\n"
            report += f"| KR总数 | {stats['total']} 项 |\n"
            report += f"| 已完成 | {stats['completed']} 项 |\n"
            report += f"| 进行中 | {stats['in_progress']} 项 |\n"
            report += f"| 已取消 | {stats['cancelled']} 项 |\n"
            report += f"| 完成率 | **{rate:.1f}%** |\n\n"

    report += f"\n{charts_section}\n"
    report += """---

## 📝 总结与建议

### 本周总结

**健康方面**:
"""

    # 添加睡眠质量总结
    if sleep_analysis['bad_rate'] >= 0.5:
        report += f"- ⚠️ 睡眠质量较差，本周{sleep_analysis['bad_days']}天睡眠差，需要改善\n"
    elif sleep_analysis['bad_rate'] > 0:
        report += f"- ⚠️ 本周有{sleep_analysis['bad_days']}天睡眠较差，需要关注\n"
    elif sleep_analysis['good_days'] == sleep_analysis['total_days'] and sleep_analysis['total_days'] > 0:
        report += "- ✅ 本周每天睡眠质量都很好，继续保持！\n"

    # 添加血糖总结
    if blood_analysis['fasting_avg'] > 0:
        if blood_analysis['fasting_avg'] <= 6.1 and blood_analysis['fasting_rate'] >= 80:
            report += f"- ✅ 空腹血糖整体控制良好，平均值{blood_analysis['fasting_avg']:.2f}在正常范围\n"
        elif blood_analysis['fasting_avg'] > 6.1:
            report += f"- ⚠️ 空腹血糖平均值{blood_analysis['fasting_avg']:.2f}偏高，需要注意\n"

    if blood_analysis['bedtime_count'] > 0 and blood_analysis['bedtime_avg'] > 7.8:
        report += f"- ❌ 睡前血糖持续偏高（平均值{blood_analysis['bedtime_avg']:.2f}），需要重点关注\n"
    elif blood_analysis['bedtime_count'] > 0:
        report += f"- ✅ 睡前血糖平均值{blood_analysis['bedtime_avg']:.2f}在正常范围\n"

    report += "\n**财务方面**:\n"
    if consumption_analysis['has_data']:
        report += f"- 本周总支出{consumption_analysis['total']:.2f}元，日均{consumption_analysis['avg_daily']:.2f}元\n"
        if consumption_analysis['avg_daily'] <= 150:
            report += "- 消费水平合理，继续保持\n"

    report += "\n**OKR方面**:\n"

    # 今日待办总结
    if goal_analysis['todo_rate'] >= 0.8:
        report += f"- ✅ 今日待办完成率 {goal_analysis['todo_rate']*100:.1f}%，日常任务规划良好\n"
    else:
        report += f"- ⚠️ 今日待办完成率 {goal_analysis['todo_rate']*100:.1f}%，建议合理规划每日任务\n"

    # KR关键结果总结
    if goal_analysis['kr_rate'] >= 0.8:
        report += f"- ✅ 关键结果(KR)完成率 {goal_analysis['kr_rate']*100:.1f}%，核心目标推进顺利\n"
    elif goal_analysis['kr_rate'] >= 0.5:
        report += f"- ⚠️ 关键结果(KR)完成率 {goal_analysis['kr_rate']*100:.1f}%，需要加快核心目标进度\n"
    else:
        report += f"- ❌ 关键结果(KR)完成率 {goal_analysis['kr_rate']*100:.1f}%，核心目标推进缓慢，需要重点关注\n"

    # P0优先级KR总结
    p0_total = goal_analysis['kr_by_priority']['P0']['total']
    p0_completed = goal_analysis['kr_by_priority']['P0']['completed']
    if p0_total > 0:
        p0_rate = p0_completed / p0_total
        if p0_rate < 1.0:
            report += f"- 🔴 有 {p0_total - p0_completed} 个P0级KR未完成，建议优先处理高优先级任务\n"
        else:
            report += f"- ✅ 所有P0级KR已完成\n"

    report += "\n### 下周建议\n\n"
    report += "1. **健康改善**:\n"

    if sleep_analysis['bad_rate'] > 0.3:
        report += "   - 改善睡眠质量，调整作息时间\n"

    if blood_analysis['fasting_avg'] > 6.1 or blood_analysis['bedtime_avg'] > 7.8:
        report += "   - 控制晚餐时间和份量，避免血糖过高\n"
        report += "   - 晚餐后进行30分钟轻度运动\n"

    report += "\n2. **财务管理**:\n"
    if consumption_analysis['has_data']:
        if consumption_analysis['avg_daily'] > 150:
            report += "   - 适当控制非必要支出\n"
        report += f"   - 关注主要消费类别（{consumption_analysis['main_category']}）的支出优化\n"

    report += "\n3. **工作计划**:\n"
    if goal_analysis['work_rate'] < 0.8:
        report += "   - 合理规划任务，提高工作完成率\n"
    else:
        report += "   - 继续保持良好的工作状态\n"

    # 添加相关链接
    prev_week = week - 1
    next_week = week + 1
    report += f"\n---\n\n## 🔗 相关链接\n"
    report += f"- 上周：[[第{prev_week}周统计报表]]\n"
    report += f"- 下周：[[第{next_week}周统计报表]]\n"
    report += f"- 月视图：[[{year}年{month}月OKR]]\n"

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
    consumption_data = []
    for d in data:
        parsed = parse_consumption(d['content'])
        parsed['date'] = d['date']
        consumption_data.append(parsed)
    task_data = []
    for d in data:
        parsed = parse_task_completion(d['content'])
        parsed['date'] = d['date']
        task_data.append(parsed)
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

        # 生成KR按优先级完成率图表
        priority_chart_path = output_dir / "okr_priority.svg"
        priority_data = {'kr_by_priority': goal_analysis['kr_by_priority']}
        if generate_chart_svg('okr_priority', 'KR按优先级完成率', priority_data,
                             priority_chart_path, script_path):
            chart_paths['okr_priority'] = priority_chart_path

        if chart_paths:
            charts_section = '\n## 📈 趋势图表\n\n'
            if 'blood_sugar_trend' in chart_paths:
                charts_section += f'### 血糖监测趋势\n\n![血糖趋势]({Path(chart_paths["blood_sugar_trend"]).name})\n\n'
            if 'consumption_trend' in chart_paths:
                charts_section += f'### 每日消费趋势\n\n![消费趋势]({Path(chart_paths["consumption_trend"]).name})\n\n'
            if 'task_completion_rate' in chart_paths:
                charts_section += f'### OKR任务完成率趋势\n\n![OKR完成率]({Path(chart_paths["task_completion_rate"]).name})\n\n'
            if 'okr_priority' in chart_paths:
                charts_section += f'### KR按优先级完成率\n\n![KR优先级]({Path(chart_paths["okr_priority"]).name})\n\n'

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

    report += f"""## 🎯 OKR目标完成情况

### 任务完成概览

| 任务类型 | 总数 | 已完成 | 进行中 | 已取消 | 完成率 |
|:---|:---:|:---:|:---:|:---:|:---:|
| 📋 今日待办 | {goal_analysis['todo_total']} 项 | {goal_analysis['todo_completed']} 项 | - | - | **{goal_analysis['todo_rate']*100:.1f}%** |
| ⚡ 临时任务 | {goal_analysis['temp_total']} 项 | {goal_analysis['temp_completed']} 项 | - | - | **{goal_analysis['temp_rate']*100:.1f}%** |
| 🎯 关键结果(KR) | {goal_analysis['kr_total']} 项 | {goal_analysis['kr_completed']} 项 | {goal_analysis['kr_in_progress']} 项 | {goal_analysis['kr_cancelled']} 项 | **{goal_analysis['kr_rate']*100:.1f}%** |
| **总计** | {goal_analysis['total_tasks']} 项 | {goal_analysis['total_completed']} 项 | {goal_analysis['kr_in_progress']} 项 | {goal_analysis['kr_cancelled']} 项 | **{goal_analysis['overall_rate']*100:.1f}%** |

### KR按优先级统计

| 优先级 | 总数 | 已完成 | 完成率 |
|:---|:---:|:---:|:---:|
| 🔴 P0(最高) | {goal_analysis['kr_by_priority']['P0']['total']} 项 | {goal_analysis['kr_by_priority']['P0']['completed']} 项 | **{goal_analysis['kr_by_priority']['P0']['completed']/goal_analysis['kr_by_priority']['P0']['total']*100 if goal_analysis['kr_by_priority']['P0']['total'] > 0 else 0:.1f}%** |
| 🟡 P1(高) | {goal_analysis['kr_by_priority']['P1']['total']} 项 | {goal_analysis['kr_by_priority']['P1']['completed']} 项 | **{goal_analysis['kr_by_priority']['P1']['completed']/goal_analysis['kr_by_priority']['P1']['total']*100 if goal_analysis['kr_by_priority']['P1']['total'] > 0 else 0:.1f}%** |
| 🟢 P2(中) | {goal_analysis['kr_by_priority']['P2']['total']} 项 | {goal_analysis['kr_by_priority']['P2']['completed']} 项 | **{goal_analysis['kr_by_priority']['P2']['completed']/goal_analysis['kr_by_priority']['P2']['total']*100 if goal_analysis['kr_by_priority']['P2']['total'] > 0 else 0:.1f}%** |

"""

    # 添加按关联月OKR分组统计
    if goal_analysis['kr_by_month_okr']:
        report += "### KR按关联月OKR分组统计\n\n"
        for okr_name, stats in goal_analysis['kr_by_month_okr'].items():
            rate = stats['completed'] / stats['total'] * 100 if stats['total'] > 0 else 0
            display_name = okr_name.replace('[[', '').replace(']]', '').replace('|月OKR', '').replace('|季度', '')
            report += f"#### 📌 {display_name}\n\n"
            report += "| 指标 | 数值 |\n"
            report += "|:---|:---: |\n"
            report += f"| KR总数 | {stats['total']} 项 |\n"
            report += f"| 已完成 | {stats['completed']} 项 |\n"
            report += f"| 进行中 | {stats['in_progress']} 项 |\n"
            report += f"| 已取消 | {stats['cancelled']} 项 |\n"
            report += f"| 完成率 | **{rate:.1f}%** |\n\n"

    report += f"{charts_section}"
    report += """## 💡 建议与总结

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

    report += "\n### OKR达成建议\n"

    # 今日待办建议
    if goal_analysis['todo_rate'] < 0.7:
        report += f"- 今日待办完成率 {goal_analysis['todo_rate']*100:.1f}%，建议合理规划每日任务量\n"

    # KR关键结果建议
    if goal_analysis['kr_rate'] < 0.6:
        report += f"- 关键结果(KR)完成率 {goal_analysis['kr_rate']*100:.1f}%，核心目标推进偏慢，建议:\n"
        report += "  - 将大目标拆分为更小的可执行任务\n"
        report += "  - 优先处理高优先级(P0/P1)的KR\n"
    elif goal_analysis['kr_rate'] < 0.8:
        report += f"- 关键结果(KR)完成率 {goal_analysis['kr_rate']*100:.1f}%，整体进展良好，可进一步提高效率\n"

    # P0优先级建议
    p0_total = goal_analysis['kr_by_priority']['P0']['total']
    p0_completed = goal_analysis['kr_by_priority']['P0']['completed']
    if p0_total > 0 and p0_completed < p0_total:
        report += f"- 有 {p0_total - p0_completed} 个P0级高优先级KR未完成，建议优先处理\n"

    # 总体评价
    if goal_analysis['overall_rate'] >= 0.8:
        report += "- ✅ 各项OKR任务完成情况良好，继续保持！\n"

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
    parser.add_argument('--ai-charts', action='store_true', default=True,
                        help='使用 ascii-chart-to-svg 技能生成SVG图表 (默认启用)')
    parser.add_argument('--no-charts', action='store_true',
                        help='禁用图表生成')

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

    use_charts = not args.no_charts

    if args.type == 'week':
        generate_weekly_report(args.year, args.month, args.week, data, output_path, use_charts)
    else:
        generate_monthly_report(args.year, args.month, data, output_path, use_charts)


if __name__ == '__main__':
    main()

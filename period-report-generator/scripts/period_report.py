#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
周期统计报表生成器
根据日记文件生成周/月统计报表，包括血糖变化、消费趋势、目标完成率
"""

import re
import sys
import io
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# 设置标准输出为 UTF-8 编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def parse_blood_sugar(content: str) -> dict:
    """
    解析血糖数据

    Returns:
        {'fasting': float, 'post_meal': float, 'bedtime': float}
    """
    result = {'fasting': None, 'post_meal': None, 'bedtime': None}

    # 空腹血糖 (格式：：:: 5.4)
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
        {'quality': str}  # quality: '差' | '一般' | '好' | None
    """
    result = {'quality': None}

    # 查找睡眠部分，检查哪个选项被勾选
    sleep_pattern = r'- 睡眠：.*?(?=\n-|\n##|\n###)'
    sleep_match = re.search(sleep_pattern, content, re.DOTALL)

    if not sleep_match:
        return result

    sleep_section = sleep_match.group(0)

    # 检查差
    if re.search(r'- \[x\]\s*差', sleep_section):
        result['quality'] = '差'
    # 检查一般
    elif re.search(r'- \[x\]\s*一般', sleep_section):
        result['quality'] = '一般'
    # 检查好
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

    # 消费笔数
    count_match = re.search(r'消费笔数.*?：\s*(\d+)', content)
    if count_match:
        result['count'] = int(count_match.group(1))

    # 总支出
    total_match = re.search(r'总支出.*?：.*?\*\*(.+?)\*\*.*?元', content)
    if total_match:
        try:
            result['total'] = float(total_match.group(1))
        except ValueError:
            result['total'] = 0

    # 最大支出
    max_match = re.search(r'最大支出.*?：([\d.]+)', content)
    if max_match:
        result['max_amount'] = float(max_match.group(1))

    # 主要类别
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

    # 今日计划完成情况
    planned_tasks = re.findall(r'^- \[([ x])\]', content, re.MULTILINE)
    result['planned'] = len(planned_tasks)
    result['completed'] = sum(1 for t in planned_tasks if t == 'x')

    # 工作/学习任务完成情况
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

    # 中文月份映射
    chinese_months = ['一月', '二月', '三月', '四月', '五月', '六月',
                      '七月', '八月', '九月', '十月', '十一月', '十二月']

    month_cn = chinese_months[month - 1] if 1 <= month <= 12 else f"{month}月"

    if week:
        # 查找指定周的文件
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

        # 去重
        week_dir_names = list(set(week_dir_names))

        for week_name in week_dir_names:
            week_dir = base_dir / f"日记/{year}年/{month_cn}/{week_name}"
            if week_dir.exists() and week_dir.is_dir():
                diary_files.extend(week_dir.glob("*.md"))
                if diary_files:
                    break

        # 如果还是没找到，尝试数字月份
        if not diary_files:
            for week_name in week_dir_names:
                week_dir = base_dir / f"日记/{year}年/{month}月/{week_name}"
                if week_dir.exists() and week_dir.is_dir():
                    diary_files.extend(week_dir.glob("*.md"))
                    if diary_files:
                        break
    else:
        # 查找指定月的所有文件
        month_dirs = [
            base_dir / f"日记/{year}年/{month_cn}",
            base_dir / f"日记/{year}年/{month}月",
        ]

        for month_dir in month_dirs:
            if month_dir.exists() and month_dir.is_dir():
                for week_dir in month_dir.iterdir():
                    if week_dir.is_dir():
                        diary_files.extend(week_dir.glob("*.md"))
                if diary_files:
                    break

    return sorted(diary_files)


def analyze_blood_sugar_trend(data: list) -> dict:
    """
    分析血糖趋势

    Args:
        data: 血糖数据列表 [{'date': str, 'fasting': float, 'post_meal': float, 'bedtime': float}]

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
    # 检查是否有有效的消费数据（总消费大于0）
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

    # 统计各类别出现次数
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
        data: 睡眠质量数据列表 [{'quality': str}]

    Returns:
        统计分析结果
    """
    # 统计各质量等级的天数
    quality_counts = {'差': 0, '一般': 0, '好': 0}

    for d in data:
        quality = d.get('quality')
        if quality in quality_counts:
            quality_counts[quality] += 1

    total_days = sum(quality_counts.values())

    # 计算平均睡眠质量 (差=1, 一般=2, 好=3)
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

    # 找出最常见的睡眠质量
    most_common = max(quality_counts, key=quality_counts.get) if total_days > 0 else '无'

    # 计算好和一般的比例（良好睡眠率）
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


def generate_weekly_report(year: int, month: int, week: int, data: list, output_path: Path):
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

    # 只在有消费数据时添加消费统计部分
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

## 📈 趋势图表

### 血糖趋势
| 日期 | 空腹 | 餐后2h | 睡前 |
| :---: | :---: | :---: | :---: |
{"".join([f"| {d['date'].split('-')[-1] if '-' in d['date'] else d['date']} | {d['fasting'] or '-'} | {d['post_meal'] or '-'} | {d['bedtime'] or '-'} |\n" for d in blood_sugar_data])}
"""

    # 只在有消费数据时添加每日消费图表
    if consumption_analysis['has_data']:
        report += f"""
### 每日消费
| 日期 | 消费额 | 笔数 |
| :---: | :---: | :---: |
{"".join([f"| {d['date'].split('-')[-1] if '-' in d['date'] else d['date']} | {consumption_data[i]['total']:.2f} | {consumption_data[i]['count']} |\n" for i, d in enumerate(data)])}
"""

    report += f"""
### 任务完成情况
| 日期 | 计划完成 | 工作完成 |
| :---: | :---: | :---: |
{"".join([f"| {d['date'].split('-')[-1] if '-' in d['date'] else d['date']} | {task_data[i]['completed']}/{task_data[i]['planned']} | {task_data[i]['work_completed']}/{task_data[i]['work_total']} |\n" for i, d in enumerate(data)])}

## 💡 建议与总结

### 健康建议
"""

    # 睡眠质量建议
    if sleep_analysis['bad_rate'] >= 0.5:
        report += f"- 睡眠质量需要改善，本周{sleep_analysis['bad_days']}天睡眠较差，建议调整作息时间\n"
    elif sleep_analysis['bad_rate'] > 0.2:
        report += f"- 本周有{sleep_analysis['bad_days']}天睡眠较差，注意休息和压力管理\n"
    elif sleep_analysis['good_days'] == sleep_analysis['total_days'] and sleep_analysis['total_days'] > 0:
        report += "- 本周每天睡眠质量都很好，继续保持！\n"
    elif sleep_analysis['avg_quality'] >= 2:
        report += f"- 平均睡眠质量{sleep_analysis['avg_quality']:.1f}分（满分3分），整体表现良好\n"

    # 血糖建议
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

    # 只在有消费数据时添加消费建议
    if consumption_analysis['has_data']:
        report += "\n### 消费建议\n"
        if consumption_analysis['avg_daily'] > 100:
            report += f"- 日均消费 {consumption_analysis['avg_daily']:.2f} 元，建议适当控制支出\n"
        report += f"- 主要消费类别为 {consumption_analysis['main_category']}，可关注该类别的支出优化\n"

    # 目标建议
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


def generate_monthly_report(year: int, month: int, data: list, output_path: Path):
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

    # 开始构建报表
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

    # 只在有消费数据时添加消费统计部分
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

## 💡 建议与总结

### 健康建议
"""

    # 睡眠质量建议
    if sleep_analysis['bad_rate'] >= 0.5:
        report += f"- 睡眠质量需要改善，本月{sleep_analysis['bad_days']}天睡眠较差，建议调整作息时间\n"
    elif sleep_analysis['bad_rate'] > 0.2:
        report += f"- 本月有{sleep_analysis['bad_days']}天睡眠较差，注意休息和压力管理\n"
    elif sleep_analysis['good_days'] == sleep_analysis['total_days'] and sleep_analysis['total_days'] > 0:
        report += "- 本月每天睡眠质量都很好，继续保持！\n"
    elif sleep_analysis['avg_quality'] >= 2:
        report += f"- 平均睡眠质量{sleep_analysis['avg_quality']:.1f}分（满分3分），整体表现良好\n"

    # 血糖建议
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

    # 只在有消费数据时添加消费建议
    if consumption_analysis['has_data']:
        report += "\n### 消费建议\n"
        if consumption_analysis['avg_daily'] > 100:
            report += f"- 日均消费 {consumption_analysis['avg_daily']:.2f} 元，建议适当控制支出\n"
        report += f"- 主要消费类别为 {consumption_analysis['main_category']}，可关注该类别的支出优化\n"
        report += f"- 本月总支出 {consumption_analysis['total']:.2f} 元\n"

    # 目标建议
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

    args = parser.parse_args()

    if args.type == 'week' and not args.week:
        print("❌ 生成周报时必须指定 --week 参数")
        sys.exit(1)

    base_dir = Path(args.base_dir)

    # 查找日记文件
    diary_files = find_diary_files(base_dir, args.year, args.month, args.week)

    if not diary_files:
        print(f"❌ 未找到 {args.year}年{args.month}月", end='')
        if args.week:
            print(f"第{args.week}周 的日记文件")
        else:
            print(" 的日记文件")
        sys.exit(1)

    print(f"📖 找到 {len(diary_files)} 个日记文件")

    # 读取日记数据
    data = []
    for file_path in diary_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            date = file_path.stem  # 从文件名提取日期
            data.append({'date': date, 'content': content})
        except Exception as e:
            print(f"⚠️  读取文件失败 {file_path}: {e}")

    if not data:
        print("❌ 没有可用的数据")
        sys.exit(1)

    # 确定输出路径
    if args.output:
        output_path = Path(args.output)
    else:
        if args.type == 'week':
            # 放在周目录下
            week_dir = diary_files[0].parent
            output_path = week_dir / f"第{args.week}周统计报表.md"
        else:
            # 放在月目录下
            month_dir = diary_files[0].parent.parent
            output_path = month_dir / f"{args.year}年{args.month}月统计报表.md"

    # 生成报表
    if args.type == 'week':
        generate_weekly_report(args.year, args.month, args.week, data, output_path)
    else:
        generate_monthly_report(args.year, args.month, data, output_path)


if __name__ == '__main__':
    main()

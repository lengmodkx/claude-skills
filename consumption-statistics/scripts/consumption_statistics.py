#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消费统计助手
自动统计日记中的今日消费清单并填写统计数据
"""

import re
import sys
import io
import argparse
from datetime import datetime
from pathlib import Path

# 设置标准输出为 UTF-8 编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def parse_consumption_table(content: str) -> list:
    """
    解析消费清单表格

    Args:
        content: 日记文件内容

    Returns:
        消费记录列表，每条记录包含 {time, category, amount, note}
    """
    # 查找今日消费清单标题到下一个标题之间的内容
    title_pattern = r'#### 📊 今日消费清单\s*\n(.*?)(?=\n####|\n###|\n##|\Z)'
    title_match = re.search(title_pattern, content, re.DOTALL)

    if not title_match:
        return []

    table_section = title_match.group(1)

    # 提取所有以 | 开头的表格行（跳过表头和分隔符）
    lines = table_section.split('\n')
    data_lines = []
    for i, line in enumerate(lines):
        # 跳过表头行（包含"时间"、"金额"、"备注"等）和分隔符行
        if line.strip().startswith('|') and i > 1:
            # 跳过分隔符行（只包含:---等）
            if ':---' not in line and '时间' not in line and '金额' not in line:
                data_lines.append(line)

    records = []
    for line in data_lines:
        # 解析表格行: | 10:05 | 🍜 餐饮 | 22.7 | 包子 |
        cells = [cell.strip() for cell in line.split('|')[1:-1]]  # 去掉首尾空元素

        if len(cells) >= 3:  # 至少需要3列：时间、类别、金额
            time_str = cells[0]
            category = cells[1].strip()  # 移除emoji等特殊字符
            amount_str = cells[2]
            note = cells[3] if len(cells) > 3 else ''

            # 提取金额数字
            amount_match = re.search(r'([\d.]+)', amount_str)
            if amount_match:
                amount = float(amount_match.group(1))

                # 提取纯类别名称（移除emoji）
                category_clean = re.sub(r'^[^\w\u4e00-\u9fff]+', '', category).strip()

                records.append({
                    'time': time_str,
                    'category': category_clean,
                    'amount': amount,
                    'note': note
                })

    return records


def calculate_statistics(records: list) -> dict:
    """
    计算消费统计数据

    Args:
        records: 消费记录列表

    Returns:
        统计数据字典
    """
    if not records:
        return {
            'count': 0,
            'total': 0,
            'max_amount': 0,
            'max_category': '',
            'max_note': '',
            'category_counts': {}
        }

    count = len(records)
    total = sum(r['amount'] for r in records)

    # 找最大支出
    max_record = max(records, key=lambda x: x['amount'])

    # 统计各类别消费次数
    category_counts = {}
    for r in records:
        cat = r['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # 找主要类别
    main_category = max(category_counts, key=category_counts.get)
    main_category_count = category_counts[main_category]

    return {
        'count': count,
        'total': total,
        'max_amount': max_record['amount'],
        'max_category': max_record['category'],
        'max_note': max_record['note'],
        'category_counts': category_counts,
        'main_category': main_category,
        'main_category_count': main_category_count
    }


def generate_statistics_section(stats: dict) -> str:
    """
    生成今日统计部分的文本

    Args:
        stats: 统计数据字典

    Returns:
        格式化的统计数据文本
    """
    if stats['count'] == 0:
        return """#### 📈 今日统计
- **消费笔数**：0 笔
- **总支出**：💰 **0** 元
"""

    # 格式化金额，最多2位小数
    total_str = f"{stats['total']:.2f}" if stats['total'] != int(stats['total']) else str(int(stats['total']))
    max_str = f"{stats['max_amount']:.2f}" if stats['max_amount'] != int(stats['max_amount']) else str(int(stats['max_amount']))

    return f"""#### 📈 今日统计
- **消费笔数**：{stats['count']} 笔
- **总支出**：💰 **{total_str}** 元
- **最大支出**：{max_str} 元（{stats['max_category']}-{stats['max_note']}）
- **主要类别**：{stats['main_category']}（{stats['main_category_count']}笔）
"""


def update_diary_with_statistics(file_path: Path, stats: dict) -> bool:
    """
    更新日记文件，添加或替换今日统计部分

    Args:
        file_path: 日记文件路径
        stats: 统计数据

    Returns:
        是否更新成功
    """
    # 读取文件
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False

    # 生成新的统计部分
    new_stats_section = generate_statistics_section(stats)

    # 查找是否已存在今日统计部分
    stats_pattern = r'#### 📈 今日统计\s*\n(?:-[^\n]+\n?)*'

    if re.search(stats_pattern, content):
        # 替换现有统计
        content = re.sub(stats_pattern, new_stats_section.strip(), content)
    else:
        # 在消费清单后添加统计
        consumption_pattern = r'(#### 📊 今日消费清单.*?(?=\n####|\n###|\n##|\Z))'
        match = re.search(consumption_pattern, content, re.DOTALL)

        if match:
            # 在消费清单后面插入
            insert_pos = match.end()
            content = content[:insert_pos] + '\n\n' + new_stats_section.strip() + content[insert_pos:]
        else:
            print("⚠️  未找到今日消费清单，无法添加统计")
            return False

    # 写回文件
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"❌ 写入文件失败: {e}")
        return False


def find_diary_by_date(base_dir: Path, date_str: str) -> Path:
    """
    根据日期查找日记文件

    Args:
        base_dir: 日记基础目录
        date_str: 日期字符串 (YYYY-MM-DD)

    Returns:
        日记文件路径，如果找不到返回 None
    """
    # 解析日期
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None

    # 计算周数
    week_num = date.isocalendar()[1]

    # 构建可能的路径
    year = date.year
    month = date.month
    possible_paths = [
        base_dir / f"日记/{year}年/{month}月/第{week_num}周/{date_str}.md",
        base_dir / f"日记/{year}年/{month}月/{week_num}周/{date_str}.md",
        base_dir / f"日记/{year}年/{month}月/{week_num:02d}周/{date_str}.md",
        base_dir / f"日记/{year}年/{month:02d}月/第{week_num}周/{date_str}.md",
        base_dir / f"日记/{year}年/{month:02d}月/{week_num}周/{date_str}.md",
        base_dir / f"日记/{year}年/{month:02d}月/{week_num:02d}周/{date_str}.md",
        base_dir / f"日记/{year}年/{month}月/第{week_num:02d}周/{date_str}.md",
    ]

    for path in possible_paths:
        if path.exists():
            return path

    return None


def main():
    parser = argparse.ArgumentParser(description='消费统计助手 - 自动统计日记中的今日消费')
    parser.add_argument('--date', '-d', default=datetime.now().strftime('%Y-%m-%d'),
                        help='日期 (YYYY-MM-DD)，默认为今天')
    parser.add_argument('--file', '-f', help='直接指定日记文件路径')
    parser.add_argument('--base-dir', '-b', default='.', help='日记基础目录')

    args = parser.parse_args()

    # 确定日记文件路径
    if args.file:
        diary_path = Path(args.file)
    else:
        diary_path = find_diary_by_date(Path(args.base_dir), args.date)

    if not diary_path or not diary_path.exists():
        print(f"❌ 找不到日记文件: {args.date}")
        print(f"   请检查路径或使用 --file 参数直接指定文件")
        sys.exit(1)

    print(f"📖 读取日记: {diary_path}")

    # 读取日记内容
    try:
        with open(diary_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        sys.exit(1)

    # 解析消费清单
    records = parse_consumption_table(content)

    if not records:
        print("⚠️  未找到今日消费清单或清单为空")
        sys.exit(0)

    print(f"📊 找到 {len(records)} 条消费记录")

    # 计算统计
    stats = calculate_statistics(records)

    print(f"💰 总支出: {stats['total']:.2f} 元")
    print(f"📈 最大支出: {stats['max_amount']:.2f} 元 ({stats['max_category']}-{stats['max_note']})")

    # 更新日记
    if update_diary_with_statistics(diary_path, stats):
        print("✅ 统计数据已更新到日记")
    else:
        print("❌ 更新失败")
        sys.exit(1)


if __name__ == '__main__':
    main()

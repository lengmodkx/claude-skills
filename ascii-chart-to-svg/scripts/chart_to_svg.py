#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASCII Chart to SVG Converter
解析文本格式的图表数据并生成SVG矢量图
"""

import re
import sys
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ChartData:
    """图表数据结构"""
    title: str
    y_values: List[float]
    y_labels: List[str]
    data_points: List[Optional[float]]
    x_labels: List[str]


def parse_ascii_chart(text: str) -> ChartData:
    """
    解析ASCII格式的图表文本

    Args:
        text: 图表文本内容

    Returns:
        ChartData: 解析后的图表数据
    """
    lines = text.strip().split('\n')
    lines = [line.rstrip() for line in lines if line.strip()]

    # 解析标题
    title = lines[0].strip(':').strip()

    # 初始化数据结构
    y_values = []
    y_labels = []
    x_labels = []

    # 先扫描找到X轴底线位置
    x_axis_line_idx = -1
    x_axis_line = ""

    for i, line in enumerate(lines[1:], 1):
        if any(c in line for c in ['┼', '━', '─']):
            x_axis_line_idx = i
            x_axis_line = line
            # 提取X轴标签(在下一行)
            if i + 1 < len(lines):
                x_line = lines[i + 1]
                # 提取数字标签
                x_labels = re.findall(r'\d+', x_line)
            break

    # 收集所有数据标记的位置
    data_marks = []  # (position, y_value)

    for i, line in enumerate(lines[1:x_axis_line_idx], 1):
        # 匹配Y轴刻度行: "数值 ┤"
        # 先找到┤或│的位置
        split_pos = -1
        for j, c in enumerate(line):
            if c in ['┤', '│']:
                split_pos = j
                break

        if split_pos >= 0:
            # 提取Y轴数值
            y_part = line[:split_pos]
            y_match = re.match(r'^\s*([\d\.]+)', y_part)
            if y_match:
                y_val = float(y_match.group(1))
                y_values.append(y_val)
                y_labels.append(y_match.group(1))

                # 获取数据内容部分
                content = line[split_pos + 1:]

                # 查找所有█的位置
                for pos, char in enumerate(content):
                    if char in ['█', '▀', '■', '#']:
                        data_marks.append((pos, y_val))

    # 根据X轴标签位置进行聚类
    if x_labels and data_marks:
        # 获取X轴标签在标签行中的位置
        label_line_idx = x_axis_line_idx + 1 if x_axis_line_idx + 1 < len(lines) else x_axis_line_idx
        label_line = lines[label_line_idx]

        label_positions = []
        for label in x_labels:
            # 在标签行中查找标签位置
            label_pos = label_line.find(label)
            if label_pos != -1:
                label_positions.append(label_pos)

        # 如果找不到标签位置,使用X轴行
        if not label_positions:
            for label in x_labels:
                label_pos = x_axis_line.find(label)
                if label_pos != -1:
                    label_positions.append(label_pos)

        # 如果还是找不到,使用均匀分布
        if not label_positions:
            num_labels = len(x_labels)
            step = len(x_axis_line) // (num_labels + 1)
            label_positions = [step * (i + 1) for i in range(num_labels)]

        # 为每个标签分配数据点
        data_points = [None] * len(x_labels)

        # 对于每个数据标记,找到最近的标签
        for mark_pos, mark_val in data_marks:
            # 找到最近的标签索引
            min_dist = float('inf')
            closest_label_idx = -1

            for i, label_pos in enumerate(label_positions):
                dist = abs(mark_pos - label_pos)
                if dist < min_dist:
                    min_dist = dist
                    closest_label_idx = i

            # 如果距离足够近,分配给该标签
            if closest_label_idx >= 0 and min_dist < 30:  # 阈值可调整
                if data_points[closest_label_idx] is None or mark_val > data_points[closest_label_idx]:
                    data_points[closest_label_idx] = mark_val
    else:
        # 没有X轴标签时的处理
        data_points = [val for _, val in data_marks] if data_marks else []

    return ChartData(
        title=title,
        y_values=y_values,
        y_labels=y_labels,
        data_points=data_points,
        x_labels=x_labels
    )


def generate_svg(chart: ChartData, width: int = 800, height: int = 400) -> str:
    """
    生成SVG图表

    Args:
        chart: 图表数据
        width: SVG宽度
        height: SVG高度

    Returns:
        str: SVG字符串
    """
    # 计算边距和绘图区域
    margin_left = 80
    margin_right = 40
    margin_top = 60
    margin_bottom = 60

    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    # Y轴范围
    if chart.y_values:
        y_min, y_max = min(chart.y_values), max(chart.y_values)
        y_range = y_max - y_min
        if y_range == 0:
            y_range = y_max if y_max > 0 else 1
    else:
        y_min, y_max, y_range = 0, 100, 100

    # X轴范围
    num_points = len(chart.data_points)
    x_step = plot_width / (num_points + 1) if num_points > 0 else plot_width

    # 构建SVG
    svg_parts = []

    # SVG头部
    svg_parts.append(f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">')
    svg_parts.append('  <style>')
    svg_parts.append('    .title { font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; }')
    svg_parts.append('    .axis-label { font-family: Arial, sans-serif; font-size: 12px; fill: #666; }')
    svg_parts.append('    .grid-line { stroke: #e0e0e0; stroke-width: 1; }')
    svg_parts.append('    .axis-line { stroke: #333; stroke-width: 1.5; }')
    svg_parts.append('    .bar { fill: #4CAF50; stroke: #45a049; stroke-width: 1; }')
    svg_parts.append('  </style>')

    # 背景
    svg_parts.append(f'  <rect width="{width}" height="{height}" fill="white"/>')

    # 标题
    svg_parts.append(f'  <text x="{width//2}" y="30" text-anchor="middle" class="title">{chart.title}</text>')

    # Y轴网格线和标签
    for i, (y_val, label) in enumerate(zip(chart.y_values, chart.y_labels)):
        y_pos = margin_top + (y_max - y_val) / y_range * plot_height

        # 网格线
        svg_parts.append(f'  <line x1="{margin_left}" y1="{y_pos}" x2="{width - margin_right}" y2="{y_pos}" class="grid-line"/>')

        # Y轴标签
        svg_parts.append(f'  <text x="{margin_left - 10}" y="{y_pos + 4}" text-anchor="end" class="axis-label">{label}</text>')

    # Y轴主线
    svg_parts.append(f'  <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}" class="axis-line"/>')

    # X轴主线
    svg_parts.append(f'  <line x1="{margin_left}" y1="{height - margin_bottom}" x2="{width - margin_right}" y2="{height - margin_bottom}" class="axis-line"/>')

    # 数据柱
    bar_width = x_step * 0.6

    for i, value in enumerate(chart.data_points):
        if value is not None and value >= y_min:
            x_pos = margin_left + (i + 1) * x_step - bar_width / 2

            # 计算柱子高度
            bar_height = (value - y_min) / y_range * plot_height
            y_pos = margin_top + plot_height - bar_height

            # 绘制柱子
            svg_parts.append(f'  <rect x="{x_pos}" y="{y_pos}" width="{bar_width}" height="{bar_height}" class="bar">')
            svg_parts.append(f'    <title>{chart.x_labels[i] if i < len(chart.x_labels) else i+1}: {value}</title>')
            svg_parts.append('  </rect>')

    # X轴标签
    for i, label in enumerate(chart.x_labels[:num_points]):
        x_pos = margin_left + (i + 1) * x_step
        svg_parts.append(f'  <text x="{x_pos}" y="{height - margin_bottom + 20}" text-anchor="middle" class="axis-label">{label}</text>')

    svg_parts.append('</svg>')

    return '\n'.join(svg_parts)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python chart_to_svg.py <output_file.svg>")
        print("\nOr pipe chart data:")
        print("  cat chart.txt | python chart_to_svg.py output.svg")
        sys.exit(1)

    output_file = sys.argv[1]

    # 从标准输入读取图表数据
    # Windows环境下使用二进制模式读取并解码
    if sys.platform == 'win32':
        import io
        text = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8').read()
    else:
        text = sys.stdin.read()

    try:
        chart = parse_ascii_chart(text)
        svg = generate_svg(chart)

        # 使用UTF-8编码写入文件
        with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
            f.write(svg)

        print(f"SVG has been generated: {output_file}")
        print(f"Title: {chart.title}")
        print(f"Data points: {chart.data_points}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

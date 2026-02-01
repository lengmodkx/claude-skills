#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASCII Chart to SVG Converter
 解析文本格式的图表数据并生成SVG矢量图
 支持柱状图和折线图
"""

import re
import json
import os
import sys
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class ChartData:
    """图表数据结构"""
    title: str
    y_values: List[float]
    y_labels: List[str]
    data_points: List[Optional[float]]
    x_labels: List[str]
    chart_type: str = "bar"  # "bar", "line", 或 "multi_line"
    series: List[Dict[str, Any]] = None  # 多序列数据
    normal_range: Dict[str, float] = None  # 正常范围


def parse_json_chart(text: str) -> Optional[ChartData]:
    """尝试解析JSON格式的图表数据"""
    text = text.strip()
    if text.startswith('{'):
        try:
            data = json.loads(text)
            return ChartData(
                title=data.get('title', ''),
                y_values=data.get('y_values', []),
                y_labels=data.get('y_labels', []),
                data_points=data.get('data_points', []),
                x_labels=data.get('x_labels', []),
                chart_type=data.get('chart_type', 'bar'),
                series=data.get('series', None),
                normal_range=data.get('normal_range', None)
            )
        except json.JSONDecodeError:
            pass
    return None


def parse_ascii_chart(text: str) -> ChartData:
    """
    解析ASCII格式的图表文本

    Args:
        text: 图表文本内容

    Returns:
        ChartData: 解析后的图表数据
    """
    # 首先尝试解析JSON格式
    json_chart = parse_json_chart(text)
    if json_chart:
        return json_chart

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
    x_label_line_idx = -1

    for i, line in enumerate(lines[1:], 1):
        if any(c in line for c in ['┼', '━', '─']):
            x_axis_line_idx = i
            x_axis_line = line
            # 提取X轴标签(在下一行)
            if i + 1 < len(lines):
                x_label_line_idx = i + 1
                x_line = lines[i + 1]
                # 提取数字标签
                x_labels = re.findall(r'\d+', x_line)
            break

    # 收集所有数据标记的位置
    data_marks = []  # (position, y_value)
    split_pos_ref = None  # 参考的split位置
    column_width = 3  # 每列宽度固定为3个字符

    for i, line in enumerate(lines[1:x_axis_line_idx], 1):
        # 匹配Y轴刻度行: "数值 ┤"
        # 先找到┤或│的位置
        split_pos = -1
        for j, c in enumerate(line):
            if c in ['┤', '│']:
                split_pos = j
                break

        if split_pos >= 0:
            # 保存第一个有效的split位置作为参考
            if split_pos_ref is None:
                split_pos_ref = split_pos

            # 提取Y轴数值
            y_part = line[:split_pos]
            y_match = re.match(r'^\s*([\d\.]+)', y_part)
            if y_match:
                y_val = float(y_match.group(1))
                y_values.append(y_val)
                y_labels.append(y_match.group(1))

                # 获取数据内容部分
                content = line[split_pos + 1:]

                # 直接遍历每个字符位置，查找数据标记
                for pos in range(len(content)):
                    char = content[pos]
                    char_code = ord(char) if len(char) > 0 else 0
                    if char_code in [0x2588, 0x2580, 0x25A0] or char in ['█', '■', '#', '●', '◉']:
                        # 列索引 = (split_pos + 1 + pos) // 列宽度
                        col_idx = (split_pos + 1 + pos) // column_width
                        data_marks.append((col_idx, y_val))

    # 处理X轴标签位置
    if x_labels and x_label_line_idx > 0:
        label_line = lines[x_label_line_idx]

        # 重新提取X轴标签和位置
        x_label_positions = []
        for match in re.finditer(r'(\d+)', label_line):
            label = match.group(1)
            pos = match.start()
            col_idx = pos // column_width
            x_label_positions.append((label, col_idx))

        # 为每个标签分配数据点
        if data_marks:
            # 按列索引排序数据标记
            sorted_marks = sorted(data_marks, key=lambda x: x[0])
            # 收集每个列的最大值
            col_to_max = {}
            for col_idx, val in sorted_marks:
                if col_idx not in col_to_max or val > col_to_max[col_idx]:
                    col_to_max[col_idx] = val
            # 按列索引排序
            sorted_cols = sorted(col_to_max.keys())
            # 创建数据点数组（按顺序）
            sorted_values = [col_to_max[col] for col in sorted_cols]
            # 匹配X轴标签数量
            if len(sorted_values) >= len(x_labels):
                data_points = sorted_values[:len(x_labels)]
            else:
                # 如果数据点少于标签，用None填充
                data_points = sorted_values + [None] * (len(x_labels) - len(sorted_values))
            # 更新x_labels
            x_labels = x_labels[:len(data_points)]
        else:
            data_points = [None] * len(x_labels)
    else:
        # 没有X轴标签时的处理
        if data_marks:
            # 使用相对顺序
            sorted_marks = sorted(data_marks, key=lambda x: x[0])
            col_to_max = {}
            for col_idx, val in sorted_marks:
                if col_idx not in col_to_max or val > col_to_max[col_idx]:
                    col_to_max[col_idx] = val
            sorted_cols = sorted(col_to_max.keys())
            data_points = [col_to_max[col] for col in sorted_cols]
            x_labels = [str(i+1) for i in range(len(data_points))]
        else:
            data_points = []
            x_labels = []

    return ChartData(
        title=title,
        y_values=y_values,
        y_labels=y_labels,
        data_points=data_points,
        x_labels=x_labels,
        chart_type="bar"
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

    # Y轴范围 - 如果chart中有预设的y_values，使用它们
    if chart.y_values and len(chart.y_values) >= 2:
        y_min = min(chart.y_values)
        y_max = max(chart.y_values)
        y_range = y_max - y_min
        y_labels = chart.y_labels if chart.y_labels else [str(v) for v in chart.y_values]
    else:
        if chart.data_points:
            data_vals = [v for v in chart.data_points if v is not None]
            if data_vals:
                y_min, y_max = min(data_vals), max(data_vals)
                y_range = y_max - y_min
                if y_range == 0:
                    y_range = y_max if y_max > 0 else 1
            else:
                y_min, y_max, y_range = 0, 100, 100
        else:
            y_min, y_max, y_range = 0, 100, 100
        y_labels = chart.y_labels if chart.y_labels else []

    # X轴范围 - 多序列图使用series数据长度
    if chart.chart_type == "multi_line" and chart.series:
        # 使用第一个series的长度作为数据点数量
        num_points = len(chart.series[0].get('data', [])) if chart.series else len(chart.data_points)
    else:
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
    svg_parts.append('    .line { fill: none; stroke: #2196F3; stroke-width: 2; }')
    svg_parts.append('    .line-point { fill: #2196F3; stroke: #fff; stroke-width: 2; }')
    svg_parts.append('    .line-point-high { fill: #f44336; stroke: #fff; stroke-width: 2; }')
    svg_parts.append('  </style>')

    # 背景
    svg_parts.append(f'  <rect width="{width}" height="{height}" fill="white"/>')

    # 标题
    svg_parts.append(f'  <text x="{width//2}" y="30" text-anchor="middle" class="title">{chart.title}</text>')

    # Y轴网格线和标签
    if chart.y_values and len(chart.y_values) >= 2:
        # 使用预设的Y轴刻度
        for y_val, label in zip(chart.y_values, y_labels):
            y_pos = margin_top + (y_max - y_val) / y_range * plot_height
            svg_parts.append(f'  <line x1="{margin_left}" y1="{y_pos}" x2="{width - margin_right}" y2="{y_pos}" class="grid-line"/>')
            svg_parts.append(f'  <text x="{margin_left - 10}" y="{y_pos + 4}" text-anchor="end" class="axis-label">{label}</text>')
    else:
        # 自动生成Y轴刻度
        for i, (y_val, label) in enumerate(zip(chart.y_values, y_labels)):
            y_pos = margin_top + (y_max - y_val) / y_range * plot_height
            svg_parts.append(f'  <line x1="{margin_left}" y1="{y_pos}" x2="{width - margin_right}" y2="{y_pos}" class="grid-line"/>')
            svg_parts.append(f'  <text x="{margin_left - 10}" y="{y_pos + 4}" text-anchor="end" class="axis-label">{label}</text>')

    # Y轴主线
    svg_parts.append(f'  <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{height - margin_bottom}" class="axis-line"/>')

    # X轴主线
    svg_parts.append(f'  <line x1="{margin_left}" y1="{height - margin_bottom}" x2="{width - margin_right}" y2="{height - margin_bottom}" class="axis-line"/>')

    # 绘制正常范围区域（如果指定）
    if chart.normal_range:
        normal_min = chart.normal_range.get('min', 3.9)
        normal_max = chart.normal_range.get('max', 7.8)
        normal_y_min = margin_top + (y_max - normal_max) / y_range * plot_height
        normal_y_max = margin_top + (y_max - normal_min) / y_range * plot_height
        normal_height = normal_y_max - normal_y_min
        if normal_height > 0:
            svg_parts.append(f'  <rect x="{margin_left}" y="{normal_y_min}" width="{plot_width}" height="{normal_height}" fill="#e8f5e9" opacity="0.5"/>')

    if chart.chart_type == "multi_line" and chart.series:
        # 多序列折线图
        for series in chart.series:
            series_name = series.get('name', '')
            series_data = series.get('data', [])
            series_color = series.get('color', '#2196F3')

            # 计算该序列的数据点位置
            points = []
            for i, value in enumerate(series_data):
                x_pos = margin_left + (i + 1) * x_step
                if value is not None and value >= y_min:
                    y_pos = margin_top + (y_max - value) / y_range * plot_height
                    points.append((x_pos, y_pos))

            # 绘制折线
            if len(points) >= 2:
                points_str = ' '.join([f'{x},{y}' for x, y in points])
                svg_parts.append(f'  <polyline points="{points_str}" fill="none" stroke="{series_color}" stroke-width="2"/>')

            # 绘制数据点
            for i, value in enumerate(series_data):
                if value is not None and value >= y_min:
                    x_pos = margin_left + (i + 1) * x_step
                    y_pos = margin_top + (y_max - value) / y_range * plot_height
                    # 判断是否超出正常范围
                    if chart.normal_range:
                        normal_min = chart.normal_range.get('min', 3.9)
                        normal_max = chart.normal_range.get('max', 7.8)
                        is_abnormal = value > normal_max or value < normal_min
                        point_fill = '#f44336' if is_abnormal else series_color
                    else:
                        point_fill = series_color
                    svg_parts.append(f'  <circle cx="{x_pos}" cy="{y_pos}" r="4" fill="{point_fill}" stroke="#fff" stroke-width="1"/>')
                    # 数值标签
                    svg_parts.append(f'  <text x="{x_pos}" y="{y_pos - 10}" text-anchor="middle" font-size="10" fill="#666">{value:.1f}</text>')

        # 绘制图例
        legend_y = margin_top - 20
        for i, series in enumerate(chart.series):
            series_name = series.get('name', '')
            series_color = series.get('color', '#2196F3')
            legend_x = margin_left + i * 150
            svg_parts.append(f'  <rect x="{legend_x}" y="{legend_y - 10}" width="12" height="12" fill="{series_color}" rx="2"/>')
            svg_parts.append(f'  <text x="{legend_x + 18}" y="{legend_y}" font-family="Arial, sans-serif" font-size="11" fill="#333">{series_name}</text>')

        # X轴标签
        for i, label in enumerate(chart.x_labels[:num_points]):
            x_pos = margin_left + (i + 1) * x_step
            svg_parts.append(f'  <text x="{x_pos}" y="{height - margin_bottom + 20}" text-anchor="middle" class="axis-label">{label}</text>')
    elif chart.chart_type == "line":
        # 折线图
        # 计算每个数据点的位置
        points = []
        point_data = []  # 存储 (x_pos, y_pos, value, label)
        for i, value in enumerate(chart.data_points):
            x_pos = margin_left + (i + 1) * x_step
            if value is not None and value >= y_min:
                y_pos = margin_top + (y_max - value) / y_range * plot_height
                points.append((x_pos, y_pos))
                label = chart.x_labels[i] if i < len(chart.x_labels) else str(i+1)
                point_data.append((x_pos, y_pos, value, label))

        # 绘制折线
        if len(points) >= 2:
            points_str = ' '.join([f'{x},{y}' for x, y in points])
            svg_parts.append(f'  <polyline points="{points_str}" class="line"/>')

        # 绘制数据点和数值标签
        for x_pos, y_pos, value, label in point_data:
            # 数据点
            is_high = value > 7.8 or value < 3.9  # 高于或低于正常范围
            point_class = "line-point-high" if is_high else "line-point"
            svg_parts.append(f'  <circle cx="{x_pos}" cy="{y_pos}" r="5" class="{point_class}"/>')
            # 数值标签
            svg_parts.append(f'  <text x="{x_pos}" y="{y_pos - 12}" text-anchor="middle" class="axis-label">{value:.1f}</text>')

        # X轴标签
        for i, label in enumerate(chart.x_labels[:num_points]):
            x_pos = margin_left + (i + 1) * x_step
            svg_parts.append(f'  <text x="{x_pos}" y="{height - margin_bottom + 20}" text-anchor="middle" class="axis-label">{label}</text>')
    else:
        # 柱状图（原有逻辑）
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
        print("Usage: python chart_to_svg.py <output_file.svg> [json_file.json]")
        print("\nOr pipe chart data:")
        print("  cat chart.txt | python chart_to_svg.py output.svg")
        sys.exit(1)

    output_file = sys.argv[1]

    # 如果有第三个参数且是JSON文件，则从文件读取
    text = None
    json_file = None
    if len(sys.argv) > 2:
        # 检查最后一个参数是否是JSON文件（不是以.svg结尾）
        last_arg = sys.argv[-1]
        if last_arg.endswith('.json') and os.path.exists(last_arg):
            json_file = last_arg
        # 如果第二个参数是JSON文件（第三个参数是其他东西）
        elif sys.argv[2].endswith('.json') and os.path.exists(sys.argv[2]):
            json_file = sys.argv[2]

    if json_file:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        text = json.dumps(json_data, ensure_ascii=False)
    else:
        # 从标准输入读取
        if hasattr(sys.stdin, 'buffer'):
            data = sys.stdin.buffer.read()
            text = data.decode('utf-8', errors='replace')
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

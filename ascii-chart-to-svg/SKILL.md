---
name: ascii-chart-to-svg
description: ASCII图表转SVG生成器。解析markdown代码块中的文本格式图表(消费趋势、血糖监测等柱状图),生成高质量SVG矢量图。当用户要求"生成图表SVG"、"转换图表为SVG"、"创建图表图片"或文档中包含ASCII柱状图数据时使用此skill。
---

# ASCII Chart to SVG

将markdown文档中的文本格式图表转换为可缩放的SVG矢量图。

## 使用场景

当文档中包含以下格式的图表时:

- 消费趋势图表(日消费、累计消费)
- 血糖监测图表(空腹血糖、睡前血糖)
- 任何使用█字符表示数据的柱状图/趋势图

示例数据格式:
```
日消费趋势(元):
350 ┤  █
300 ┤
250 ┤              █
200 ┤  █
150 ┤           █
100 ┤
 50 ┤     █  █
  0 ┼─────────────────────────
      5  6  7  8  9  10 11 (日期)
```

## 工作流程

### 1. 提取图表数据

从markdown文档中定位代码块内的图表内容。识别特征:
- 标题行(包含单位)
- Y轴刻度(数值 + ┤)
- 数据标记(█字符)
- X轴底线(┼ + ─)
- X轴标签

### 2. 执行转换

使用bundled script生成SVG:

```bash
python scripts/chart_to_svg.py output.svg < chart_data.txt
```

或通过管道传递数据:

```bash
echo "图表内容" | python scripts/chart_to_svg.py output.svg
```

### 3. 输出选项

- **文件输出**: 保存为.svg文件
- **内联SVG**: 直接嵌入markdown或HTML
- **样式自定义**: 修改脚本中的CSS样式(颜色、字体、尺寸)

## 自定义选项

脚本支持以下参数调整(在`generate_svg`函数中):

- `width`: SVG宽度(默认800px)
- `height`: SVG高度(默认400px)
- 样式: 修改`<style>`块中的CSS类
  - `.bar`: 柱子颜色和样式
  - `.title`: 标题字体
  - `.axis-label`: 轴标签样式

## 注意事项

- 确保图表数据使用UTF-8编码(支持中文字符)
- Y轴刻度必须是数值格式(整数或小数)
- 数据点用█表示,位置对应Y轴刻度
- 如果X轴标签缺失,将自动生成数字序列

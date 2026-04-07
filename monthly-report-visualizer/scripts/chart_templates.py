"""
ECharts 图表模板
为月度报表生成各种图表的 HTML 模板
"""

# 睡眠质量分布图模板
SLEEP_CHART_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>睡眠质量分布</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        .container {{
            width: 800px;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            padding: 40px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }}
        h1 {{
            color: #fff;
            text-align: center;
            margin-bottom: 10px;
            font-size: 24px;
        }}
        .subtitle {{
            color: rgba(255,255,255,0.6);
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }}
        #chart {{
            width: 100%;
            height: 400px;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin-top: 30px;
        }}
        .stat-item {{
            text-align: center;
            color: #fff;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
        }}
        .stat-label {{
            font-size: 12px;
            color: rgba(255,255,255,0.6);
            margin-top: 5px;
        }}
        .good {{ color: #27ae60; }}
        .average {{ color: #f39c12; }}
        .bad {{ color: #e74c3c; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>😴 睡眠质量分布</h1>
        <p class="subtitle">{year}年{month}月 | 总计{total_days}天 | 良好睡眠率: {good_rate}%</p>
        <div id="chart"></div>
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value bad">{bad_days}天</div>
                <div class="stat-label">睡眠差</div>
            </div>
            <div class="stat-item">
                <div class="stat-value average">{average_days}天</div>
                <div class="stat-label">睡眠一般</div>
            </div>
            <div class="stat-item">
                <div class="stat-value good">{good_days}天</div>
                <div class="stat-label">睡眠好</div>
            </div>
        </div>
    </div>
    <script>
        const chart = echarts.init(document.getElementById('chart'));
        chart.setOption({{
            tooltip: {{
                trigger: 'item',
                formatter: '{{b}}: {{c}}天 ({{d}}%)',
                backgroundColor: 'rgba(0,0,0,0.8)',
                borderColor: '#333',
                textStyle: {{ color: '#fff' }}
            }},
            series: [{{
                type: 'pie',
                radius: ['50%', '75%'],
                center: ['50%', '50%'],
                avoidLabelOverlap: true,
                itemStyle: {{
                    borderRadius: 15,
                    borderColor: '#1a1a2e',
                    borderWidth: 5
                }},
                label: {{
                    show: true,
                    color: '#fff',
                    fontSize: 14,
                    formatter: '{{b}}\n{{c}}天 ({{d}}%)'
                }},
                labelLine: {{
                    lineStyle: {{ color: 'rgba(255,255,255,0.3)' }}
                }},
                data: [
                    {{ value: {bad_days}, name: '差', itemStyle: {{ color: '#e74c3c' }} }},
                    {{ value: {average_days}, name: '一般', itemStyle: {{ color: '#f39c12' }} }},
                    {{ value: {good_days}, name: '好', itemStyle: {{ color: '#27ae60' }} }}
                ]
            }}]
        }});
    </script>
</body>
</html>
'''

# 血糖监测分析图模板
BLOOD_SUGAR_CHART_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>血糖监测分析</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        .container {{
            width: 900px;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            padding: 40px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }}
        h1 {{
            color: #fff;
            text-align: center;
            margin-bottom: 10px;
            font-size: 24px;
        }}
        .subtitle {{
            color: rgba(255,255,255,0.6);
            text-align: center;
            margin-bottom: 20px;
            font-size: 14px;
        }}
        #chart {{
            width: 100%;
            height: 400px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-top: 20px;
        }}
        .info-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            color: #fff;
        }}
        .info-title {{
            font-size: 14px;
            color: rgba(255,255,255,0.6);
            margin-bottom: 10px;
        }}
        .info-value {{
            font-size: 24px;
            font-weight: bold;
        }}
        .warning {{ color: #e74c3c; }}
        .success {{ color: #27ae60; }}
        .info {{ color: #3498db; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🩸 血糖监测分析</h1>
        <p class="subtitle">{year}年{month}月 | 正常范围: 空腹 3.9-6.1 mmol/L | 餐后 4.4-7.8 mmol/L</p>
        <div id="chart"></div>
        <div class="info-grid">
            <div class="info-card">
                <div class="info-title">空腹血糖平均值</div>
                <div class="info-value {fasting_class}">{fasting_avg} mmol/L</div>
            </div>
            <div class="info-card">
                <div class="info-title">空腹血糖达标率</div>
                <div class="info-value {fasting_rate_class}">{fasting_rate}%</div>
            </div>
            <div class="info-card">
                <div class="info-title">餐后2h血糖平均值</div>
                <div class="info-value {postprandial_class}">{postprandial_avg} mmol/L</div>
            </div>
            <div class="info-card">
                <div class="info-title">餐后血糖达标率</div>
                <div class="info-value {postprandial_rate_class}">{postprandial_rate}%</div>
            </div>
        </div>
    </div>
    <script>
        const chart = echarts.init(document.getElementById('chart'));
        chart.setOption({{
            tooltip: {{
                trigger: 'axis',
                axisPointer: {{ type: 'shadow' }},
                backgroundColor: 'rgba(0,0,0,0.8)',
                borderColor: '#333',
                textStyle: {{ color: '#fff' }}
            }},
            legend: {{
                data: ['平均值', '最小值', '最大值', '正常上限'],
                textStyle: {{ color: '#fff' }},
                top: 10
            }},
            grid: {{
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            }},
            xAxis: {{
                type: 'category',
                data: ['空腹血糖', '餐后2h血糖'],
                axisLine: {{ lineStyle: {{ color: 'rgba(255,255,255,0.3)' }} }},
                axisLabel: {{ color: '#fff', fontSize: 14 }}
            }},
            yAxis: {{
                type: 'value',
                name: 'mmol/L',
                nameTextStyle: {{ color: '#fff' }},
                max: 12,
                axisLine: {{ lineStyle: {{ color: 'rgba(255,255,255,0.3)' }} }},
                axisLabel: {{ color: '#fff' }},
                splitLine: {{ lineStyle: {{ color: 'rgba(255,255,255,0.1)' }} }}
            }},
            series: [
                {{
                    name: '平均值',
                    type: 'bar',
                    data: [{fasting_avg}, {postprandial_avg}],
                    itemStyle: {{ color: '#3498db', borderRadius: [8, 8, 0, 0] }},
                    label: {{ show: true, position: 'top', color: '#fff', fontSize: 12, formatter: '{{c}}' }}
                }},
                {{
                    name: '最小值',
                    type: 'bar',
                    data: [{fasting_min}, {postprandial_min}],
                    itemStyle: {{ color: '#27ae60', borderRadius: [8, 8, 0, 0] }}
                }},
                {{
                    name: '最大值',
                    type: 'bar',
                    data: [{fasting_max}, {postprandial_max}],
                    itemStyle: {{ color: '#e74c3c', borderRadius: [8, 8, 0, 0] }}
                }},
                {{
                    name: '正常上限',
                    type: 'line',
                    data: [6.1, 7.8],
                    lineStyle: {{ color: '#f1c40f', type: 'dashed', width: 3 }},
                    symbol: 'circle',
                    symbolSize: 10,
                    itemStyle: {{ color: '#f1c40f' }}
                }}
            ]
        }});
    </script>
</body>
</html>
'''

# 消费趋势分析图模板
SPENDING_CHART_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>消费趋势分析</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        .container {{
            width: 900px;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            padding: 40px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }}
        h1 {{
            color: #fff;
            text-align: center;
            margin-bottom: 10px;
            font-size: 24px;
        }}
        .subtitle {{
            color: rgba(255,255,255,0.6);
            text-align: center;
            margin-bottom: 20px;
            font-size: 14px;
        }}
        #chart {{
            width: 100%;
            height: 350px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-top: 30px;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            color: #fff;
        }}
        .stat-icon {{
            font-size: 24px;
            margin-bottom: 10px;
        }}
        .stat-value {{
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 12px;
            color: rgba(255,255,255,0.7);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>💰 消费趋势分析</h1>
        <p class="subtitle">{year}年{month}月 | 主要消费类别: {top_category}</p>
        <div id="chart"></div>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">💳</div>
                <div class="stat-value">¥{total_spending:.2f}</div>
                <div class="stat-label">总支出</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-value">¥{daily_avg:.2f}</div>
                <div class="stat-label">日均消费</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📝</div>
                <div class="stat-value">{transaction_count}笔</div>
                <div class="stat-label">消费笔数</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📈</div>
                <div class="stat-value">¥{max_daily:.2f}</div>
                <div class="stat-label">单日最高</div>
            </div>
        </div>
    </div>
    <script>
        const chart = echarts.init(document.getElementById('chart'));
        chart.setOption({{
            tooltip: {{
                trigger: 'item',
                formatter: '{{b}}: {{c}}元 ({{d}}%)',
                backgroundColor: 'rgba(0,0,0,0.8)',
                borderColor: '#333',
                textStyle: {{ color: '#fff' }}
            }},
            legend: {{
                orient: 'vertical',
                left: 'left',
                textStyle: {{ color: '#fff', fontSize: 12 }},
                top: 'center'
            }},
            series: [{{
                type: 'pie',
                radius: ['40%', '70%'],
                center: ['60%', '50%'],
                avoidLabelOverlap: false,
                itemStyle: {{
                    borderRadius: 10,
                    borderColor: '#1e3c72',
                    borderWidth: 5
                }},
                label: {{
                    show: true,
                    color: '#fff',
                    fontSize: 12,
                    formatter: '{{b}}\n{{d}}%'
                }},
                labelLine: {{
                    lineStyle: {{ color: 'rgba(255,255,255,0.3)' }}
                }},
                data: [
                    {{ value: {food_amount}, name: '餐饮', itemStyle: {{ color: '#e74c3c' }} }},
                    {{ value: {shopping_amount}, name: '购物', itemStyle: {{ color: '#3498db' }} }},
                    {{ value: {transport_amount}, name: '交通', itemStyle: {{ color: '#9b59b6' }} }},
                    {{ value: {entertainment_amount}, name: '娱乐', itemStyle: {{ color: '#f39c12' }} }},
                    {{ value: {other_amount}, name: '其他', itemStyle: {{ color: '#1abc9c' }} }}
                ]
            }}]
        }});
    </script>
</body>
</html>
'''

# OKR完成情况图模板
OKR_CHART_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OKR完成情况</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        .container {{
            width: 900px;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            padding: 40px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }}
        h1 {{
            color: #fff;
            text-align: center;
            margin-bottom: 10px;
            font-size: 24px;
        }}
        .subtitle {{
            color: rgba(255,255,255,0.6);
            text-align: center;
            margin-bottom: 20px;
            font-size: 14px;
        }}
        .charts-wrapper {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }}
        .chart-box {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
        }}
        .chart-title {{
            color: #fff;
            font-size: 14px;
            margin-bottom: 15px;
            text-align: center;
        }}
        .chart-container {{
            width: 100%;
            height: 250px;
        }}
        .stats-row {{
            display: flex;
            justify-content: space-around;
            margin-top: 30px;
        }}
        .stat-box {{
            text-align: center;
            color: #fff;
            padding: 15px 25px;
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
        }}
        .stat-number {{
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 12px;
            color: rgba(255,255,255,0.7);
        }}
        .warning {{ color: #e74c3c; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 OKR完成情况</h1>
        <p class="subtitle">{year}年{month}月 | 总计{total_tasks}项任务 | 整体完成率{overall_rate}%</p>
        <div class="charts-wrapper">
            <div class="chart-box">
                <div class="chart-title">任务类型完成情况</div>
                <div id="taskChart" class="chart-container"></div>
            </div>
            <div class="chart-box">
                <div class="chart-title">KR按优先级完成率</div>
                <div id="priorityChart" class="chart-container"></div>
            </div>
        </div>
        <div class="stats-row">
            <div class="stat-box">
                <div class="stat-number">{todo_completed}/{todo_total}</div>
                <div class="stat-label">今日待办 ({todo_rate}%)</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{kr_completed}/{kr_total}</div>
                <div class="stat-label">关键结果KR ({kr_rate}%)</div>
            </div>
            <div class="stat-box">
                <div class="stat-number warning">{p0_pending}</div>
                <div class="stat-label">P0未完成 ⚠️</div>
            </div>
        </div>
    </div>
    <script>
        // 任务类型完成情况
        const taskChart = echarts.init(document.getElementById('taskChart'));
        taskChart.setOption({{
            tooltip: {{
                trigger: 'axis',
                axisPointer: {{ type: 'shadow' }},
                backgroundColor: 'rgba(0,0,0,0.8)',
                borderColor: '#333',
                textStyle: {{ color: '#fff' }}
            }},
            legend: {{
                data: ['总数', '已完成'],
                textStyle: {{ color: '#fff' }},
                top: 5
            }},
            grid: {{
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            }},
            xAxis: {{
                type: 'category',
                data: ['今日待办', '临时任务', '关键结果'],
                axisLine: {{ lineStyle: {{ color: 'rgba(255,255,255,0.3)' }} }},
                axisLabel: {{ color: '#fff', fontSize: 11 }}
            }},
            yAxis: {{
                type: 'value',
                axisLine: {{ lineStyle: {{ color: 'rgba(255,255,255,0.3)' }} }},
                axisLabel: {{ color: '#fff' }},
                splitLine: {{ lineStyle: {{ color: 'rgba(255,255,255,0.1)' }} }}
            }},
            series: [
                {{
                    name: '总数',
                    type: 'bar',
                    data: [{todo_total}, {temp_total}, {kr_total}],
                    itemStyle: {{ color: 'rgba(255,255,255,0.3)', borderRadius: [6, 6, 0, 0] }}
                }},
                {{
                    name: '已完成',
                    type: 'bar',
                    data: [{todo_completed}, {temp_completed}, {kr_completed}],
                    itemStyle: {{ color: '#27ae60', borderRadius: [6, 6, 0, 0] }},
                    label: {{
                        show: true,
                        position: 'top',
                        color: '#fff',
                        fontSize: 10,
                        formatter: function(params) {{
                            const rates = ['{todo_rate}%', '{temp_rate}%', '{kr_rate}%'];
                            return rates[params.dataIndex];
                        }}
                    }}
                }}
            ]
        }});

        // 优先级完成率
        const priorityChart = echarts.init(document.getElementById('priorityChart'));
        priorityChart.setOption({{
            tooltip: {{
                trigger: 'axis',
                backgroundColor: 'rgba(0,0,0,0.8)',
                borderColor: '#333',
                textStyle: {{ color: '#fff' }},
                formatter: '{{b}}: {{c}}% 完成率'
            }},
            grid: {{
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            }},
            xAxis: {{
                type: 'category',
                data: ['P0(最高)', 'P1(高)', 'P2(中)'],
                axisLine: {{ lineStyle: {{ color: 'rgba(255,255,255,0.3)' }} }},
                axisLabel: {{ color: '#fff' }}
            }},
            yAxis: {{
                type: 'value',
                max: 100,
                axisLine: {{ lineStyle: {{ color: 'rgba(255,255,255,0.3)' }} }},
                axisLabel: {{ color: '#fff', formatter: '{{value}}%' }},
                splitLine: {{ lineStyle: {{ color: 'rgba(255,255,255,0.1)' }} }}
            }},
            series: [{{
                type: 'bar',
                data: [
                    {{ value: {p0_rate}, itemStyle: {{ color: '#e74c3c' }} }},
                    {{ value: {p1_rate}, itemStyle: {{ color: '#f39c12' }} }},
                    {{ value: {p2_rate}, itemStyle: {{ color: '#3498db' }} }}
                ],
                barWidth: '50%',
                itemStyle: {{ borderRadius: [8, 8, 0, 0] }},
                label: {{
                    show: true,
                    position: 'top',
                    color: '#fff',
                    fontSize: 12,
                    fontWeight: 'bold',
                    formatter: '{{c}}%'
                }}
            }}]
        }});
    </script>
</body>
</html>
'''

# 综合数据看板模板
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{year}年{month}月统计报表 - 数据可视化</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }}
        .dashboard {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            color: white;
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 14px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        }}
        .card-title {{
            font-size: 16px;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }}
        .chart-container {{
            width: 100%;
            height: 300px;
        }}
        .summary-card {{
            grid-column: span 2;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }}
        .summary-card .card-title {{
            color: white;
            border-bottom-color: rgba(255,255,255,0.3);
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-top: 15px;
        }}
        .summary-item {{
            text-align: center;
            padding: 15px;
            background: rgba(255,255,255,0.2);
            border-radius: 8px;
        }}
        .summary-item .value {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .summary-item .label {{
            font-size: 12px;
            opacity: 0.9;
        }}
        .insights {{
            grid-column: span 2;
        }}
        .insights-content {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }}
        .insight-section h4 {{
            color: #e74c3c;
            font-size: 14px;
            margin-bottom: 10px;
        }}
        .insight-section ul {{
            list-style: none;
            font-size: 12px;
            color: #666;
        }}
        .insight-section li {{
            margin-bottom: 5px;
            padding-left: 15px;
            position: relative;
        }}
        .insight-section li::before {{
            content: '•';
            position: absolute;
            left: 0;
            color: #e74c3c;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>📊 {year}年{month}月统计报表</h1>
            <p>统计周期: {year}年{month}月 | 记录天数: {total_days}天 | 生成时间: {generate_time}</p>
        </div>

        <div class="grid">
            <!-- 摘要卡片 -->
            <div class="card summary-card">
                <div class="card-title">📈 核心指标概览</div>
                <div class="summary-grid">
                    <div class="summary-item">
                        <div class="value">{sleep_good_rate}%</div>
                        <div class="label">良好睡眠率</div>
                    </div>
                    <div class="summary-item">
                        <div class="value">{blood_sugar_rate}%</div>
                        <div class="label">血糖达标率</div>
                    </div>
                    <div class="summary-item">
                        <div class="value">¥{total_spending:,}</div>
                        <div class="label">月度总支出</div>
                    </div>
                    <div class="summary-item">
                        <div class="value">{kr_completion_rate}%</div>
                        <div class="label">KR完成率</div>
                    </div>
                </div>
            </div>

            <!-- 睡眠质量分布 -->
            <div class="card">
                <div class="card-title">😴 睡眠质量分布</div>
                <div id="sleepChart" class="chart-container"></div>
            </div>

            <!-- 血糖监测分析 -->
            <div class="card">
                <div class="card-title">🩸 血糖监测分析</div>
                <div id="bloodSugarChart" class="chart-container"></div>
            </div>

            <!-- 消费趋势 -->
            <div class="card">
                <div class="card-title">💰 消费趋势分析</div>
                <div id="spendingChart" class="chart-container"></div>
            </div>

            <!-- OKR完成情况 -->
            <div class="card">
                <div class="card-title">🎯 OKR完成情况</div>
                <div id="okrChart" class="chart-container"></div>
            </div>

            <!-- 建议与总结 -->
            <div class="card insights">
                <div class="card-title">💡 建议与总结</div>
                <div class="insights-content">
                    <div class="insight-section">
                        <h4>健康建议</h4>
                        <ul>
                            <li>睡眠质量需要改善，{sleep_bad_days}天睡眠较差</li>
                            <li>建议调整作息时间</li>
                            <li>空腹血糖偏高，控制晚餐</li>
                            <li>减少碳水化合物摄入</li>
                        </ul>
                    </div>
                    <div class="insight-section">
                        <h4>消费建议</h4>
                        <ul>
                            <li>日均消费¥{daily_avg}，建议控制</li>
                            <li>主要消费为{top_category}类别</li>
                            <li>关注餐饮支出优化</li>
                            <li>本月总支出¥{total_spending}</li>
                        </ul>
                    </div>
                    <div class="insight-section">
                        <h4>OKR建议</h4>
                        <ul>
                            <li>今日待办完成率{todo_rate}%，需改善</li>
                            <li>合理规划每日任务量</li>
                            <li>{p0_pending}个P0级KR未完成</li>
                            <li>优先处理高优先级任务</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 睡眠质量分布饼图
        const sleepChart = echarts.init(document.getElementById('sleepChart'));
        sleepChart.setOption({{
            tooltip: {{ trigger: 'item', formatter: '{{b}}: {{c}}天 ({{d}}%)' }},
            legend: {{ bottom: '5%', left: 'center' }},
            series: [{{
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: {{ borderRadius: 10, borderColor: '#fff', borderWidth: 2 }},
                label: {{ show: true, formatter: '{{b}}\n{{c}}天' }},
                data: [
                    {{ value: {sleep_bad_days}, name: '差', itemStyle: {{ color: '#e74c3c' }} }},
                    {{ value: {sleep_average_days}, name: '一般', itemStyle: {{ color: '#f39c12' }} }},
                    {{ value: {sleep_good_days}, name: '好', itemStyle: {{ color: '#27ae60' }} }}
                ]
            }}]
        }});

        // 血糖监测分析柱状图
        const bloodSugarChart = echarts.init(document.getElementById('bloodSugarChart'));
        bloodSugarChart.setOption({{
            tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }} }},
            legend: {{ data: ['平均值', '最小值', '最大值', '正常上限'] }},
            grid: {{ left: '3%', right: '4%', bottom: '3%', containLabel: true }},
            xAxis: {{ type: 'category', data: ['空腹血糖', '餐后2h血糖'] }},
            yAxis: {{ type: 'value', name: 'mmol/L', max: 12 }},
            series: [
                {{
                    name: '平均值',
                    type: 'bar',
                    data: [{fasting_avg}, {postprandial_avg}],
                    itemStyle: {{ color: '#3498db' }},
                    label: {{ show: true, position: 'top', formatter: '{{c}}' }}
                }},
                {{
                    name: '最小值',
                    type: 'bar',
                    data: [{fasting_min}, {postprandial_min}],
                    itemStyle: {{ color: '#2ecc71' }}
                }},
                {{
                    name: '最大值',
                    type: 'bar',
                    data: [{fasting_max}, {postprandial_max}],
                    itemStyle: {{ color: '#e74c3c' }}
                }},
                {{
                    name: '正常上限',
                    type: 'line',
                    data: [6.1, 7.8],
                    lineStyle: {{ color: '#27ae60', type: 'dashed', width: 2 }},
                    symbol: 'circle',
                    symbolSize: 8
                }}
            ]
        }});

        // 消费趋势分析
        const spendingChart = echarts.init(document.getElementById('spendingChart'));
        spendingChart.setOption({{
            tooltip: {{ trigger: 'item', formatter: '{{b}}: {{c}}元 ({{d}}%)' }},
            legend: {{ bottom: '5%', left: 'center' }},
            series: [{{
                type: 'pie',
                radius: '60%',
                data: [
                    {{ value: {food_amount}, name: '餐饮', itemStyle: {{ color: '#e74c3c' }} }},
                    {{ value: {shopping_amount}, name: '购物', itemStyle: {{ color: '#3498db' }} }},
                    {{ value: {transport_amount}, name: '交通', itemStyle: {{ color: '#9b59b6' }} }},
                    {{ value: {entertainment_amount}, name: '娱乐', itemStyle: {{ color: '#f39c12' }} }},
                    {{ value: {other_amount}, name: '其他', itemStyle: {{ color: '#1abc9c' }} }}
                ],
                label: {{ formatter: '{{b}}\n{{d}}%' }},
                emphasis: {{
                    itemStyle: {{ shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.5)' }}
                }}
            }}]
        }});

        // OKR完成情况
        const okrChart = echarts.init(document.getElementById('okrChart'));
        okrChart.setOption({{
            tooltip: {{ trigger: 'axis', axisPointer: {{ type: 'shadow' }} }},
            legend: {{ data: ['总数', '已完成'] }},
            grid: {{ left: '3%', right: '4%', bottom: '3%', containLabel: true }},
            xAxis: {{
                type: 'category',
                data: ['今日待办', '临时任务', '关键结果(KR)', 'P0优先级', 'P1优先级', 'P2优先级']
            }},
            yAxis: {{ type: 'value', name: '数量' }},
            series: [
                {{
                    name: '总数',
                    type: 'bar',
                    data: [{todo_total}, {temp_total}, {kr_total}, {p0_total}, {p1_total}, {p2_total}],
                    itemStyle: {{ color: '#95a5a6' }}
                }},
                {{
                    name: '已完成',
                    type: 'bar',
                    data: [{todo_completed}, {temp_completed}, {kr_completed}, {p0_completed}, {p1_completed}, {p2_completed}],
                    itemStyle: {{ color: '#27ae60' }},
                    label: {{
                        show: true,
                        position: 'top',
                        formatter: function(params) {{
                            const rates = ['{todo_rate}%', '{temp_rate}%', '{kr_rate}%', '{p0_rate}%', '{p1_rate}%', '{p2_rate}%'];
                            return rates[params.dataIndex];
                        }},
                        fontSize: 11,
                        color: '#27ae60',
                        fontWeight: 'bold'
                    }}
                }}
            ]
        }});

        // 响应式调整
        window.addEventListener('resize', function() {{
            sleepChart.resize();
            bloodSugarChart.resize();
            spendingChart.resize();
            okrChart.resize();
        }});
    </script>
</body>
</html>
'''

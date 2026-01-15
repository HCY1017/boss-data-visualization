"""
可视化模块
负责创建和导出图表
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Union
import pandas as pd
from datetime import datetime


def create_line_chart(
    dates: List[Union[datetime, pd.Timestamp]],
    user1_values: List[Union[int, float, None]],
    user2_values: List[Union[int, float, None]],
    user1_name: str,
    user2_name: str,
    metric_name: str,
    date_range: str
) -> go.Figure:
    """
    创建双用户对比折线图
    
    Args:
        dates: 日期列表
        user1_values: 用户1的数值列表
        user2_values: 用户2的数值列表
        user1_name: 用户1姓名
        user2_name: 用户2姓名
        metric_name: 指标名称
        date_range: 日期范围字符串
        
    Returns:
        Plotly Figure对象
    """
    fig = go.Figure()
    
    # 添加用户1曲线（蓝色）
    fig.add_trace(go.Scatter(
        x=dates,
        y=user1_values,
        name=user1_name,
        mode='lines+markers',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=6),
        connectgaps=False  # 不连接缺失值
    ))
    
    # 添加用户2曲线（橙色）
    fig.add_trace(go.Scatter(
        x=dates,
        y=user2_values,
        name=user2_name,
        mode='lines+markers',
        line=dict(color='#ff7f0e', width=2),
        marker=dict(size=6),
        connectgaps=False  # 不连接缺失值
    ))
    
    # 配置布局
    fig.update_layout(
        title=f'{date_range} {user1_name} vs {user2_name} - {metric_name}趋势',
        xaxis=dict(
            title='日期',
            gridcolor='#E5E5E5',
            showgrid=True
        ),
        yaxis=dict(
            title=metric_name,
            gridcolor='#E5E5E5',
            showgrid=True
        ),
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='top',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        height=500,
        plot_bgcolor='white',
        margin=dict(t=80)  # 增加顶部边距以容纳图例
    )
    
    return fig


def export_chart(fig: go.Figure, filename: str, format: str) -> None:
    """
    导出图表为文件
    
    Args:
        fig: Plotly Figure对象
        filename: 输出文件名
        format: 导出格式 ('PNG', 'PDF', 'HTML')
        
    Raises:
        ValueError: 当格式不支持时
    """
    format = format.upper()
    
    if format == 'PNG':
        fig.write_image(filename, width=1200, height=600, scale=2)
    elif format == 'PDF':
        fig.write_image(filename, width=1200, height=600)
    elif format == 'HTML':
        fig.write_html(filename)
    else:
        raise ValueError(f"不支持的导出格式: {format}。支持的格式: PNG, PDF, HTML")


def create_conversion_chart(
    df: pd.DataFrame,
    user1_name: str,
    user2_name: str,
    date_range: str
) -> go.Figure:
    """
    创建转化率对比图表
    
    Args:
        df: 包含date, user1_conversion_rate, user2_conversion_rate列的数据框
        user1_name: 用户1姓名
        user2_name: 用户2姓名
        date_range: 日期范围字符串
        
    Returns:
        Plotly Figure对象
    """
    fig = go.Figure()
    
    # 添加用户1转化率曲线
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['user1_conversion_rate'],
        name=user1_name,
        mode='lines+markers',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=6),
        connectgaps=False
    ))
    
    # 添加用户2转化率曲线
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['user2_conversion_rate'],
        name=user2_name,
        mode='lines+markers',
        line=dict(color='#ff7f0e', width=2),
        marker=dict(size=6),
        connectgaps=False
    ))
    
    # 配置布局
    fig.update_layout(
        title=f'{date_range} {user1_name} vs {user2_name} - 添加微信转化率趋势',
        xaxis=dict(
            title='日期',
            gridcolor='#E5E5E5',
            showgrid=True
        ),
        yaxis=dict(
            title='转化率 (%)',
            gridcolor='#E5E5E5',
            showgrid=True,
            range=[0, 100]  # 转化率范围0-100%
        ),
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='top',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        height=500,
        plot_bgcolor='white',
        margin=dict(t=80)  # 增加顶部边距以容纳图例
    )
    
    return fig


def create_dual_metric_chart(
    dates: List[Union[datetime, pd.Timestamp]],
    metric1_user1_values: List[Union[int, float, None]],
    metric1_user2_values: List[Union[int, float, None]],
    metric2_user1_values: List[Union[int, float, None]],
    metric2_user2_values: List[Union[int, float, None]],
    user1_name: str,
    user2_name: str,
    metric1_name: str,
    metric2_name: str,
    date_range: str
) -> go.Figure:
    """
    创建双指标对比图表（使用双Y轴）
    
    Args:
        dates: 日期列表
        metric1_user1_values: 指标1用户1的数值列表
        metric1_user2_values: 指标1用户2的数值列表
        metric2_user1_values: 指标2用户1的数值列表
        metric2_user2_values: 指标2用户2的数值列表
        user1_name: 用户1姓名
        user2_name: 用户2姓名
        metric1_name: 指标1名称
        metric2_name: 指标2名称
        date_range: 日期范围字符串
        
    Returns:
        Plotly Figure对象（带双Y轴）
    """
    # 创建带双Y轴的图表
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 添加指标1的曲线（左Y轴）
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=metric1_user1_values,
            name=f"{user1_name} - {metric1_name}",
            mode='lines+markers',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=6),
            connectgaps=False
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=metric1_user2_values,
            name=f"{user2_name} - {metric1_name}",
            mode='lines+markers',
            line=dict(color='#ff7f0e', width=2),
            marker=dict(size=6),
            connectgaps=False
        ),
        secondary_y=False
    )
    
    # 添加指标2的曲线（右Y轴）
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=metric2_user1_values,
            name=f"{user1_name} - {metric2_name}",
            mode='lines+markers',
            line=dict(color='#2ca02c', width=2, dash='dash'),
            marker=dict(size=6, symbol='diamond'),
            connectgaps=False
        ),
        secondary_y=True
    )
    
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=metric2_user2_values,
            name=f"{user2_name} - {metric2_name}",
            mode='lines+markers',
            line=dict(color='#d62728', width=2, dash='dash'),
            marker=dict(size=6, symbol='diamond'),
            connectgaps=False
        ),
        secondary_y=True
    )
    
    # 配置布局
    fig.update_xaxes(
        title_text='日期',
        gridcolor='#E5E5E5',
        showgrid=True
    )
    
    # 左Y轴（指标1）
    fig.update_yaxes(
        title_text=metric1_name,
        gridcolor='#E5E5E5',
        showgrid=True,
        secondary_y=False
    )
    
    # 右Y轴（指标2）
    fig.update_yaxes(
        title_text=metric2_name,
        gridcolor='#E5E5E5',
        showgrid=False,
        secondary_y=True
    )
    
    fig.update_layout(
        title=f'{date_range} {user1_name} vs {user2_name} - {metric1_name} vs {metric2_name} 对比',
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='top',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        height=500,
        plot_bgcolor='white',
        margin=dict(t=80)
    )
    
    return fig

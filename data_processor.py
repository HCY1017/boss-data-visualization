"""
数据处理模块
负责数据筛选、转化率计算和指标提取
"""
import pandas as pd
from typing import Tuple, List, Dict
import numpy as np


def filter_by_date_range(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """
    根据日期范围筛选数据
    
    Args:
        df: 包含date列的数据框
        start_date: 起始日期 (YYYY-MM-DD格式字符串)
        end_date: 结束日期 (YYYY-MM-DD格式字符串)
        
    Returns:
        筛选后的DataFrame
    """
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)
    
    # 确保date列是datetime类型
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
    
    # 筛选日期范围
    mask = (df['date'] >= start_dt) & (df['date'] <= end_dt)
    filtered_df = df[mask].copy()
    
    return filtered_df.reset_index(drop=True)


def calculate_conversion_rates(df: pd.DataFrame) -> pd.DataFrame:
    """
    计算转化率指标
    
    计算公式：
    - 添加微信转化率 = (添加微信 / 交换微信) × 100%
    
    Args:
        df: 包含user1_add, user1_exchange, user2_add, user2_exchange列的数据框
        
    Returns:
        包含转化率列的新DataFrame（添加user1_conversion_rate和user2_conversion_rate列）
    """
    result_df = df.copy()
    
    # 计算用户1转化率
    result_df['user1_conversion_rate'] = (
        result_df['user1_add'].div(result_df['user1_exchange']) * 100
    )
    
    # 计算用户2转化率
    result_df['user2_conversion_rate'] = (
        result_df['user2_add'].div(result_df['user2_exchange']) * 100
    )
    
    # 当分母为0或NaN时，结果已经是NaN，无需额外处理
    
    return result_df


def get_metric_data(df: pd.DataFrame, metric: str) -> Tuple[List, List, List]:
    """
    提取指定指标的两位用户数据
    
    Args:
        df: 数据框
        metric: 指标名称 ('曝光', '新招呼', '交换微信', '添加微信')
        
    Returns:
        tuple: (dates, user1_values, user2_values)
        - dates: 日期列表
        - user1_values: 用户1的数值列表
        - user2_values: 用户2的数值列表
        
    Raises:
        ValueError: 当指标名称无效时
    """
    metric_mapping = {
        '曝光': ('user1_exposure', 'user2_exposure'),
        '新招呼': ('user1_greet', 'user2_greet'),
        '交换微信': ('user1_exchange', 'user2_exchange'),
        '添加微信': ('user1_add', 'user2_add'),
        '补刀次数': ('user1_kill', 'user2_kill')
    }
    
    if metric not in metric_mapping:
        raise ValueError(f"无效的指标名称: {metric}。支持的指标: {list(metric_mapping.keys())}")
    
    user1_col, user2_col = metric_mapping[metric]
    
    dates = df['date'].tolist()
    user1_values = df[user1_col].tolist()
    user2_values = df[user2_col].tolist()
    
    return dates, user1_values, user2_values


def calculate_statistics(df: pd.DataFrame, metric: str) -> Dict:
    """
    计算统计数据
    
    Args:
        df: 数据框
        metric: 指标名称
        
    Returns:
        包含统计信息的字典:
        {
            'user1': {'mean': float, 'max': float, 'min': float, 'sum': float},
            'user2': {'mean': float, 'max': float, 'min': float, 'sum': float}
        }
    """
    metric_mapping = {
        '曝光': ('user1_exposure', 'user2_exposure'),
        '新招呼': ('user1_greet', 'user2_greet'),
        '交换微信': ('user1_exchange', 'user2_exchange'),
        '添加微信': ('user1_add', 'user2_add'),
        '补刀次数': ('user1_kill', 'user2_kill')
    }
    
    if metric not in metric_mapping:
        raise ValueError(f"无效的指标名称: {metric}")
    
    user1_col, user2_col = metric_mapping[metric]
    
    stats = {
        'user1': {
            'mean': df[user1_col].mean(),
            'max': df[user1_col].max(),
            'min': df[user1_col].min(),
            'sum': df[user1_col].sum()
        },
        'user2': {
            'mean': df[user2_col].mean(),
            'max': df[user2_col].max(),
            'min': df[user2_col].min(),
            'sum': df[user2_col].sum()
        }
    }
    
    return stats


def get_dual_metric_data(df: pd.DataFrame, metric1: str, metric2: str) -> Tuple[List, List, List, List, List]:
    """
    提取两个指标的两位用户数据
    
    Args:
        df: 数据框
        metric1: 指标1名称 ('曝光', '新招呼', '交换微信', '添加微信', '补刀次数')
        metric2: 指标2名称 ('曝光', '新招呼', '交换微信', '添加微信', '补刀次数')
        
    Returns:
        tuple: (dates, metric1_user1_values, metric1_user2_values, metric2_user1_values, metric2_user2_values)
        - dates: 日期列表
        - metric1_user1_values: 指标1用户1的数值列表
        - metric1_user2_values: 指标1用户2的数值列表
        - metric2_user1_values: 指标2用户1的数值列表
        - metric2_user2_values: 指标2用户2的数值列表
        
    Raises:
        ValueError: 当指标名称无效时
    """
    metric_mapping = {
        '曝光': ('user1_exposure', 'user2_exposure'),
        '新招呼': ('user1_greet', 'user2_greet'),
        '交换微信': ('user1_exchange', 'user2_exchange'),
        '添加微信': ('user1_add', 'user2_add'),
        '补刀次数': ('user1_kill', 'user2_kill')
    }
    
    if metric1 not in metric_mapping:
        raise ValueError(f"无效的指标1名称: {metric1}。支持的指标: {list(metric_mapping.keys())}")
    if metric2 not in metric_mapping:
        raise ValueError(f"无效的指标2名称: {metric2}。支持的指标: {list(metric_mapping.keys())}")
    
    metric1_user1_col, metric1_user2_col = metric_mapping[metric1]
    metric2_user1_col, metric2_user2_col = metric_mapping[metric2]
    
    dates = df['date'].tolist()
    metric1_user1_values = df[metric1_user1_col].tolist()
    metric1_user2_values = df[metric1_user2_col].tolist()
    metric2_user1_values = df[metric2_user1_col].tolist()
    metric2_user2_values = df[metric2_user2_col].tolist()
    
    return dates, metric1_user1_values, metric1_user2_values, metric2_user1_values, metric2_user2_values

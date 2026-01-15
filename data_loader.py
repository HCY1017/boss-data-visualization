"""
数据加载模块
负责从Excel文件读取数据并转换为标准格式
"""
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, Dict


def convert_excel_date(excel_date: float) -> datetime:
    """
    将Excel日期序列号转换为Python datetime对象
    
    Excel使用1900年1月1日作为基准日期（序列号1），但实际是1899年12月30日
    公式: datetime(1899, 12, 30) + timedelta(days=excel_date)
    
    Args:
        excel_date: Excel日期序列号（如 45957）
        
    Returns:
        datetime对象
        
    Raises:
        ValueError: 当输入无效时
    """
    if not isinstance(excel_date, (int, float)):
        raise ValueError(f"无效的日期值: {excel_date}")
    
    if excel_date < 0:
        raise ValueError(f"日期序列号不能为负数: {excel_date}")
    
    base_date = datetime(1899, 12, 30)
    return base_date + timedelta(days=int(excel_date))


def load_excel_data(file_path: str) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    读取Excel文件并转换为标准DataFrame，同时提取用户名
    
    Excel文件结构：
    - 第一列：日期（Excel序列号）
    - 第2-5列：用户1的数据（曝光、新招呼、交换微信、添加微信）
    - 第6-9列：用户2的数据（曝光、新招呼、交换微信、添加微信）
    - 表头包含用户名
    
    Args:
        file_path: Excel文件路径
        
    Returns:
        tuple: (DataFrame, 用户名字典)
        - DataFrame包含列: date, user1_exposure, user1_greet, user1_exchange, 
          user1_add, user2_exposure, user2_greet, user2_exchange, user2_add
        - 用户名字典: {'user1_name': '用户1', 'user2_name': '用户2'}
        
    Raises:
        FileNotFoundError: 文件不存在
        ValueError: 文件格式错误
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    try:
        # 先读取前两行，用于提取用户名
        df_raw = pd.read_excel(file_path, engine='openpyxl', header=None, nrows=2)
        
        # 从第一行直接提取两个用户的名字
        # 用户1的名字在列0（第一行），用户2的名字在列7（第一行）
        first_row = df_raw.iloc[0]
        
        # 提取用户1的名字（列0）
        if len(first_row) > 0 and pd.notna(first_row.iloc[0]):
            user1_name = str(first_row.iloc[0]).strip()
        else:
            user1_name = "用户1"
        
        # 提取用户2的名字（列7）
        if len(first_row) > 7 and pd.notna(first_row.iloc[7]):
            user2_name = str(first_row.iloc[7]).strip()
        else:
            user2_name = "用户2"
        
        # 现在读取完整数据，跳过第一行（用户名行），使用第二行作为表头
        # 或者直接读取，第一行作为表头（pandas会自动处理）
        df = pd.read_excel(file_path, engine='openpyxl')
        
        if df.empty:
            raise ValueError("Excel文件为空")
        
        headers = df.columns.tolist()
        
        # 识别用户1和用户2的列
        # 新结构：用户1的列在1-5（曝光、新招呼、交换微信、添加微信、补刀次数）
        # 用户2的列在8-12（曝光、新招呼、交换微信、添加微信、补刀次数）
        # 如果只有12列，说明还没有补刀次数，用户2的列在8-11
        if len(headers) < 12:
            raise ValueError(f"Excel文件列数不足，期望至少12列，实际{len(headers)}列")
        
        has_kill_metric = len(headers) >= 13
        
        # 转换日期列（第一列）
        # 获取第一列的列名和数据
        date_col_name = df.columns[0]
        date_col = df[date_col_name]
        
        # 检查第一列是否已经是datetime类型（pandas可能已经自动识别）
        if pd.api.types.is_datetime64_any_dtype(date_col):
            # 如果已经是datetime，直接使用
            df['date'] = pd.to_datetime(date_col)
        else:
            # 处理日期列：可能是Excel序列号、字符串或其他格式
            def safe_convert_date(x):
                if pd.isna(x):
                    return pd.NaT
                
                # 如果已经是datetime类型，直接返回
                if isinstance(x, (datetime, pd.Timestamp)):
                    return pd.Timestamp(x)
                
                # 如果是字符串，尝试解析
                if isinstance(x, str):
                    # 跳过表头（如果表头是"日期"等字符串）
                    if x.strip() in ['日期', 'date', 'Date', 'DATE', 'Date', '时间', '时间']:
                        return pd.NaT
                    try:
                        # 尝试解析为日期字符串
                        return pd.to_datetime(x)
                    except:
                        return pd.NaT
                
                # 如果是数字，当作Excel日期序列号处理
                if isinstance(x, (int, float)):
                    # Excel日期序列号通常在1到100000之间（1900-2174年）
                    if 1 <= x <= 100000:
                        try:
                            return convert_excel_date(x)
                        except:
                            return pd.NaT
                    else:
                        # 可能是其他格式的数字，尝试直接转换为datetime
                        try:
                            return pd.to_datetime(x, origin='1899-12-30', unit='D')
                        except:
                            return pd.NaT
                
                return pd.NaT
            
            df['date'] = date_col.apply(safe_convert_date)
        
        # 重命名列
        # 实际Excel结构（第二行表头）：
        # 列0: 日期 | 列1: 曝光 | 列2: 新招呼 | 列3: 补刀次数 | 列4: 交换微信 | 列5: 添加微信 |
        # 列7: 日期 | 列8: 曝光 | 列9: 新招呼 | 列10: 补刀次数 | 列11: 交换微信 | 列12: 添加微信
        column_mapping = {
            headers[1]: 'user1_exposure',   # 用户1-曝光
            headers[2]: 'user1_greet',      # 用户1-新招呼
        }
        
        # 根据实际表头判断列顺序
        # 读取第二行（表头行）来确定列顺序
        df_header = pd.read_excel(file_path, engine='openpyxl', header=None, nrows=2)
        header_row = df_header.iloc[1]  # 第二行是表头
        
        # 用户1的列映射（列1-5）
        user1_cols = {}
        for col_idx in range(1, min(6, len(header_row))):
            header_val = str(header_row.iloc[col_idx]).strip() if pd.notna(header_row.iloc[col_idx]) else ''
            if header_val == '曝光':
                user1_cols[col_idx] = 'user1_exposure'
            elif header_val == '新招呼':
                user1_cols[col_idx] = 'user1_greet'
            elif header_val == '补刀次数':
                user1_cols[col_idx] = 'user1_kill'
            elif header_val == '交换微信':
                user1_cols[col_idx] = 'user1_exchange'
            elif header_val == '添加微信':
                user1_cols[col_idx] = 'user1_add'
        
        # 用户2的列映射（列8-12）
        user2_cols = {}
        for col_idx in range(8, min(13, len(header_row))):
            header_val = str(header_row.iloc[col_idx]).strip() if pd.notna(header_row.iloc[col_idx]) else ''
            if header_val == '曝光':
                user2_cols[col_idx] = 'user2_exposure'
            elif header_val == '新招呼':
                user2_cols[col_idx] = 'user2_greet'
            elif header_val == '补刀次数':
                user2_cols[col_idx] = 'user2_kill'
            elif header_val == '交换微信':
                user2_cols[col_idx] = 'user2_exchange'
            elif header_val == '添加微信':
                user2_cols[col_idx] = 'user2_add'
        
        # 合并映射
        for col_idx, col_name in user1_cols.items():
            if col_idx < len(headers):
                column_mapping[headers[col_idx]] = col_name
        
        for col_idx, col_name in user2_cols.items():
            if col_idx < len(headers):
                column_mapping[headers[col_idx]] = col_name
        
        # 选择需要的列并重命名
        new_df = pd.DataFrame()
        new_df['date'] = df['date']
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                new_df[new_col] = df[old_col]
        
        # 删除日期为NaN的行
        before_drop = len(new_df)
        new_df = new_df.dropna(subset=['date'])
        after_drop = len(new_df)
        
        if after_drop == 0:
            raise ValueError(
                f"无法解析日期数据。请检查Excel文件第一列是否为有效的日期格式。\n"
                f"支持的格式：Excel日期序列号（数字）、日期字符串、或datetime对象。\n"
                f"原始数据第一列类型：{date_col.dtype}，前5个值：{date_col.head().tolist()}"
            )
        
        if before_drop > after_drop:
            print(f"警告：删除了 {before_drop - after_drop} 行无效日期数据")
        
        # 按日期排序
        new_df = new_df.sort_values('date').reset_index(drop=True)
        
        # 构建用户名字典
        user_names = {
            'user1_name': user1_name,
            'user2_name': user2_name
        }
        
        return new_df, user_names
        
    except Exception as e:
        if isinstance(e, (FileNotFoundError, ValueError)):
            raise
        raise ValueError(f"读取Excel文件失败: {str(e)}")


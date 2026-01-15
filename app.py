"""
BOSS数据统计可视化工具 - Streamlit主应用
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

from data_loader import load_excel_data
from data_processor import (
    filter_by_date_range,
    calculate_conversion_rates,
    get_metric_data,
    get_dual_metric_data,
    calculate_statistics
)
from visualizer import create_line_chart, create_conversion_chart, create_dual_metric_chart, export_chart


# 页面配置
st.set_page_config(
    page_title="BOSS数据统计可视化",
    page_icon="📊",
    layout="wide"
)

# 缓存数据加载
@st.cache_data
def load_data(file_path: str):
    """
    加载Excel数据（带缓存）
    """
    return load_excel_data(file_path)


def format_date_range(start_date, end_date):
    """格式化日期范围为字符串"""
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    return f"{start_str} 至 {end_str}"


def main():
    """主应用函数"""
    # 标题和说明
    st.title("📊 BOSS数据统计可视化工具")
    st.markdown("对比分析两位用户的运营数据")
    
    # 侧边栏控制面板
    with st.sidebar:
        st.header("⚙️ 控制面板")
        
        # 文件上传（必需）
        uploaded_file = st.file_uploader(
            "上传Excel文件",
            type=['xlsx'],
            help="请上传Excel数据文件以开始分析"
        )
        
        # 如果没有上传文件，显示提示并停止
        if uploaded_file is None:
            st.info("👆 请先上传Excel文件以开始分析")
            st.stop()
        
        # 保存上传的文件到临时位置
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            file_to_use = tmp_file.name
        
        try:
            df, user_names = load_data(file_to_use)
            
            # 对比模式选择
            comparison_mode = st.radio(
                "对比模式",
                options=['单指标对比', '双指标对比'],
                index=0,
                help="选择单指标对比或双指标对比模式"
            )
            
            # 指标选择
            if comparison_mode == '单指标对比':
                metric = st.selectbox(
                    "选择指标",
                    options=['曝光', '新招呼', '交换微信', '添加微信', '补刀次数'],
                    index=0
                )
                metric1 = None
                metric2 = None
            else:
                col1, col2 = st.columns(2)
                with col1:
                    metric1 = st.selectbox(
                        "指标1（左Y轴）",
                        options=['曝光', '新招呼', '交换微信', '添加微信', '补刀次数'],
                        index=0,
                        key='metric1'
                    )
                with col2:
                    metric2 = st.selectbox(
                        "指标2（右Y轴）",
                        options=['曝光', '新招呼', '交换微信', '添加微信', '补刀次数'],
                        index=1,
                        key='metric2'
                    )
                metric = None
                
                # 检查两个指标是否相同
                if metric1 == metric2:
                    st.warning("⚠️ 请选择两个不同的指标进行对比")
                    st.stop()
            
            # 日期范围选择
            st.subheader("📅 日期范围")
            
            # 计算默认日期范围（最近30天）
            if not df.empty:
                max_date = df['date'].max().date()
                min_date = df['date'].min().date()
                default_start = max(min_date, max_date - timedelta(days=30))
                default_end = max_date
            else:
                default_start = datetime.now().date() - timedelta(days=30)
                default_end = datetime.now().date()
            
            date_range = st.date_input(
                "选择日期范围",
                value=(default_start, default_end),
                min_value=min_date if not df.empty else datetime.now().date() - timedelta(days=365),
                max_value=max_date if not df.empty else datetime.now().date()
            )
            
            # 显示转化率选项
            show_conversion = st.checkbox("显示转化率", value=False)
            
            # 导出选项
            st.subheader("💾 导出")
            export_format = st.selectbox(
                "导出格式",
                options=['PNG', 'PDF', 'HTML'],
                index=0
            )
            export_button = st.button("导出图表", type="primary")
            
        except Exception as e:
            st.error(f"❌ 加载数据失败：{str(e)}")
            st.stop()
    
    # 主内容区域
    try:
        # 显示用户名
        st.info(f"ℹ️ 当前对比用户：**{user_names['user1_name']}** vs **{user_names['user2_name']}**")
        
        # 数据筛选
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filter_by_date_range(df, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        else:
            # 如果只选择了一个日期，使用该日期作为起始和结束
            if isinstance(date_range, tuple):
                start_date = date_range[0]
                end_date = date_range[-1]
            else:
                start_date = end_date = date_range
            filtered_df = filter_by_date_range(df, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        
        if filtered_df.empty:
            st.warning("⚠️ 选择的日期范围内没有数据")
            st.stop()
        
        # 格式化日期范围字符串
        date_range_str = format_date_range(start_date, end_date)
        
        # 根据对比模式显示不同的图表和统计
        if comparison_mode == '单指标对比':
            # 单指标对比模式
            dates, user1_values, user2_values = get_metric_data(filtered_df, metric)
            
            # 创建并显示主图表
            fig = create_line_chart(
                dates, user1_values, user2_values,
                user_names['user1_name'], user_names['user2_name'],
                metric, date_range_str
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 统计摘要
            stats = calculate_statistics(filtered_df, metric)
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("数据天数", len(filtered_df))
            
            with col2:
                st.metric(
                    f"{user_names['user1_name']}平均值",
                    f"{stats['user1']['mean']:.1f}"
                )
            
            with col3:
                st.metric(
                    f"{user_names['user2_name']}平均值",
                    f"{stats['user2']['mean']:.1f}"
                )
            
            with col4:
                diff = stats['user2']['mean'] - stats['user1']['mean']
                st.metric(
                    "差值",
                    f"{diff:+.1f}",
                    delta=f"{diff/stats['user1']['mean']*100:+.1f}%" if stats['user1']['mean'] > 0 else None
                )
        else:
            # 双指标对比模式
            dates, metric1_user1_values, metric1_user2_values, metric2_user1_values, metric2_user2_values = get_dual_metric_data(
                filtered_df, metric1, metric2
            )
            
            # 创建并显示双指标对比图表
            fig = create_dual_metric_chart(
                dates,
                metric1_user1_values, metric1_user2_values,
                metric2_user1_values, metric2_user2_values,
                user_names['user1_name'], user_names['user2_name'],
                metric1, metric2,
                date_range_str
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 双指标统计摘要
            stats1 = calculate_statistics(filtered_df, metric1)
            stats2 = calculate_statistics(filtered_df, metric2)
            
            st.subheader(f"📊 {metric1} 统计")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("数据天数", len(filtered_df))
            with col2:
                st.metric(
                    f"{user_names['user1_name']}平均值",
                    f"{stats1['user1']['mean']:.1f}"
                )
            with col3:
                st.metric(
                    f"{user_names['user2_name']}平均值",
                    f"{stats1['user2']['mean']:.1f}"
                )
            with col4:
                diff1 = stats1['user2']['mean'] - stats1['user1']['mean']
                st.metric(
                    "差值",
                    f"{diff1:+.1f}",
                    delta=f"{diff1/stats1['user1']['mean']*100:+.1f}%" if stats1['user1']['mean'] > 0 else None
                )
            
            st.subheader(f"📊 {metric2} 统计")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("数据天数", len(filtered_df))
            with col2:
                st.metric(
                    f"{user_names['user1_name']}平均值",
                    f"{stats2['user1']['mean']:.1f}"
                )
            with col3:
                st.metric(
                    f"{user_names['user2_name']}平均值",
                    f"{stats2['user2']['mean']:.1f}"
                )
            with col4:
                diff2 = stats2['user2']['mean'] - stats2['user1']['mean']
                st.metric(
                    "差值",
                    f"{diff2:+.1f}",
                    delta=f"{diff2/stats2['user1']['mean']*100:+.1f}%" if stats2['user1']['mean'] > 0 else None
                )
        
        # 转化率图表（可选）
        if show_conversion:
            st.divider()
            st.subheader("📉 添加微信转化率分析")
            
            conversion_df = calculate_conversion_rates(filtered_df)
            conversion_fig = create_conversion_chart(
                conversion_df,
                user_names['user1_name'],
                user_names['user2_name'],
                date_range_str
            )
            st.plotly_chart(conversion_fig, use_container_width=True)
            
            # 转化率统计
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    f"{user_names['user1_name']}平均转化率",
                    f"{conversion_df['user1_conversion_rate'].mean():.1f}%"
                )
            with col2:
                st.metric(
                    f"{user_names['user2_name']}平均转化率",
                    f"{conversion_df['user2_conversion_rate'].mean():.1f}%"
                )
        
        # 数据表格（可折叠）
        with st.expander("📋 查看原始数据"):
            st.dataframe(
                filtered_df,
                use_container_width=True,
                hide_index=True
            )
        
        # 导出处理
        if export_button:
            try:
                if comparison_mode == '单指标对比':
                    filename = f"chart_{metric}_{date_range_str.replace(' ', '_').replace('至', 'to')}.{export_format.lower()}"
                else:
                    filename = f"chart_{metric1}_vs_{metric2}_{date_range_str.replace(' ', '_').replace('至', 'to')}.{export_format.lower()}"
                export_chart(fig, filename, export_format)
                st.success(f"✅ 图表已导出：{filename}")
            except Exception as e:
                st.error(f"❌ 导出失败：{str(e)}")
                if "kaleido" in str(e).lower():
                    st.info("💡 PNG和PDF导出需要安装kaleido：`pip install kaleido`")
    
    except Exception as e:
        st.error(f"❌ 发生错误：{str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()


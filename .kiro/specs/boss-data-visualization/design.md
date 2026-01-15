# BOSS 数据统计可视化工具 - 设计文档

## 1. 系统架构

### 1.1 整体架构
```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Web UI                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ 日期选择器    │  │ 指标选择器    │  │ 导出按钮      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │           Plotly 交互式图表                        │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   数据处理层 (Pandas)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Excel 读取    │  │ 数据清洗      │  │ 数据筛选      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  数据源 (Excel 文件)                     │
│              BOSS数据统计.xlsx                           │
└─────────────────────────────────────────────────────────┘
```

### 1.2 技术栈
- **前端框架**: Streamlit 1.30+
- **数据处理**: Pandas 2.0+
- **可视化**: Plotly 5.18+
- **Excel 读取**: openpyxl 3.1+
- **图表导出**: kaleido 0.2.1+（可选，用于PNG/PDF导出）
- **Python 版本**: 3.8+

## 2. 数据模型

### 2.1 Excel 文件结构
```
列索引    0        1         2          3          4        5          6           7          8
       日期   用户1曝光  用户1新招呼  用户1交换微信  用户1添加微信  用户2曝光  用户2新招呼  用户2交换微信  用户2添加微信
表头    日期   用户A     用户A       用户A         用户A       用户B      用户B        用户B         用户B
行1     45957    100       20         15          10       120        25          18          12
行2     45958    110       22         16          11       115        23          17          11
...

注：用户名从表头自动读取，支持任意用户名
```

### 2.2 数据结构定义

#### 原始数据 DataFrame
```python
columns = [
    'date',           # 日期 (datetime)
    'user1_exposure',   # 用户1-曝光 (int)
    'user1_greet',      # 用户1-新招呼 (int)
    'user1_exchange',   # 用户1-交换微信 (int)
    'user1_add',        # 用户1-添加微信 (int)
    'user2_exposure',   # 用户2-曝光 (int)
    'user2_greet',      # 用户2-新招呼 (int)
    'user2_exchange',   # 用户2-交换微信 (int)
    'user2_add'         # 用户2-添加微信 (int)
]

# 用户名存储在元数据中
metadata = {
    'user1_name': '用户A',  # 从表头读取
    'user2_name': '用户B'   # 从表头读取
}
```

#### 转化率 DataFrame（可选）
```python
columns = [
    'date',                    # 日期
    'user1_conversion_rate',  # 用户1-添加微信转化率 (添加微信/交换微信 %)
    'user2_conversion_rate'   # 用户2-添加微信转化率 (添加微信/交换微信 %)
]
```

## 3. 核心模块设计

### 3.1 数据加载模块 (data_loader.py)

#### 函数: load_excel_data(file_path: str) -> tuple[pd.DataFrame, dict]
**功能**: 读取 Excel 文件并转换为标准 DataFrame，同时提取用户名

**输入**:
- file_path: Excel 文件路径

**输出**:
- DataFrame: 包含日期和所有指标的数据框
- dict: 用户名字典 {'user1_name': '用户1姓名', 'user2_name': '用户2姓名'}

**处理流程**:
1. 使用 pd.read_excel() 读取文件（包含表头）
2. 从表头提取用户名（假设表头第2列和第6列包含用户名）
3. 识别列结构（第一列为日期，后续为两组用户数据）
4. 转换 Excel 日期序列号为 datetime 对象
5. 重命名列为标准名称（user1_*, user2_*）
6. 处理缺失值（保留为 NaN）
7. 按日期排序

**错误处理**:
- 文件不存在：抛出 FileNotFoundError
- 格式错误：抛出 ValueError 并提示用户

#### 函数: convert_excel_date(excel_date: float) -> datetime
**功能**: 将 Excel 日期序列号转换为 Python datetime

**公式**: `datetime(1899, 12, 30) + timedelta(days=excel_date)`

### 3.2 数据处理模块 (data_processor.py)

#### 函数: filter_by_date_range(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame
**功能**: 根据日期范围筛选数据

**输入**:
- df: 原始数据框
- start_date: 起始日期 (YYYY-MM-DD)
- end_date: 结束日期 (YYYY-MM-DD)

**输出**:
- 筛选后的 DataFrame

#### 函数: calculate_conversion_rates(df: pd.DataFrame) -> pd.DataFrame
**功能**: 计算转化率指标

**计算公式**:
- 添加微信转化率 = (添加微信 / 交换微信) × 100%

**特殊处理**:
- 分母为 0 或 NaN 时，结果为 NaN
- 使用 pd.Series.div() 方法安全除法

#### 函数: get_metric_data(df: pd.DataFrame, metric: str) -> tuple
**功能**: 提取指定指标的两位用户数据

**输入**:
- df: 数据框
- metric: 指标名称 ('曝光', '新招呼', '交换微信', '添加微信', '补刀次数')

**输出**:
- (dates, user1_values, user2_values): 日期列表和两位用户的数值列表

#### 函数: get_dual_metric_data(df: pd.DataFrame, metric1: str, metric2: str) -> tuple
**功能**: 提取两个指标的两位用户数据

**输入**:
- df: 数据框
- metric1: 指标1名称
- metric2: 指标2名称

**输出**:
- (dates, metric1_user1_values, metric1_user2_values, metric2_user1_values, metric2_user2_values): 日期列表和两个指标的数值列表

### 3.3 可视化模块 (visualizer.py)

#### 函数: create_line_chart(dates, user1_values, user2_values, user1_name, user2_name, metric_name, date_range) -> plotly.graph_objects.Figure
**功能**: 创建双用户对比折线图

**参数**:
- dates: 日期列表
- user1_values: 用户1数据
- user2_values: 用户2数据
- user1_name: 用户1姓名
- user2_name: 用户2姓名
- metric_name: 指标名称
- date_range: 日期范围字符串

**图表配置**:
```python
layout = {
    'title': f'{date_range} {user1_name} vs {user2_name} - {metric_name}趋势',
    'xaxis': {'title': '日期', 'gridcolor': '#E5E5E5'},
    'yaxis': {'title': metric_name, 'gridcolor': '#E5E5E5'},
    'hovermode': 'x unified',
    'legend': {'orientation': 'h', 'y': -0.2}
}

trace_user1 = {
    'name': user1_name,
    'mode': 'lines+markers',
    'line': {'color': '#1f77b4', 'width': 2},
    'marker': {'size': 6},
    'connectgaps': False  # 不连接缺失值
}

trace_user2 = {
    'name': user2_name,
    'mode': 'lines+markers',
    'line': {'color': '#ff7f0e', 'width': 2},
    'marker': {'size': 6},
    'connectgaps': False
}
```

#### 函数: create_dual_metric_chart(...) -> plotly.graph_objects.Figure
**功能**: 创建双指标对比图表（使用双Y轴）

**参数**:
- dates: 日期列表
- metric1_user1_values, metric1_user2_values: 指标1的两位用户数据
- metric2_user1_values, metric2_user2_values: 指标2的两位用户数据
- user1_name, user2_name: 用户姓名
- metric1_name, metric2_name: 指标名称
- date_range: 日期范围字符串

**图表配置**:
- 使用 `make_subplots` 创建双Y轴图表
- 指标1使用左Y轴，实线显示
- 指标2使用右Y轴，虚线显示
- 不同指标使用不同颜色和标记样式区分

#### 函数: export_chart(fig, filename: str, format: str) -> None
**功能**: 导出图表为文件

**支持格式**:
- PNG: fig.write_image(filename) (需要 kaleido)
- PDF: fig.write_image(filename) (需要 kaleido)
- HTML: fig.write_html(filename)

### 3.4 主应用模块 (app.py)

#### Streamlit 应用结构
```python
def main():
    # 1. 页面配置
    st.set_page_config(
        page_title="BOSS数据统计可视化",
        page_icon="📊",
        layout="wide"
    )
    
    # 2. 标题和说明
    st.title("📊 BOSS数据统计可视化工具")
    st.markdown("对比分析两位用户的运营数据")
    
    # 3. 侧边栏控制面板
    with st.sidebar:
        # 3.1 文件上传（可选）
        uploaded_file = st.file_uploader("上传Excel文件", type=['xlsx'])
        
        # 3.2 对比模式选择
        comparison_mode = st.radio(
            "对比模式",
            options=['单指标对比', '双指标对比']
        )
        
        # 3.2.1 单指标对比模式
        if comparison_mode == '单指标对比':
            metric = st.selectbox(
                "选择指标",
                options=['曝光', '新招呼', '交换微信', '添加微信', '补刀次数']
            )
        # 3.2.2 双指标对比模式
        else:
            metric1 = st.selectbox("指标1（左Y轴）", options=[...])
            metric2 = st.selectbox("指标2（右Y轴）", options=[...])
        
        # 3.3 日期范围选择
        date_range = st.date_input(
            "选择日期范围",
            value=(default_start, default_end)
        )
        
        # 3.4 显示转化率选项
        show_conversion = st.checkbox("显示转化率", value=False)
        
        # 3.5 导出选项
        export_format = st.selectbox(
            "导出格式",
            options=['PNG', 'PDF', 'HTML']
        )
        export_button = st.button("导出图表")
    
    # 4. 数据加载
    df, user_names = load_data(uploaded_file or 'BOSS数据统计.xlsx')
    
    # 4.1 显示用户名
    st.info(f"当前对比用户：{user_names['user1_name']} vs {user_names['user2_name']}")
    
    # 5. 数据筛选
    filtered_df = filter_by_date_range(df, date_range[0], date_range[1])
    
    # 6. 图表展示
    fig = create_line_chart(
        filtered_df, 
        metric, 
        user_names['user1_name'], 
        user_names['user2_name']
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 7. 数据表格（可折叠）
    with st.expander("查看原始数据"):
        st.dataframe(filtered_df)
    
    # 8. 统计摘要
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("数据天数", len(filtered_df))
    with col2:
        st.metric(f"{user_names['user1_name']}平均值", filtered_df['user1_metric'].mean())
    with col3:
        st.metric(f"{user_names['user2_name']}平均值", filtered_df['user2_metric'].mean())
    
    # 9. 导出处理
    if export_button:
        export_chart(fig, f"chart_{metric}_{date_range}.{export_format.lower()}")
        st.success("图表已导出！")
```

## 4. 数据流程

### 4.1 应用启动流程
```
1. 加载 Streamlit 应用
2. 初始化会话状态 (st.session_state)
3. 读取默认 Excel 文件
4. 解析数据并缓存 (@st.cache_data)
5. 计算默认日期范围（最近30天）
6. 渲染初始图表
```

### 4.2 用户交互流程
```
用户操作 → 触发 Streamlit 重新运行 → 更新参数 → 重新筛选数据 → 重新生成图表 → 更新显示
```

### 4.3 数据缓存策略
```python
@st.cache_data
def load_data(file_path):
    # 缓存原始数据加载，避免重复读取文件
    return load_excel_data(file_path)

# 不缓存筛选后的数据，因为参数经常变化
def filter_data(df, start, end, metric):
    return filter_by_date_range(df, start, end)
```

## 5. UI/UX 设计

### 5.1 布局设计
```
┌─────────────────────────────────────────────────────────────┐
│  📊 BOSS数据统计可视化工具                                    │
│  对比分析两位用户的运营数据                                   │
│  ℹ️ 当前对比用户：用户1 vs 用户2                              │
├──────────┬──────────────────────────────────────────────────┤
│          │                                                  │
│ 侧边栏    │              主图表区域                           │
│          │                                                  │
│ □ 指标选择 │         [折线图显示区域]                         │
│ □ 日期范围 │                                                  │
│ □ 转化率   │                                                  │
│ □ 导出     │                                                  │
│          ├──────────────────────────────────────────────────┤
│          │  [数据天数]  [用户1平均]  [用户2平均]              │
│          ├──────────────────────────────────────────────────┤
│          │  ▼ 查看原始数据                                   │
│          │     [数据表格]                                    │
└──────────┴──────────────────────────────────────────────────┘
```

### 5.2 颜色方案
- 用户1曲线: #1f77b4 (蓝色)
- 用户2曲线: #ff7f0e (橙色)
- 背景: #FFFFFF (白色)
- 网格线: #E5E5E5 (浅灰)
- 强调色: #2E86AB (深蓝)

### 5.3 响应式设计
- 使用 Streamlit 的 `use_container_width=True` 自适应宽度
- 移动端自动调整侧边栏为顶部菜单
- 图表高度固定为 500px，宽度自适应

## 6. 错误处理

### 6.1 文件错误
```python
try:
    df = pd.read_excel(file_path)
except FileNotFoundError:
    st.error("❌ 找不到文件：BOSS数据统计.xlsx")
    st.info("请确保文件在当前目录下")
except Exception as e:
    st.error(f"❌ 读取文件失败：{str(e)}")
```

### 6.2 数据错误
```python
if df.empty:
    st.warning("⚠️ 选择的日期范围内没有数据")
    st.stop()

if df['date'].isna().any():
    st.warning("⚠️ 检测到无效日期，已自动过滤")
    df = df.dropna(subset=['date'])
```

### 6.3 计算错误
```python
# 安全除法，避免除零错误
conversion_rate = df['add'].div(df['exposure']).fillna(0) * 100
```

## 7. 性能优化

### 7.1 数据加载优化
- 使用 `@st.cache_data` 缓存 Excel 读取结果
- 仅在文件变化时重新加载

### 7.2 图表渲染优化
- 限制数据点数量（超过 1000 点时降采样）
- 使用 Plotly 的 `scattergl` 模式处理大数据集

### 7.3 内存优化
- 使用 `dtype` 优化数据类型
- 及时释放不需要的 DataFrame

## 8. 测试策略

### 8.1 功能验证
- 手动验证日期转换的准确性
- 验证数据筛选的边界条件
- 验证转化率计算的正确性

### 8.2 集成验证
- 验证完整的数据加载到展示流程
- 验证不同日期范围的切换
- 验证图表导出功能
- 验证双指标对比功能

### 8.3 用户验收
- 验证图表显示是否符合预期
- 验证交互操作是否流畅
- 验证导出文件是否正确
- 验证双指标对比图表显示正确

## 9. 部署方案

### 9.1 本地运行
```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run app.py
```

### 9.2 Streamlit Cloud 部署（可选）
1. 将代码推送到 GitHub
2. 在 Streamlit Cloud 创建应用
3. 连接 GitHub 仓库
4. 自动部署

### 9.3 Docker 部署（可选）
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## 10. 项目文件结构

```
boss-data-visualization/
├── app.py                    # Streamlit 主应用
├── data_loader.py            # 数据加载模块
├── data_processor.py         # 数据处理模块
├── visualizer.py             # 可视化模块
├── requirements.txt          # 依赖列表
├── .gitignore                # Git忽略文件配置
├── README.md                 # 项目说明
├── PROJECT_STATUS.md         # 项目状态文档
├── recommended_excel_structure.md  # Excel结构建议
└── excel_structure_recommendation.md  # Excel结构优化建议
```

## 11. 依赖清单 (requirements.txt)

```
streamlit>=1.30.0
pandas>=2.0.0
plotly>=5.18.0
openpyxl>=3.1.0
kaleido>=0.2.1  # 用于图表导出（PNG/PDF）
```

## 12. 正确性属性

### 12.1 数据完整性属性
**属性 12.1.1**: 日期转换的可逆性  
对于任何有效的 Excel 日期序列号 d，转换为 datetime 后再转换回序列号应得到原值（误差 < 1天）

**属性 12.1.2**: 数据行数一致性  
加载后的 DataFrame 行数应等于 Excel 文件的数据行数（排除表头）

### 12.2 数据筛选属性
**属性 12.2.1**: 日期范围边界正确性  
筛选后的所有日期应满足：start_date ≤ date ≤ end_date

**属性 12.2.2**: 筛选幂等性  
对已筛选的数据再次应用相同筛选条件，结果应保持不变

### 12.3 转化率计算属性
**属性 12.3.1**: 转化率范围有效性  
所有转化率值应在 [0, 100] 范围内（排除 NaN），因为添加微信数 ≤ 交换微信数

**属性 12.3.2**: 转化率逻辑一致性  
当交换微信数为 0 时，转化率应为 NaN；当添加微信数为 0 且交换微信数 > 0 时，转化率应为 0

### 12.4 图表渲染属性
**属性 12.4.1**: 数据点数量一致性  
图表中每条曲线的数据点数量应等于筛选后的日期数量

**属性 12.4.2**: 缺失值处理正确性  
当数据为 NaN 时，图表不应连接前后数据点

## 13. 测试框架

使用 **Hypothesis** 进行属性测试：

```python
from hypothesis import given, strategies as st
import hypothesis.extra.pandas as pdst

@given(pdst.data_frames([
    pdst.column('date', dtype='datetime64[ns]'),
    pdst.column('value', dtype='float64')
]))
def test_filter_preserves_order(df):
    """属性测试：筛选后日期顺序保持不变"""
    filtered = filter_by_date_range(df, df['date'].min(), df['date'].max())
    assert filtered['date'].is_monotonic_increasing
```

## 14. 未来扩展考虑

### 14.1 多用户支持
- 支持 3 个或更多用户的同时对比
- 用户选择器（从 Excel 中选择要对比的用户）
- 动态颜色分配

### 14.2 高级分析
- 趋势预测（线性回归）
- 异常检测（Z-score）
- 相关性分析
- 多维度转化率分析（如：添加微信/曝光、交换微信/新招呼等）

### 14.3 数据持久化
- 支持 SQLite 存储历史数据
- 增量更新机制

### 14.4 自动化报告
- 定时生成周报/月报
- 邮件自动发送

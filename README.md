# BOSS 数据统计可视化工具

一个交互式数据可视化工具，用于分析和对比两位用户的每日运营数据。

## 功能特性

- 📊 自动加载和解析 Excel 文件中的运营数据
- 📈 单指标对比：在同一张折线图中对比两位用户的数据曲线
- 🔀 双指标对比：同时对比两个不同指标，使用双Y轴图表展示（新增功能）
- 📅 灵活的日期范围筛选（默认显示最近30天）
- 🔄 支持切换不同指标（曝光、新招呼、补刀次数、交换微信、添加微信）
- 📉 转化率分析（添加微信转化率）
- 💾 图表导出功能（PNG、PDF、HTML）

## 安装说明

1. 确保已安装 Python 3.8+
2. 安装 [uv](https://github.com/astral-sh/uv)（如果尚未安装）：
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   或使用 pip：
   ```bash
   pip install uv
   ```

3. 使用 uv 创建虚拟环境并安装依赖：
   ```bash
   uv venv
   source .venv/bin/activate  # 在 macOS/Linux 上
   # 或
   .venv\Scripts\activate  # 在 Windows 上
   uv pip install -r requirements.txt
   ```

   或者直接使用 uv 运行（无需手动激活环境）：
   ```bash
   uv venv
   uv pip install -r requirements.txt
   ```

## 使用方法

1. 确保 `BOSS数据统计.xlsx` 文件在项目根目录下

2. 运行应用：
   ```bash
   # 激活虚拟环境后运行：
   source .venv/bin/activate  # macOS/Linux
   # 或
   .venv\Scripts\activate  # Windows
   streamlit run app.py
   
   # 或者使用 uv 直接运行（如果已安装依赖）：
   uv run streamlit run app.py
   ```

3. 在浏览器中打开显示的地址（通常是 http://localhost:8501）

4. 使用侧边栏选择指标和日期范围，查看数据对比图表

## 项目结构

```
boss-data-visualization/
├── app.py                    # Streamlit 主应用
├── data_loader.py            # 数据加载模块
├── data_processor.py         # 数据处理模块（支持单指标和双指标数据提取）
├── visualizer.py             # 可视化模块（单指标和双指标图表）
├── requirements.txt          # 依赖列表
├── .gitignore                # Git忽略文件配置
├── README.md                 # 项目说明
├── PROJECT_STATUS.md         # 项目状态文档
├── recommended_excel_structure.md  # Excel结构建议
└── excel_structure_recommendation.md  # Excel结构优化建议
```

## 技术栈

- **前端框架**: Streamlit 1.30+
- **数据处理**: Pandas 2.0+
- **可视化**: Plotly 5.18+
- **Excel 读取**: openpyxl 3.1+
- **图表导出**: kaleido 0.2.1+（用于PNG/PDF导出）

## 使用方法

### 单指标对比模式
1. 选择"单指标对比"模式
2. 选择一个指标（如"曝光"）
3. 选择日期范围
4. 查看单指标对比图表和统计摘要

### 双指标对比模式（新增）
1. 选择"双指标对比"模式
2. 选择指标1（左Y轴，如"曝光"）
3. 选择指标2（右Y轴，如"新招呼"）
4. 选择日期范围
5. 查看双指标对比图表（双Y轴）和两个指标的统计摘要

**注意**：双指标模式下不能选择相同的两个指标

## Excel文件结构

### 表结构要求

**第一行（用户名行）：**
- 列0（A1）：用户1的名字
- 列7（H1）：用户2的名字

**第二行（表头行）：**
- 列0：日期
- 列1：曝光
- 列2：新招呼
- 列3：补刀次数
- 列4：交换微信
- 列5：添加微信
- 列7：日期（用户2）
- 列8-12：用户2的5个指标（顺序同上）

**数据行：** 从第三行开始

### 重要特性

- ✅ **动态列识别**：代码根据表头自动识别列顺序，支持列顺序变化
- ✅ **兼容性**：支持12列（无补刀次数）和13列（有补刀次数）两种结构

详细说明请查看 [recommended_excel_structure.md](recommended_excel_structure.md)

## 依赖管理

本项目使用 [uv](https://github.com/astral-sh/uv) 进行依赖管理。

### 添加新依赖
```bash
uv add package-name
```

### 移除依赖
```bash
uv remove package-name
```

### 更新依赖
```bash
uv sync --upgrade
```

### 查看依赖
```bash
uv pip list
```

## 开发说明

本项目采用模块化设计：
1. **data_loader.py**: 负责Excel文件读取和数据解析
2. **data_processor.py**: 负责数据筛选、统计和指标提取
3. **visualizer.py**: 负责图表创建和导出
4. **app.py**: 负责Streamlit界面和用户交互

所有核心功能都有完整的文档注释和类型提示。

## 项目状态

**当前状态**: ✅ **生产就绪，功能完整**

- ✅ 所有核心功能已完成
- ✅ 单指标对比功能正常
- ✅ 双指标对比功能已实现（新增）
- ✅ 功能验证通过
- ✅ 列映射问题已修复
- ✅ 支持5个指标（曝光、新招呼、补刀次数、交换微信、添加微信）

详细项目状态请查看 [PROJECT_STATUS.md](PROJECT_STATUS.md)

## 许可证

MIT


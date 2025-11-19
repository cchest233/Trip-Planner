# Quick Start Guide

## 快速开始指南

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```env
OPENAI_API_KEY=sk-your-actual-key-here
PARSER_MODEL=gpt-4
PLANNER_MODEL=gpt-4
RENDERER_MODEL=gpt-3.5-turbo
```

### 3. 运行示例

#### 基础用法

```bash
python main.py "I want to drive from San Francisco to Los Angeles in 3 days, I like coastal views and good food"
```

#### 交互模式

```bash
python main.py --interactive
```

#### 带调试信息

```bash
python main.py "Plan a Seattle to Portland road trip" --debug
```

#### 保存到文件

```bash
python main.py "SF to LA road trip" --output my_trip.md
```

### 4. 示例查询

以下是一些示例查询，你可以直接使用：

**英文示例：**
- "I want to drive from San Francisco to Los Angeles in 3 days, I like coastal views and good food"
- "Plan a 4-day road trip from Seattle to Portland with lots of nature stops"
- "Road trip from Boston to New York, 2 days, interested in city attractions and museums"

**中文示例：**
- "我想从旧金山开车到洛杉矶，3天，喜欢海岸风景和美食"
- "计划一次西雅图到波特兰的4天自驾游，多安排自然景点"
- "波士顿到纽约的公路旅行，2天，对城市景点和博物馆感兴趣"

### 5. 项目结构

```
roadtrip_planner/
├── config.py              # 配置管理
├── models.py              # Pydantic 数据模型
├── state.py               # LangGraph 状态管理
├── llm_clients.py         # LLM 抽象层（pydantic-ai）
├── tools_media.py         # 媒体搜索工具存根
├── nodes_parse_request.py # 节点：解析请求
├── nodes_media_search.py  # 节点：媒体搜索
├── nodes_route_skeleton.py# 节点：路线骨架规划
├── nodes_select_pois.py   # 节点：选择兴趣点
├── nodes_render_itinerary.py # 节点：渲染行程
└── graph.py               # LangGraph 工作流构建
```

### 6. 工作流程

```
用户输入
    ↓
[parse_request] 解析自然语言 → RoadTripRequest
    ↓
[media_search] 搜索相关内容/媒体
    ↓
[plan_route_skeleton] 创建路线骨架
    ↓
[select_daily_pois] 选择每日兴趣点
    ↓
[render_itinerary] 生成可读行程
    ↓
输出最终行程
```

### 7. 自定义配置

#### 修改模型

编辑 `.env` 文件来使用不同的模型：

```env
# 使用更便宜的模型以降低成本
PARSER_MODEL=gpt-3.5-turbo
PLANNER_MODEL=gpt-3.5-turbo
RENDERER_MODEL=gpt-3.5-turbo

# 或使用 Claude
PARSER_MODEL=claude-3-sonnet-20240229
```

#### 调试模式

```env
DEBUG_MODE=true
VERBOSE_TRACE=true
```

### 8. 扩展开发

#### 添加新的媒体源

编辑 `roadtrip_planner/tools_media.py`：

```python
def search_xiaohongshu(query: str, location: str | None = None) -> list[MediaItem]:
    # 实现小红书 API 集成
    api_key = config.XIAOHONGSHU_API_KEY
    # ... 调用 API
    return media_items
```

#### 添加新节点

1. 创建新文件 `roadtrip_planner/nodes_your_feature.py`
2. 实现节点函数：
```python
def your_feature(state: RoadTripState) -> RoadTripState:
    state = log_node_start(state, "your_feature")
    # ... 你的逻辑
    state = log_node_complete(state, "your_feature")
    return state
```
3. 在 `graph.py` 中添加节点和边

#### 添加循环和条件

在 `graph.py` 中：

```python
def should_refine(state: RoadTripState) -> str:
    # 决策逻辑
    if needs_refinement:
        return "refine"
    return "continue"

# 添加条件边
graph.add_conditional_edges(
    "select_daily_pois",
    should_refine,
    {
        "refine": "plan_route_skeleton",  # 循环回去
        "continue": "render_itinerary"     # 继续前进
    }
)
```

### 9. 故障排查

#### API 密钥错误

```
Configuration Error: OPENAI_API_KEY not set
```

**解决方案：**确保 `.env` 文件存在且包含有效的 API 密钥。

#### 模块导入错误

```
ModuleNotFoundError: No module named 'pydantic_ai'
```

**解决方案：**
```bash
pip install pydantic-ai
```

#### LangGraph 版本问题

如果遇到 LangGraph 兼容性问题，尝试：

```bash
pip install --upgrade langgraph langchain-core
```

### 10. 性能优化建议

- **成本优化：**使用 `gpt-3.5-turbo` 替代 `gpt-4` 以降低 API 调用成本
- **速度优化：**考虑并行调用多个媒体搜索 API
- **缓存：**实现结果缓存以避免重复的 LLM 调用

### 需要帮助？

- 查看 `README.md` 了解项目概述
- 查看各个节点文件中的详细文档字符串
- 使用 `--debug` 标志查看详细的执行跟踪

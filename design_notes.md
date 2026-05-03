# NSEH 架构设计笔记

## 已完成的核心架构改动

### 1. Feature → 字符串标签序列
- 启发式的 `feature` 字段改为 **list of strings**（标签序列）
- 每个标签以 `[标签名]` 格式由 LLM 输出，prompt_template.py 中 `parse_tags()` 负责解析
- 记忆中的 `positive_features` / `negative_features` 存储的是 **标签列表的组合**
- 去重逻辑改为 tuple 化比较（见 evolution.py `dedup_features()`）

### 2. 标签管理系统的数据库支持
- `tag_stats` 表：记录每个标签被标记为"积极"或"消极"的次数
- `tag_combinations` 表：记录标签组合对应的平均适应度，支持组合层面的优劣势判断

### 3. 前后端分离的查询接口
- `GET /api/get_tag_stats` — 查询标签统计数据
- `GET /api/get_experiment_history` — 查询历史实验记录

---

## 关于泛化到其他问题的构思（待讨论）

当前框架已通过 `problems/tsp/` 模块展示了以 TSP 为例的"问题情景"模式。泛化的核心思想如下：

### 发散性想法

1. **问题情景插件化**
   - 每个问题情景（TSP、VRP、Knapsack、Job Shop Scheduling 等）是一个独立模块，位于 `problems/` 下
   - 每个情景需要提供：
     - `train_eval.py` — 快速评估函数
     - `test_eval.py` — 完整测试评估
     - `heuristic.py` — 缺省启发式（作为 baseline）
     - `datasets/` — 预生成数据集
   - 框架通过动态导入加载不同情景，已有 `importlib.import_module` 支持

2. **通用函数签名协议**
   当前 TSP 的函数签名是 `select_next_node(current_node, destination_node, unvisited_nodes, distance_matrix)` → `next_node`
   
   泛化思路：
   - 定义**启发式函数接口协议**，不同的优化问题共享相同的调用模式
   - 例如：`heuristic(state, context)` → `action`，其中 `state` 是问题状态，`context` 是元信息

3. **标签体系的继承性**
   - 某些标签是跨问题通用的：`贪婪搜索`、`随机抖动`、`局部搜索`、`动态规划`、`遗传思想`
   - 某些标签是问题特定：`最近邻`（TSP）、`贪心适应度`（Knapsack）
   - 可以建立**标签层级树**：通用标签 → 领域标签 → 问题特定标签

4. **记忆的可迁移性**
   - 如果标签是跨问题的，那么积极/消极记忆也可以跨问题共享
   - 组合优化问题本质上共享大量底层策略（构造型、改进型、元启发式）

5. **非组合优化类问题的适配**
   - 强化学习领域的策略搜索（policy search）
   - 神经网络架构搜索（NAS）中的操作选择
   - AutoML 中的 pipeline 组合
   - 关键在于将"选择下一个操作"抽象为统一的接口

### 待讨论问题

1. **用户想要什么样的泛化接口？**
   - Web 界面上直接配置问题描述、函数签名、数据路径（已有此能力）
   - 还是需要代码级别的扩展？

2. **标签库的管理方式？**
   - 预定义标签库 vs LLM 自由生成标签
   - 标签冲突消解（同义标签合并）

3. **跨问题迁移学习？**
   - 在一个问题上学到的积极特征能否自动适配到新问题？

---

## 当前技术债务

- [ ] OpenAI 库尚未安装（网络问题，需在可访问 PyPI 的环境中 `pip install openai`）
- [ ] 推送至 GitHub（已 commit，需网络环境推送到 `origin master`）
- [ ] 实际运行测试（需要 DeepSeek API key 和网络连通）
- [ ] 前端结果图表的自动渲染（当前依赖 Chart.js 数据更新）

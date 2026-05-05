<p align="center">
  <h1 align="center">🧬 NSEH - 基于大模型的启发式组合优化算法自动生成</h1>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/LLM-DeepSeek-orange" alt="LLM">
  <img src="https://img.shields.io/badge/Framework-Flask-black?logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/status-beta-yellow" alt="Status">
  <img src="https://img.shields.io/github/stars/IvesSilent/NSEH?style=flat" alt="Stars">
</p>

<p align="center">
  <b>自然选择启发进化</b> · 用 LLM 自动生成 + 进化启发式算法
</p>

<p align="center">
  <a href="#v20-新特性">✨ v2.0 新特性</a> ·
  <a href="#-快速开始">🚀 快速开始</a> ·
  <a href="#-web-应用使用指南">🌐 前端</a>
</p>

---

## v2.0 新特性

### 🎨 全面 UI 升级

- **SVG 图标系统**：全部按钮、选项卡、标题的 emoji 替换为 [Heroicons](https://heroicons.com) SVG（MIT 开源），暗色/亮色主题完美匹配
- **密码可视切换**：登录/注册页密码框内嵌眼睛图标，点击切换明文
- **智能 Toast 堆叠**：多条通知自动错位排列，旧通知向上推移，避免重叠
- **弹窗动效**：模态框 fade-in + slide-up 入场动画，支持键盘 `Esc` 关闭
- **加载动画**：spinner 旋转 SVG 替换静态文字「⏳」
- **主题图标联动**：Sun/Moon SVG 随主题自动切换

### 🌳 特征探索树

新增「特征树」面板，实时可视化当前种群已探索的启发式策略空间：

- **层级分类**：按「构造型 → 改进型 → 元启发式」三层结构展示问题领域的知识图谱
- **探索状态**：已出现的标签高亮显示（蓝色），积极/消极特征分别用绿色/红色标记
- **统计摘要**：标签总数、积极/消极特征数、共现组合数一目了然
- **高频共现**：自动统计标签组合的出现频率，展示哪些策略常搭配使用

### 🔧 问题修复

- **最优适应度显示修复**：`update_population_data()` 改为扫描所有启发式寻找真正的最优值，而非假设 `heuristics[0]` 已排序
- **长文本溢出修复**：启发式详情面板中概念文本超出限制时自动滚动
- **弹窗 CSS 补齐**：`modal-overlay` 和 `modal-card` 类样式完整实现（此前缺失导致弹窗错位）
- **按钮样式修复**：场景自适应按钮独立样式设计

### ⚙️ 后端增强

- 新增 `GET /api/get_feature_tree` 端点，返回场景分类树、标签统计、共现分析

---

## 📑 目录

- [v2.0 新特性](#v20-新特性)
- [🚀 项目简介](#-项目简介)
- [🧬 核心概念：启发式种群](#-核心概念启发式种群)
- [🔄 进化流程](#-进化流程)
- [⚡ 快速开始](#-快速开始)
  - [安装依赖](#安装依赖)
  - [Web 启动](#web-启动)
  - [CLI 启动](#cli-启动)
- [📂 项目结构](#-项目结构)
- [⚙️ 参数配置](#️-参数配置)
- [🌐 Web 应用使用指南](#-web-应用使用指南)
  - [登录](#登录)
  - [进化设置](#进化设置)
  - [进化过程](#进化过程)
  - [进化结果](#进化结果)
- [📖 支持的问题情景](#-支持的问题情景)
- [📜 项目来源](#-项目来源)

---

## 🚀 项目简介

本项目使用 **LLM 生成启发式算法**，构建启发式种群，在预备数据集上执行启发式并与标准解比较计算适应度，按适应度排名保留效益最好的启发式——**模仿自然选择法则**，让算法自动进化。

> 💡 **设计灵感**：参考 [EoH (Evolution of Heuristic)](https://github.com/FeiLiu36/EoH/blob/main/README_CN.md) 的进化思路，在 LLM 交互策略和种群记忆机制上做了扩展。

---

## 🧬 核心概念：启发式种群

进化过程中培养多代**启发式种群（Population）**，每一代包含两部分：

### 启发式个体 (Heuristic)

| 维度 | 说明 |
|:----|:----|
| **概念 (Concept)** | 以自然语言描述启发式的思想方法 |
| **算法 (Algorithm)** | 可执行的 Python 函数（函数名/输入/输出固定） |
| **特征 (Feature)** | 算法的思想特点，如 "贪婪搜索"，字符串数组 |
| **适应度 (Objective)** | 评价算法效益的数值指标 |

### 种群记忆 (Memory)

| 维度 | 说明 |
|:----|:----|
| **积极特征 (Positive Feature)** | 以往进化中的优势特征组合，如 "贪婪搜索+随机抖动" |
| **消极特征 (Negative Feature)** | 以往进化中的劣势特征组合 |

![启发式种群结构：个体包含概念、算法、特征、适应度四个维度；记忆包含积极特征和消极特征](image/%E7%A7%8D%E7%BE%A4%E7%BB%93%E6%9E%84%E5%9B%BE.png)

---

## 🔄 进化流程

![进化流程总览：初始化→生成(突变/杂交/优化)→筛选(淘汰/反思)→循环](image/%E8%BF%9B%E5%8C%96%E6%B5%81%E7%A8%8B%E5%9B%BE.png)

### 阶段 0 — 初始化
设置种群容量 `N`、进化代数 `M`，生成初始启发式种群。

### 阶段 1 — 生成新启发式

| 步骤 | 操作 | 说明 |
|:---|:----|:----|
| 🧬 **1.1 突变 (Mutation)** | 提示 LLM 设计 `k1` 个**尽可能不同**的新算法 | 引入多样性 |
| 🧪 **1.2 杂交 (Hybridization)** | 选取前 `k2` 个优势算法 **两两杂交**，LLM 综合思路 | 保留优势 |
| ⚡ **1.3 优化 (Optimization)** | 对每个算法 **调参/精简/优化**，生成优化版本 | 精炼收敛 |

### 阶段 2 — 筛选与反思

| 步骤 | 操作 | 说明 |
|:---|:----|:----|
| 🗑️ **2.1 淘汰 (Elimination)** | 按适应度排名保留前 `N` 个 | 优胜劣汰 |
| 💡 **2.2 反思 (Reflection)** | 前 k3 和最差 k3 的特征分别记入积极/消极记忆 | 经验积累 |

### 阶段 3 — 循环
未达进化代数 `M` 则返回阶段 1，否则结束。


---

## ⚡ 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

> ⚠️ **需要自行申请 API Key**。默认使用 DeepSeek：[申请 DeepSeek API](https://api-docs.deepseek.com/zh-cn/api/deepseek-api/)
> - `API_BASE`: `https://api.deepseek.com`
> - 在 Web 配置页面或 `start_evo.py` 中填入 `api_key`

### Web 启动

```bash
python app.py
# 或双击 web.bat (Windows)
```

### CLI 启动

```bash
cd problems/tsp
python start_evo.py
```

CLI 参数在 `start_evo.py` 中直接配置：

| 参数 | 缺省值 | 说明 |
|:----|:------|:----|
| `POPULATION_CAPACITY` | 7 | 种群容量 |
| `NUM_GENERATIONS` | 5 | 进化代数 |
| `NUM_MUTATION` | 3 | 每轮突变数 (`k1`) |
| `NUM_HYBRIDIZATION` | 3 | 每轮杂交数 (`k2`) |
| `NUM_REFLECTION` | 3 | 反思特征数 (`k3`) |

---

## 📂 项目结构

<details>
<summary>📁 点击展开目录树</summary>

```
/NSEH
├── core/                          # 核心框架
│   ├── llm_interface.py           # LLM 通信模块
│   ├── prompt_template.py         # 提示词模板模块
│   ├── generator.py               # 启发式生成器
│   └── evolution.py               # 进化框架主逻辑
├── problems/                      # 问题情景插件
│   ├── tsp/                       # TSP 旅行商问题
│   │   ├── train_eval.py          # 训练评估
│   │   ├── test_eval.py           # 测试评估
│   │   ├── start_evo.py           # CLI 启动项
│   │   ├── heuristic.py           # 缺省启发式
│   │   ├── generate_datasets.py   # 数据集生成器
│   │   ├── datasets/              # 预生成数据集
│   │   └── result/                # 生成结果
│   ├── cvrp/                      # CVRP 容量受限车辆路径问题
│   ├── knapsack/                  # 0/1 背包问题
│   ├── pfsp/                      # PFSP 置换流水车间调度
│   └── maxcut/                    # MaxCut 最大割问题
├── static/                        # Web 前端
│   ├── NSEH_login.css/.js
│   ├── NSEH_main.css/.js
│   └── NSEH_rank.css/.js
├── templates/                     # HTML 模板
├── app.py                         # Web 应用入口 (含错误处理)
├── readme.md                      # 本文件
├── requirements.txt               # 依赖
├── nseh.db                        # SQLite 数据库
├── user_info.csv                  # 用户账密表
└── web.bat                        # Windows 启动脚本
```

</details>

---

## ⚙️ 参数配置

### 进化参数

| 参数 | 类型 | 说明 | 缺省值 |
|:----|:----|:-----|:------|
| `population_capacity` | `int` | 种群容量 | 7 |
| `num_generations` | `int` | 进化迭代次数 | 5 |
| `num_mutation` | `int` | 每代突变启发式数 | 3 |
| `num_hybridization` | `int` | 每代参与杂交数 | 3 |
| `ascend` | `bool` | 适应度是否取小 | `True` |

### LLM 与问题配置

| 参数 | 类型 | 说明 | 缺省值 |
|:----|:----|:-----|:------|
| `base_url` | `str` | LLM API 地址 | `https://api.deepseek.com/v1` |
| `llm_model` | `str` | 模型名称 | `deepseek-chat` |
| `api_key` | `str` | 你的 API Key | 需填写 |
| `problem` | `str` | 问题情景描述 | TSP 问题，即…… |
| `fun_name` | `str` | 目标函数名 | `select_next_node` |
| `fun_args` | `list` | 函数参数 | `['current_node', …]` |
| `fun_return` | `list` | 函数返回值 | `["next_node"]` |
| `fun_notes` | `str` | 注意事项 | 所有数据均为 numpy 数组… |
| `problem_path` | `str` | 问题目录（相对路径） | `problems/tsp` |
| `train_data_name` | `str` | 训练数据文件名 | `train_data_tsp.pkl` |
| `train_solution_name` | `str` | 标准解文件名 | `train_data_solution.pkl` |

---

## 🌐 Web 应用使用指南

### 登录

打开 Web 应用后需登录。密码框右侧眼睛图标可切换密码可见性。账号密码设置在 `user_info.csv` 中：

| 用户名 | 账号 | 密码 | 用户最优适应度 |
|:------|:----|:-----|:------------|
| 用户_01 | 213111111 | 123456 | null |

用户登录后，生成的最优启发式适应度会被自动录入该文件。

### 进化设置

在配置页面填写参数（见上方 [参数配置](#️-参数配置)），点击「开始进化」。

### 进化过程

进化页面动态显示各代种群及其成员启发式：

- 🖱️ **点击启发式卡片** → 查看构成及代码实现
- ⏯️ **暂停/继续** 进化过程
- ✏️ **自定义 Prompt 模板** — 当进化陷入瓶颈时，可修改模板突破限制
- 🌳 **特征树** → 点击「特征树」按钮查看当前种群的策略空间探索状态

#### 特征树面板

点击「特征树」按钮打开交互式知识图谱：

- **层级折叠**：按问题领域预设的分类树展开/收起
- **标签着色**：蓝色=已探索，绿色=积极特征（高产标签），红色=消极特征（低效标签）
- **统计栏**：顶部显示标签总数、积极/消极特征数、共现组数
- **高频组合**：底部展示哪些标签经常搭配出现，为 LLM 提示提供参考

<details>
<summary>📝 点击查看预设 Prompt 模板</summary>

#### 函数要求

```plain text
用Python实现一个名为select_next_node的函数。
该函数应接受4个输入：'current_node', 'destination_node', 'unvisited_nodes', 'distance_matrix'；
函数应返回1个输出：'next_node'。
'current_node','destination_node', 'next_node', 和 'unvisited_nodes'是节点ID，
distance_matrix是节点的距离矩阵。所有数据均为Numpy数组。
```

#### 进化策略

**MUTATION 突变**
```plain text
请你设计一个与现有的这些启发式算法尽可能不同的新启发式算法。
```

**HYBRIDIZATION 繁殖**
```plain text
请你综合现有的这些启发式算法的关键思想，设计一个新的启发式算法。
```

**OPTIMIZATION 优化**
```plain text
请你对现有的这个启发式进行优化，使用包括但不限于调整其参数值、
对其进行复杂度层面的优化或精简其结构等方式，得到一个新的启发式算法。
```

#### 分析过程

```plain text
请你梳理所有信息，进行一个长度在200字内的分析。
你可以将构思新启发式需要纳入考量的条件列举出来，并分析该如何进行设计构思或改进，
以得到新的启发式。
不要进行任何代码实现，只给出修改的目标，并构思如何设计新启发式。
```

</details>

### 进化结果

- 📈 **实时曲线**：查看各代种群最优适应度变化折线图（含历代最优、最优/均值/方差、前三条形、全部启发式、Token消耗 五种视图）
- 🏆 **排行榜**：进化结束后查看系统内各用户的最优适应度排名

---

## 📖 支持的问题情景

本项目目前支持以下 **5 种组合优化问题情景**，均可通过 Web 端「问题选择」下拉框切换。

### 🛤️ TSP（旅行商问题）

> **目标**：给定一组节点的坐标，找到访问每个节点一次并返回起点的最短路径。

| 数据集 | 位置 | 说明 |
|:------|:-----|:----|
| **训练数据** | `problems/tsp/datasets/` | 64 组 TSP100 实例，[0,1]² 空间随机生成（参考 EoH） |
| **测试数据** | `problems/tsp/datasets/` | TSP10/20/50/100/200 各 10 组实例 |

- **函数签名**：`select_next_node(current_node, destination_node, unvisited_nodes, distance_matrix) → next_node`
- **适配函数**：`train_eval.py`（动态评估） / `test_eval.py`（静态评估+计时）
- **标准解**：Concorde 精确求解器

---

### 🚚 CVRP（容量受限车辆路径问题）

> **目标**：在车辆容量限制下，为车队规划最短路径，服务所有客户节点。

| 数据集 | 位置 | 说明 |
|:------|:-----|:----|
| **训练数据** | `problems/cvrp/datasets/` | 64 组 CVRP100 实例，容量 200 |
| **测试数据** | `problems/cvrp/datasets/` | CVRP50/100/200 各 10 组实例 |

- **函数签名**：`find_best_route(current_node, remaining_demands, vehicle_capacity, current_load, distance_matrix, demand_list) → next_node`
- **标准解**：Clarke-Wright 节约算法（参考 EoH 实验设置）
- **特点**：需考虑容量约束，决策哪个客户下一个服务

---

### 🎒 Knapsack（0/1 背包问题）

> **目标**：在背包容量限制下，从一组物品中选择子集，使总价值最大化。

| 数据集 | 位置 | 说明 |
|:------|:-----|:----|
| **训练数据** | `problems/knapsack/datasets/` | 64 组，150 个物品 |
| **测试数据** | `problems/knapsack/datasets/` | 50/100/150 个物品各 10 组 |

- **函数签名**：`select_item(current_index, remaining_capacity, weights, values, num_items) → take_item`
- **标准解**：动态规划精确解
- **特点**：逐步决策选或不选物品，返回 0/1

---

### 🏭 PFSP（置换流水车间调度问题）

> **目标**：n 个作业在 m 台机器上的流水线调度，使最大完工时间（makespan）最小化。

| 数据集 | 位置 | 说明 |
|:------|:-----|:----|
| **训练数据** | `problems/pfsp/datasets/` | 64 组，20 作业 × 5 机器 |
| **测试数据** | `problems/pfsp/datasets/` | 10×5 / 20×5 / 50×10 各 10 组 |

- **函数签名**：`select_next_job(unscheduled_jobs, current_schedule, processing_times, num_machines) → next_job`
- **标准解**：NEH 启发式（EoH 论文标准基线）
- **特点**：目标是构建作业加工序列，使各机器等待时间最短

---

### ✂️ MaxCut（最大割问题）

> **目标**：将图的节点分为两组，最大化组间边的权重之和。

| 数据集 | 位置 | 说明 |
|:------|:-----|:----|
| **训练数据** | `problems/maxcut/datasets/` | 64 组，100 节点 G-set 风格随机图 |
| **测试数据** | `problems/maxcut/datasets/` | 50/100/200 节点各 10 组 |

- **函数签名**：`assign_node(node_id, unassigned_nodes, adjacency_matrix, current_partition) → side`
- **标准解**：贪心随机重启 + 多 trials 近似最优
- **特点**：返回 0 或 1（划分到哪一侧），每次决策一个节点

---

### 🧩 如何添加自定义问题情景

参考以上任一情景的实现，在 `problems/` 下创建新目录，提供以下文件：

```
problems/<new_problem>/
├── __init__.py              # 空文件，标记为包
├── heuristic.py             # 缺省启发式算法
├── train_eval.py            # 训练评估（必须导出 heuristic_solve_dynamic）
├── test_eval.py             # 测试评估（必须导出 heuristic_solve_static）
├── start_evo.py             # CLI 启动脚本
├── image.py                 # 可视化函数
├── generate_datasets.py     # 数据集生成脚本
├── datasets/                # 预生成数据集 (.pkl)
└── result/                  # 输出目录
```

然后在 `app.py` 的 `PROBLEM_CONFIG_MAP` 中添加对应配置，Web 端会自动载入。

---

## 📜 项目来源

本项目为 **毕业设计：基于大模型的启发式组合优化算法生成机制** 的代码实现。

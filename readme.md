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

---

## 📑 目录

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
- [📖 问题情景：TSP](#-问题情景tsp)
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
├── problems/
│   └── tsp/                       # 示例：旅行商问题 (TSP)
│       ├── train_eval.py          # 训练评估
│       ├── test_eval.py           # 测试评估
│       ├── start_evo.py           # CLI 启动项
│       ├── heuristic.py           # 缺省启发式
│       ├── result/                # 生成结果
│       │   ├── population/        # 各阶段种群 JSON
│       │   └── best/              # 各阶段最优启发式 JSON
│       └── datasets/              # 预生成数据集
├── static/                        # Web 前端静态文件
│   ├── NSEH_login.css/.js
│   ├── NSEH_main.css/.js
│   └── NSEH_rank.css/.js
├── templates/                     # HTML 模板
│   ├── NSEH_login.html
│   ├── NSEH_main.html
│   └── NSEH_rank.html
├── app.py                         # Web 应用入口
├── readme.md                      # 本文件
├── requirements.txt               # 依赖
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

打开 Web 应用后需登录。账号密码设置在 `user_info.csv` 中：

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

- 📈 **实时曲线**：查看各代种群最优适应度变化折线图
- 🏆 **排行榜**：进化结束后查看系统内各用户的最优适应度排名

---

## 📖 问题情景：TSP

本项目以 **旅行商问题 (TSP)** 为示例情景。如需在其他问题使用本架构，参照 TSP 的实现即可。

### TSP 数据

| 数据集 | 位置 | 说明 |
|:------|:-----|:----|
| **训练数据** | `problems/tsp/train_data/` | 64 组 TSP100 实例，[0,1]² 空间随机生成（参考 EoH），`.pkl` 格式 |
| **测试数据** | `problems/tsp/test_data/` | TSP10/20/100/200 实例，`.pkl` 格式 |

### 评估方法 (`problems/tsp/eval.py`)

读取数据 → 加载 Concorde 标准解 → 与启发式结果对比 → 计算适应度。

单独运行可测试当前 `heuristic.py` 在测试集上的性能。

### 缺省算法 (`problems/tsp/heuristic.py`)

TSP 的常见启发式算法，可被替换为其他算法。

---

## 📜 项目来源

本项目为 **毕业设计：基于大模型的启发式组合优化算法生成机制** 的代码实现。

# NSEH - 基于大模型的启发式组合优化算法自动生成机制

---

## 项目简述

本项目使用LLM生成启发式，构建启发式种群，在预备数据集上执行启发式的算法并与标准解进行比较计算适应度，然后根据适应度的排名保留效益最好的启发式。

项目结构如下：

```PlainText
/NSEH
├── core/
│   ├── __init__.py
│   ├── llm_interface.py      # LLM通信模块
│   ├── prompt_template.py    # 提示词模版模块
│   ├── generator.py          # 启发式生成器
│   └── evolution.py          # 进化框架主逻辑
├── problems/
│   └── tsp/                  # 示例问题情景_旅行商问题(TSP)
│       ├── train_eval.py     # 用于训练过程中的评估
│       ├── test_eval.py      # 用于测试过程中的评估
│       ├── start_evo.py      # tsp问题情景的启动项
│       ├── heuristic.py      # 缺省启发式
│       ├── result/           # 生成结果目录
│       │   ├──population/    # 存放各阶段的种群json
│       │   └──best/          # 存放各阶段的最优启发式json
│       └── datasets/         # 预生成数据集
├── static/
│   ├── NSEH_login.css        # web应用登录页面css配置
│   ├── NSEH_login.js         # web应用登录页面js代码
│   ├── NSEH_main.css         # web应用主界面css配置
│   ├── NSEH_main.js          # web应用主界面js代码
│   ├── NSEH_rank.css         # web应用排行榜css配置
│   └── NSEH_rank.js          # web应用排行榜js代码
├── templates/
│   ├── NSEH_login.html       # web应用登录页面html模版
│   ├── NSEH_main.html        # web应用页面html模版
│   └── NSEH_rank.html        # web应用排行榜html模版
├── app.py                    # web应用启动项
├── readme.md                 # 本说明文档
├── requirements.txt          # 依赖项文档
├── user_info.csv             # 用户账密及信息表
└── web.bat                   # web应用启动脚本
```

### 问题情形
本项目以TSP问题情形作为示例情形。如用户想在其他情形使用本架构，可以参照TSP情形进行评估算法的实现和配置。

TSP情形位于目录 `/problem/tsp` ， 包含训练用数据、测试用数据、评估方法、缺省算法。

- 训练用数据：位于 `/problem/tsp/train_data` 内，仿照EoH的生成方法，在[0,1]^2空间随机生成的TSP100实例，共64组，每组包含这些点的坐标和距离矩阵，文件存储为.pkl
- 测试用数据：位于 `/problem/tsp/test_data` 内，仿照EoH，取TSP10\20\100\200，可单独执行启发式评估计算你选取的启发式的计算时间和适应度，文件存储为.pkl
- 评估方法：位于 `/problem/tsp/eval.py`
  ，仿照EoH，读取数据；加载基于Concorde的标准解方法，求解，与框架动态加载的启发式的计算结果进行对比，得到适应度的值；单独运行可以加载该目录下heuristic.py内的算法在测试用数据下的性能并打印出来
- 缺省算法：`/problem/tsp/heuristic.py`，该情景下问题的一个常见算法，可以被替换为任何想用来进行单独评估的算法


### 关于启发式种群

本项目在进化过程中，培养多代启发式种群（Population），模仿自然选择法则进行进化。 每一代的种群包含两部分：种群内的启发式 (Heuristic)，和当前阶段的记忆(Memory)。

- 启发式包含
    - 概念（Concept）：以自然语言描述启发式的思想和方法，字符串
    - 算法（Algorithm）：一个可执行的python函数，函数名、输入和输出都是固定的，字符串
    - 特征（Feature）：算法的思想特点，比如“贪婪搜索“，字符串数组
    - 适应度（Objective）：评价算法效益的数值指标，数值

- 记忆（Memory）包含
    - 积极特征（Positive Feature）：以往进化过程中取得优势的启发式的特征组合，比如“贪婪搜索+随机抖动”，字符串数组
    - 消极特征（Negative Feature）：以往进化过程中取得劣势的启发式的特征组合，字符串数组
  
![图片1.png](image/%E5%9B%BE%E7%89%871.png)

### 进化流程

![图片2.png](image/%E5%9B%BE%E7%89%872.png)

0. 在开始时，设置种群容量（启发式个数）为`N`，进化种群数`M`，使用启发式生成器初始化`N`个启发式，将新种群存储至文件


1. 使用启发式生成器和启发式评估器，生成启发式加入包括旧启发式的新种群

- 1.1 **Mutation突变**：提示 LLM 设计`k1`个与现有种群启发式算法尽可能不同的新启发式算法
- 1.2 **Hybridization 杂交**：按照上一轮的优势排名，选取前`k2`个启发式，两两进行杂交，让 LMM 综合其思路生成一个新启发式
- 1.3 **Optimization 优化**：对于每一个现有算法，让 LMM 调整其参数值、对其进行复杂度层面的优化，或精简其结构，生成新启发式算法

2. 筛选启发式，获得新一代种群

- 2.1 **Elimination 淘汰**：在前三个阶段后，对于新的种群，按照适应度给每个启发式排名，保留前`N`个启发式作为新的种群，将新种群存储至文件
- 2.2 **Reflection 反思**：在淘汰前将排名最靠前的k3个启发式和排名最靠后的k3个启发式的特征组合分别纳入积极特征和消极特征，删去重复的特征组合

3. 在2完成后，如未到达停止条件，如进化种群数未达到M，返回1；循环结束后进程结束


![图片3.png](image/%E5%9B%BE%E7%89%873.png)

---

## 依赖项
在使用前请先安装依赖。

```bash
pip install -r requirements.txt
```

另外，用户需自行申请api-key。本项目实现时采用Deepseek作为示例LLM。
* **DS API 文档说明**: [DeepSeek API文档](https://api-docs.deepseek.com/zh-cn/api/deepseek-api/)
* **API_BASE**: "https://api.deepseek.com"

---
## Web应用

### 启动项（app.py)

启动根目录脚本web.bat，或在终端执行app.py

```bash
python app.py
```

### 登录

web应用端需登录，用户账号密码设置位于user_info.csv，表格示例数据如下

| 用户名   | 账号  | 密码     | 用户最优适应度 |
|:------|:----|:-------|:--------|
| 用户_01 | 213111111 | 123456 | null    |

 - 在用户登录后，生成的最优启发式适应度会被录入该csv文件

### 进化设置

在配置页面进行参数配置，随后点击“开始进化”。


| 参数名称                 | 参数类型 | 该参数的意义                      | 缺省值                           |
| :------------------- | :--- | :-------------------------- | :---------------------------- |
| population\_capacity | int  | 种群容量                        | 7                             |
| num\_generations     | int  | 进化迭代次数                      | 5                             |
| num\_mutation        | int  | 每次迭代生成突变启发式数                | 3                             |
| num\_hybridization   | int  | 每次迭代参与交配的启发式数               | 3                             |
| ascend               | bool | 是否在种群中按适应度升序排列启发式（即适应度是否取小） | True                          |
| base\_url            | 字符串  | LLM API接口的base url          | <https://api.deepseek.com/v1> |
| llm\_model            | 字符串   | 所需选用的LLM模型     | deepseek-chat             |
| api\_key              | 字符串   | LLM的API key    | /                         |
| problem               | 字符串   | 问题情景描述         | TSP问题，即……                 |
| fun\_name             | 字符串   | 函数名            | select\_next\_node        |
| fun\_args             | 字符串列表 | 函数参数           | \[‘current\_node’,…]      |
| fun\_return           | 字符串列表 | 函数返回值          | \["next\_node"]           |
| fun\_notes            | 字符串   | 注意事项           | …所有数据均为numpy数组…           |
| problem\_path         | 字符串   | 问题目录（根目录下相对路径） | problems/tsp              |
| train\_data\_name     | 字符串   | 训练数据文件名        | train\_data\_tsp.pkl      |
| train\_solution\_name | 字符串   | 标准解文件名         | train\_data\_solution.pkl |

### 进化过程

在进化页面将动态显示进化过程中各种群及其成员启发式
 - 可点击**单个启发式卡片**查看其构成及代码实现。
 - 可控制进化过程**暂停/继续**
 - 可自定义**prompt模版**，以TSP问题情景为例(如下)

#### 函数要求

```plain text
用Python实现一个名为select_next_node的函数。
该函数应接受4个输入：'current_node', 'destination_node', 'unvisited_nodes', 'distance_matrix'；
函数应返回1个输出：'next_node'。
'current_node','destination_node', 'next_node', 和 'unvisited_nodes'是节点ID，distance_matrix是节点的距离矩阵。所有数据均为Numpy数组。
```

#### 进化策略描述

**MUTATION突变**
```plain text
请你设计一个与现有的这些启发式算法尽可能不同的新启发式算法。
```

**HYBRIDIZATION繁殖**
```plain text
请你综合现有的这些启发式算法的关键思想，设计一个新的启发式算法。
```

**OPTIMIZATION优化**
```plain text
请你对现有的这个启发式进行优化，使用包括但不限于调整其参数值、对其进行复杂度层面的优化或精简其结构等方式，得到一个新的启发式算法。
```

#### 分析过程
```plain text
请你梳理所有信息，进行一个长度在200字内的分析。
你可以将构思新启发式需要纳入考量的条件列举出来，并分析该如何进行设计构思或改进，以得到新的启发式。
不要进行任何代码实现，只给出修改的目标，并构思如何设计新启发式。
```

当进化过程遭遇瓶颈，即多轮进化无法得到适应度更优的启发式时，用户可以尝试对模版进行自定义修改，以突破种群进化瓶颈。

### 进化结果

在结果页面可以随时查看进化过程中各种群最优启发式的适应度变化，历代种群适应度以折线图形式呈现。

进化过程结束后，可以打开排行榜查看当前系统内各用户的最有适应度排名。

---
## CLI运行
也可从命令行运行本项目，CLI启动项位于目录`problems/tsp/start_evo.py`。

```bash
cd problems/tsp
python start_evo.py
```

在`start_evo.py`中配置参数可以在命令行运行进化框架。

| **参数名称**            | **缺省值** | **意义**                |
|---------------------|---------|-----------------------|
| POPULATION_CAPACITY | 7       | 种群容量，种群中启发式实例的数量      |
| NUM_GENERATIONS     | 5       | 种群迭代数，即进行多少轮进化        |
| NUM_MUTATION        | 3       | 每轮中突变的启发式数(`k1`)      |
| NUM_HYBRIDIZATION   | 3       | 每轮中参与杂交的启发式数(`k2`)    |
| NUM_REFLECTION      | 3       | 反思过程中特征被记住的启发式数(`k3`) |

---

## 项目来源

本项目为毕业设计 **基于大模型的启发式组合优化算法生成机制** 的项目代码实现

本项目设计灵感参考 [**EoH**](https://github.com/FeiLiu36/EoH/blob/main/README_CN.md)

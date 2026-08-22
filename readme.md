# 🧬 NSEH - LLM-Based Automatic Generation of Heuristic Combinatorial Optimization Algorithms

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/LLM-DeepSeek-orange" alt="LLM">
  <img src="https://img.shields.io/badge/Framework-Flask-black?logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/status-beta-yellow" alt="Status">
  <img src="https://img.shields.io/github/stars/IvesSilent/NSEH?style=flat" alt="Stars">
</p>

<p align="center">
  <b>Natural Selection Heuristic Evolution</b> · Automatically generate & evolve heuristics with LLMs
</p>

<p align="center">
  <a href="readme_CN.md">🇨🇳 简体中文</a> ·
  <a href="publication/CHANGELOG.md">✨ Changelog</a>
</p>

---

## 📑 Table of Contents

- [🚀 Introduction](#-introduction)
- [🧬 Core Concept: Heuristic Population](#-core-concept-heuristic-population)
- [🔄 Evolution Pipeline](#-evolution-pipeline)
- [⚡ Quick Start](#-quick-start)
  - [Install Dependencies](#install-dependencies)
  - [Web Launch](#web-launch)
  - [CLI Launch](#cli-launch)
- [📂 Project Structure](#-project-structure)
- [⚙️ Configuration](#-configuration)
  - [Evolution Parameters](#evolution-parameters)
  - [LLM & Problem Config](#llm--problem-config)
- [🌐 Web App Guide](#-web-app-guide)
  - [Login](#login)
  - [Language Switching](#language-switching)
  - [Evolution Settings](#evolution-settings)
  - [Evolution Process](#evolution-process)
  - [Evolution Results](#evolution-results)
  - [Leaderboard](#leaderboard)
- [📖 Supported Problems](#-supported-problems)
- [📜 Origin](#-origin)

---

## 🚀 Introduction

This project uses **LLMs to generate heuristic algorithms**, builds a heuristic population, runs each heuristic on prepared datasets, compares its objective against reference solutions, and keeps the best-performing heuristics by fitness ranking — **mimicking natural selection** to let algorithms evolve automatically.

> 💡 **Inspiration**: Built upon the evolutionary idea of [EoH (Evolution of Heuristic)](https://github.com/FeiLiu36/EoH/blob/main/README_CN.md), with extensions to LLM interaction strategies and population memory mechanisms.

---

## 🧬 Core Concept: Heuristic Population

The evolution process cultivates a multi-generation **heuristic population**, where each generation consists of:

### Heuristic Individual

| Dimension | Description |
|:----|:----|
| **Concept** | Natural-language description of the heuristic's idea |
| **Algorithm** | Executable Python function (fixed name/inputs/outputs) |
| **Feature** | Tags describing the algorithmic idea, e.g. "greedy search" (string array) |
| **Objective** | Numeric metric evaluating the heuristic's effectiveness |

### Population Memory

The memory mechanism uses a **hierarchical tag memory system** (v2.5):

| Level | Description |
|:----|:-----|
| **Scenario Classification Tree** | Each problem scenario maintains its own tag taxonomy (constructive, local search, hybrid strategy classes, etc.) |
| **Positive Features** | Advantageous feature combinations from past evolutions, archived by fitness |
| **Negative Features** | Disadvantageous feature combinations from past evolutions |
| **LLM Structured Prompts** | Memory is presented as structured text in the prompt to guide the LLM toward better strategies |

![Heuristic population structure: individuals have concept, algorithm, feature and objective; memory contains positive and negative features](image/%E7%A7%8D%E7%BE%A4%E7%BB%93%E6%9E%84%E5%9B%BE.png)

---

## 🔄 Evolution Pipeline

![Evolution overview: initialize → generate (mutation/hybridization/optimization) → select (eliminate/reflect) → loop](image/%E8%BF%9B%E5%8C%96%E6%B5%81%E7%A8%8B%E5%9B%BE.png)

### Stage 0 — Initialization
Set population capacity `N` and number of generations `M`, then generate the initial heuristic population.

### Stage 1 — Generate New Heuristics

| Step | Operation | Description |
|:---|:----|:----|
| 🧬 **1.1 Mutation** | Prompt the LLM to design `k1` new algorithms that are **as different as possible** | Introduce diversity |
| 🧪 **1.2 Hybridization** | Pick the top `k2` heuristics and **cross them pairwise**; the LLM synthesizes their ideas | Preserve advantages |
| ⚡ **1.3 Optimization** | **Tune/simplify/optimize** each algorithm to produce an optimized version | Refine & converge |

### Stage 2 — Selection & Reflection

| Step | Operation | Description |
|:---|:----|:----|
| 🗑️ **2.1 Elimination** | Keep the top `N` heuristics by fitness ranking | Survival of the fittest |
| 💡 **2.2 Reflection** | Record features of the best `k3` and worst `k3` heuristics into positive/negative memory | Accumulate experience |

### Stage 3 — Loop
Return to Stage 1 if the generation count `M` is not reached; otherwise finish.

---

## ⚡ Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

> ⚠️ **You need to apply for an API Key yourself.** DeepSeek is used by default: [Apply for DeepSeek API](https://api-docs.deepseek.com/)
> - `API_BASE`: `https://api.deepseek.com`
> - Fill in `api_key` on the Web config page or in `start_evo.py`

### Web Launch

```bash
python app.py
# or double-click web.bat (Windows)
```

Open `http://localhost:5000` in your browser to reach the login page.

### CLI Launch

```bash
cd problems/tsp
python start_evo.py
```

CLI parameters are configured directly in `start_evo.py`:

| Parameter | Default | Description |
|:----|:------|:----|
| `POPULATION_CAPACITY` | 7 | Population capacity |
| `NUM_GENERATIONS` | 5 | Number of generations |
| `NUM_MUTATION` | 3 | Mutations per round (`k1`) |
| `NUM_HYBRIDIZATION` | 3 | Hybridizations per round (`k2`) |
| `NUM_REFLECTION` | 3 | Reflection features (`k3`) |

---

## 📂 Project Structure

```
/NSEH
├── core/                          # Core framework
│   ├── llm_interface.py           # LLM communication module
│   ├── prompt_template.py         # Prompt templates (Chinese/English)
│   ├── generator.py               # Heuristic generator
│   ├── evolution.py               # Evolution framework main logic
│   └── tag_memory.py              # Hierarchical tag memory system (v2.5)
├── problems/                      # Problem scenario plugins
│   ├── tsp/                       # TSP Travelling Salesman Problem
│   │   ├── train_eval.py          # Training evaluation
│   │   ├── test_eval.py           # Test evaluation
│   │   ├── start_evo.py           # CLI entry
│   │   ├── heuristic.py           # Default heuristic
│   │   ├── generate_datasets.py   # Dataset generator
│   │   ├── datasets/              # Pre-generated datasets
│   │   └── result/                # Output results
│   ├── cvrp/                      # CVRP Capacitated Vehicle Routing Problem
│   ├── knapsack/                  # 0/1 Knapsack Problem
│   ├── pfsp/                      # PFSP Permutation Flow Shop Scheduling
│   ├── maxcut/                    # MaxCut Maximum Cut Problem
│   ├── binpacking/                # Bin Packing Problem
│   ├── graphcoloring/             # Graph Coloring Problem
│   ├── jsp/                       # Job Shop Scheduling Problem
│   ├── setcover/                  # Set Cover Problem
│   ├── vertexcover/               # Minimum Vertex Cover Problem
│   ├── mtsp/                      # Multiple Travelling Salesman Problem
│   ├── vrptw/                     # VRPTW (Vehicle Routing with Time Windows)
│   ├── orienteering/              # Orienteering Problem
│   ├── steinertree/               # Steiner Tree Problem
│   ├── maxclique/                 # Maximum Clique Problem
│   ├── smtwt/                     # Single Machine Total Weighted Tardiness
│   ├── parmachine/                # Parallel Machine Scheduling (P||Cmax)
│   ├── qap/                       # Quadratic Assignment Problem
│   ├── kcenter/                   # k-Center Problem
│   └── partition/                 # Number Partitioning Problem
├── static/                        # Web frontend
│   ├── i18n.js                    # Chinese/English i18n framework (v5.1)
│   ├── NSEH_login.css             # Login page styles
│   ├── NSEH_login.js              # Login page logic
│   ├── NSEH_main.css              # Main UI styles (v5 Refined)
│   ├── NSEH_main.js               # Main UI logic (evolution, results)
│   ├── NSEH_ux.js                 # UX enhancements (animations, toasts, etc.)
│   ├── NSEH_rank.css              # Leaderboard styles
│   └── NSEH_rank.js               # Leaderboard logic
├── templates/                     # HTML templates
│   ├── NSEH_login.html            # Login page
│   ├── NSEH_main.html             # Main UI (settings + evolution + results)
│   └── NSEH_rank.html             # Leaderboard
├── image/                         # Documentation images
│   ├── 种群结构图.png
│   └── 进化流程图.png
├── externel/                      # External tools
│   ├── concorde_solve.py          # Concorde TSP solver
│   ├── read_tsp_data.py           # TSP data reader
│   └── tsp_data_generate.py       # TSP data generator
├── publication/                   # Publication section
│   └── CHANGELOG.md               # Changelog (Release Notes)
├── app.py                         # Web app entry
├── readme.md                      # English docs (shown by default on GitHub)
├── readme_CN.md                   # Chinese docs
├── requirements.txt               # Dependencies
├── .config_cache.json             # Config cache (auto-generated)
├── nseh.db                        # SQLite database (auto-generated)
├── user_info.csv                  # User credentials table (auto-generated)
└── web.bat                        # Windows launch script
```

---

## ⚙️ Configuration

### Evolution Parameters

| Parameter | Type | Description | Default |
|:----|:----|:-----|:------|
| `population_capacity` | `int` | Population capacity | 7 |
| `num_generations` | `int` | Number of evolution iterations | 5 |
| `num_mutation` | `int` | Mutated heuristics per generation | 3 |
| `num_hybridization` | `int` | Hybridized heuristics per generation | 3 |
| `ascend` | `bool` | Whether smaller fitness is better | `True` |

### LLM & Problem Config

| Parameter | Type | Description | Default |
|:----|:----|:-----|:------|
| `base_url` | `str` | LLM API endpoint | `https://api.deepseek.com/v1` |
| `llm_model` | `str` | Model name | `deepseek-v4-flash` |
| `api_key` | `str` | Your API Key | required |
| `problem` | `str` | Problem scenario description | TSP problem, i.e. ... |
| `fun_name` | `str` | Target function name | `select_next_node` |
| `fun_args` | `list` | Function arguments | `['current_node', …]` |
| `fun_return` | `list` | Function return values | `["next_node"]` |
| `fun_notes` | `str` | Notes | All data are numpy arrays... |
| `problem_path` | `str` | Problem directory (relative) | `problems/tsp` |
| `train_data_name` | `str` | Training data filename | `train_data_tsp.pkl` |
| `train_solution_name` | `str` | Reference solution filename | `train_data_solution.pkl` |

---

## 🌐 Web App Guide

### Login

You must log in to use the web app. The eye icon on the right of the password field toggles password visibility. Account credentials are stored in `user_info.csv`:

| Username | Account | Password | Best Fitness |
|:------|:----|:-----|:------------|
| 用户_01 | 213111111 | 123456 | null |

After login, the best heuristic fitness you generate is automatically recorded in this file.

### Language Switching

A **language toggle button** in the top-right corner of the UI switches between **中文 / English**:

- **Chinese mode**: UI text and preset prompt templates are in Chinese; the button shows `English`
- **English mode**: UI text and preset prompt templates are in English; the button shows `中文`
- The language preference is saved in the browser and restored automatically on next visit
- Switching also affects the **preset prompt templates** (mutation/hybridization/optimization/analysis): if evolution starts in English mode, the LLM receives English prompts

### Evolution Settings

On the "Evolution Settings" page you can configure:
- **Evolution parameters**: population size, generations, mutation/hybridization/reflection counts
- **LLM config**: model selection, API Key
- **Problem selection**: switch among supported problem scenarios via the dropdown

Click "Start Evolution" to begin. The config is cached automatically to `.config_cache.json` and restored on the next launch.

### Evolution Process

The evolution page dynamically displays each generation's population and its member heuristics:

- 🖱️ **Click a heuristic card** → view its concept description and code implementation
- 🔽 **Collapse/expand generations** → inspect the population of a specific generation
- ⏯️ **Pause/Resume** → control the pace of evolution
- ✏️ **Edit Prompt templates** → modify templates to break through bottlenecks
- 📂 **Load snapshot** → load historical evolution records

<details>
<summary>📝 Click to view the preset prompt templates (English example)</summary>

#### Function Requirements

```plain text
Implement a Python function named select_next_node.
The function should accept 4 input(s): 'current_node', 'destination_node', 'unvisited_nodes', 'distance_matrix';
The function should return 1 output(s): 'next_node'.
'current_node','destination_node', 'next_node', and 'unvisited_nodes' are node IDs,
distance_matrix is the distance matrix of nodes. All data are numpy arrays.
```

#### Evolution Strategies

**MUTATION**
```plain text
Design a new heuristic algorithm that is as different as possible from the existing heuristic algorithms.
```

**HYBRIDIZATION**
```plain text
Synthesize the key ideas of the existing heuristic algorithms and design a new heuristic algorithm.
```

**OPTIMIZATION**
```plain text
Optimize the existing heuristic, using methods including but not limited to tuning its parameter values,
optimizing its time/space complexity, or simplifying its structure, to obtain a new heuristic algorithm.
```

#### Analysis

```plain text
Please review all the information and provide an analysis within 200 characters.
You may list the conditions that need to be considered when designing a new heuristic and analyze how to
design or improve it, so as to obtain a new heuristic.
Do not implement any code. Only give the improvement goals and describe how to design the new heuristic.
```

</details>

### Evolution Results

- 📈 **Real-time curves**: line charts showing the best fitness of each generation
  - Five views: Best per Gen / Best+Mean+Variance / Top-3 Bars / All Heuristics / Token Usage
- 🔗 **View result details**: jump to the detailed analysis page
- 📊 **Switch chart tabs**: switch visualization dimensions on demand

### Leaderboard

- 🏆 Visit the `/rank` page after evolution completes
- Displays the best-fitness ranking of all users in the system
- Supports returning to the main UI to continue experiments

---

## 📖 Supported Problems

The project currently supports **20 combinatorial optimization problem scenarios**, all switchable via the "Problem Selection" dropdown on the Web UI.

<details>
<summary><b>📋 Click to expand — detailed description of all 20 problem scenarios</b> (datasets / function signatures / reference solutions)</summary>


### 🛤️ TSP (Travelling Salesman Problem)

> **Goal**: Given the coordinates of a set of nodes, find the shortest route that visits each node exactly once and returns to the origin.

| Dataset | Location | Description |
|:------|:-----|:----|
| **Training** | `problems/tsp/datasets/` | 64 TSP100 instances, randomly generated in [0,1]² (following EoH) |
| **Test** | `problems/tsp/datasets/` | 10 instances each for TSP10/20/50/100/200 |

- **Signature**: `select_next_node(current_node, destination_node, unvisited_nodes, distance_matrix) → next_node`
- **Evaluators**: `train_eval.py` (dynamic) / `test_eval.py` (static + timing)
- **Reference solutions**: Concorde exact solver

---

### 🚚 CVRP (Capacitated Vehicle Routing Problem)

> **Goal**: Plan shortest routes for a fleet under vehicle capacity constraints to serve all customer nodes.

| Dataset | Location | Description |
|:------|:-----|:----|
| **Training** | `problems/cvrp/datasets/` | 64 CVRP100 instances, capacity 200 |
| **Test** | `problems/cvrp/datasets/` | 10 instances each for CVRP50/100/200 |

- **Signature**: `find_best_route(current_node, remaining_demands, vehicle_capacity, current_load, distance_matrix, demand_list) → next_node`
- **Reference solutions**: Clarke-Wright savings algorithm (following EoH setup)
- **Feature**: must respect capacity constraints when deciding which customer to serve next

---

### 🎒 Knapsack (0/1 Knapsack Problem)

> **Goal**: Choose a subset of items within the knapsack capacity to maximize total value.

| Dataset | Location | Description |
|:------|:-----|:----|
| **Training** | `problems/knapsack/datasets/` | 64 instances, 150 items |
| **Test** | `problems/knapsack/datasets/` | 10 instances each for 50/100/150 items |

- **Signature**: `select_item(current_index, remaining_capacity, weights, values, num_items) → take_item`
- **Reference solutions**: dynamic programming exact solution
- **Feature**: decide item by item whether to take it, returning 0/1

---

### 🏭 PFSP (Permutation Flow Shop Scheduling Problem)

> **Goal**: Schedule n jobs on m machines to minimize the makespan.

| Dataset | Location | Description |
|:------|:-----|:----|
| **Training** | `problems/pfsp/datasets/` | 64 instances, 20 jobs × 5 machines |
| **Test** | `problems/pfsp/datasets/` | 10 instances each for 10×5 / 20×5 / 50×10 |

- **Signature**: `select_next_job(unscheduled_jobs, current_schedule, processing_times, num_machines) → next_job`
- **Reference solutions**: NEH heuristic (standard baseline in the EoH paper)
- **Feature**: build the job processing sequence to minimize machine idle/waiting time

---

### ✂️ MaxCut (Maximum Cut Problem)

> **Goal**: Partition graph nodes into two groups to maximize the total weight of edges between groups.

| Dataset | Location | Description |
|:------|:-----|:----|
| **Training** | `problems/maxcut/datasets/` | 64 instances, 100-node G-set style random graphs |
| **Test** | `problems/maxcut/datasets/` | 10 instances each for 50/100/200 nodes |

- **Signature**: `assign_node(node_id, unassigned_nodes, adjacency_matrix, current_partition) → side`
- **Reference solutions**: greedy random restart + multiple trials near-optimal
- **Feature**: return 0 or 1 (which side to assign), deciding one node at a time

---


### 📦 Bin Packing (1D Bin Packing Problem)

> **Goal**: Pack items with given sizes into the minimum number of equal-capacity bins.

| Dataset | Location | Description |
|:------|:-----|:----|
| **Training** | `problems/binpacking/datasets/` | 64 instances, 100 items, bin capacity 100 |
| **Test** | `problems/binpacking/datasets/` | 10 instances each for 50×100 / 100×150 / 200×200 |

- **Signature**: `place_item(item_size, remaining_capacities, item_sizes, num_items) → bin_index`
- **Reference solutions**: Best-Fit Decreasing (BFD)
- **Feature**: return -1 to open a new bin when no opened bin fits

---

### 🎨 Graph Coloring (Graph Coloring Problem)

> **Goal**: Color graph nodes so adjacent nodes differ, minimizing the number of colors.

| Dataset | Location | Description |
|:------|:-----|:----|
| **Training** | `problems/graphcoloring/datasets/` | 64 instances, 60 nodes, edge density 0.5 |
| **Test** | `problems/graphcoloring/datasets/` | 10 instances each for 30 / 60 / 100 nodes |

- **Signature**: `choose_color(node_id, adjacency_matrix, current_colors, num_colors_used) → color`
- **Reference solutions**: DSATUR greedy coloring

---

### 🏭 JSP (Job Shop Scheduling Problem)

> **Goal**: Schedule jobs with operation-machine sequences to minimize the makespan.

| Dataset | Location | Description |
|:------|:-----|:----|
| **Training** | `problems/jsp/datasets/` | 64 instances, 10 jobs × 5 machines |
| **Test** | `problems/jsp/datasets/` | 10 instances each for 10×5 / 20×10 / 30×15 |

- **Signature**: `select_next_job(available_operations, job_progress, operation_times, machine_ready_times, machine_of_op) → next_job`
- **Reference solutions**: multi-rule greedy (SPT/MWKR/LPT) + random restarts

---

### 🗂️ Set Cover (Set Cover Problem)

> **Goal**: Select minimum-cost sets covering all elements of the universe.

| Dataset | Location | Description |
|:------|:-----|:----|
| **Training** | `problems/setcover/datasets/` | 64 instances, 100 elements, 50 sets |
| **Test** | `problems/setcover/datasets/` | 10 instances each for 100×50 / 200×100 / 300×150 |

- **Signature**: `select_next_set(uncovered_elements, set_membership, set_costs) → set_index`
- **Reference solutions**: randomized greedy + redundant-set elimination

---

### 🛡️ Vertex Cover (Minimum Vertex Cover Problem)

> **Goal**: Select the minimum number of vertices so every edge has an endpoint in the cover.

| Dataset | Location | Description |
|:------|:-----|:----|
| **Training** | `problems/vertexcover/datasets/` | 64 instances, 60 nodes, edge density 0.3 |
| **Test** | `problems/vertexcover/datasets/` | 10 instances each for 40 / 80 / 120 nodes |

- **Signature**: `select_next_vertex(uncovered_edges, adjacency_matrix, current_cover) → vertex_index`
- **Reference solutions**: multi-start greedy + redundant-vertex elimination

---

### 🧑‍🤝‍🧑 mTSP (Multiple Travelling Salesman Problem)

> **Goal**: Plan multiple depot-returning tours covering all customers, minimizing total distance.

| Dataset | Location | Description |
|:------|:-----|:----|
| **Training** | `problems/mtsp/datasets/` | 64 instances, 100 nodes, 3 salesmen |
| **Test** | `problems/mtsp/datasets/` | 10 instances each for 50×3 / 100×4 / 200×5 |

- **Signature**: `select_next_node(current_node, unvisited_nodes, distance_matrix, remaining_salesmen) → next_node`
- **Reference solutions**: multi-start nearest neighbor

---

### ⏰ VRPTW (Vehicle Routing Problem with Time Windows)

> **Goal**: Serve all customers within time windows and capacity, minimizing total distance.

| Dataset | Location | Description |
|:------|:-----|:----|
| **Training** | `problems/vrptw/datasets/` | 64 instances, 50 customers |
| **Test** | `problems/vrptw/datasets/` | 10 instances each for 50 / 100 / 200 customers |

- **Signature**: `select_next_customer(current_node, current_time, remaining_demands, vehicle_capacity, current_load, distance_matrix, demand_list, time_windows, service_times) → next_node`
- **Reference solutions**: multi-strategy greedy (EDD/distance/slack) + random restarts
- **Feature**: return -1 to return to the depot when no customer is feasible

---

### 🧭 Orienteering (Orienteering Problem)

> **Goal**: Collect maximum profit within a distance budget on a route from and back to the start.

| Dataset | Location | Description |
|:------|:-----|:----|
| **Training** | `problems/orienteering/datasets/` | 64 instances, 100 nodes |
| **Test** | `problems/orienteering/datasets/` | 10 instances each for 50 / 100 / 200 nodes |

- **Signature**: `select_next_node(current_node, visited, remaining_profits, distance_matrix, budget_left, total_profit) → next_node`
- **Reference solutions**: greedy + local search (insert / remove-insert)

---

### 🌲 Steiner Tree (Steiner Tree Problem)

> **Goal**: Connect all terminal nodes with minimum total edge weight (Steiner points allowed).

| Dataset | Location | Description |
|:------|:-----|:----|
| **Training** | `problems/steinertree/datasets/` | 64 instances, 80 nodes, 12 terminals |
| **Test** | `problems/steinertree/datasets/` | 10 instances each for 50×8 / 100×15 / 200×20 |

- **Signature**: `select_next_terminal(current_tree, unconnected_terminals, adjacency_matrix, distances) → terminal_index`
- **Reference solutions**: KMB algorithm (terminal MST + shortest-path expansion)

---

### 🔷 MaxClique (Maximum Clique Problem)

> **Goal**: Find the largest set of pairwise-adjacent vertices in an undirected graph.

| Dataset | Location | Description |
|:------|:-----|:----|
| **Training** | `problems/maxclique/datasets/` | 64 instances, 60 nodes, density 0.5 |
| **Test** | `problems/maxclique/datasets/` | 10 instances each for 30 / 60 / 100 nodes |

- **Signature**: `select_next_vertex(current_clique, candidate_vertices, adjacency_matrix) → vertex_index`
- **Reference solutions**: multi-start greedy (degree priority)

---

### ⚖️ SMTWT (Single Machine Total Weighted Tardiness)

> **Goal**: Minimize the total weighted tardiness ΣwT on a single machine.

| Dataset | Location | Description |
|:------|:-----|:----|
| **Training** | `problems/smtwt/datasets/` | 64 instances, 50 jobs |
| **Test** | `problems/smtwt/datasets/` | 10 instances each for 50 / 100 / 200 jobs |

- **Signature**: `select_next_job(unscheduled_jobs, current_time, processing_times, due_dates, weights) → next_job`
- **Reference solutions**: WSPT/EDD/MS greedy + adjacent-swap local search

---

### 🖥️ ParMachine (Parallel Machine Scheduling P||Cmax)

> **Goal**: Assign jobs to identical parallel machines minimizing the makespan.

| Dataset | Location | Description |
|:------|:-----|:----|
| **Training** | `problems/parmachine/datasets/` | 64 instances, 100 jobs, 4 machines |
| **Test** | `problems/parmachine/datasets/` | 10 instances each for 50×4 / 100×8 / 200×8 |

- **Signature**: `assign_job(job_id, machine_loads, processing_times, num_machines) → machine_index`
- **Reference solutions**: LPT + local search (moves & swaps)

---

### 🔀 QAP (Quadratic Assignment Problem)

> **Goal**: Assign facilities to locations minimizing total flow × distance.

| Dataset | Location | Description |
|:------|:-----|:----|
| **Training** | `problems/qap/datasets/` | 64 instances, 12 facilities |
| **Test** | `problems/qap/datasets/` | 10 instances each for 8 / 12 / 16 facilities |

- **Signature**: `assign_facility(facility_id, available_positions, flow_matrix, distance_matrix, current_assignment) → position_index`
- **Reference solutions**: greedy + pairwise-swap local search

---

### 🎯 k-Center (k-Center Problem)

> **Goal**: Select k centers minimizing the maximum distance from any node to its nearest center.

| Dataset | Location | Description |
|:------|:-----|:----|
| **Training** | `problems/kcenter/datasets/` | 64 instances, 100 nodes, k=8 |
| **Test** | `problems/kcenter/datasets/` | 10 instances each for 50×5 / 100×10 / 200×10 |

- **Signature**: `select_next_center(selected_centers, candidate_nodes, distance_matrix, k) → center_index`
- **Reference solutions**: farthest-first greedy + center-swap local search

---

### ➗ Partition (Number Partitioning Problem)

> **Goal**: Partition numbers into two groups minimizing the sum difference.

| Dataset | Location | Description |
|:------|:-----|:----|
| **Training** | `problems/partition/datasets/` | 64 instances, 100 numbers |
| **Test** | `problems/partition/datasets/` | 10 instances each for 50 / 100 / 200 numbers |

- **Signature**: `assign_number(number_id, sum_a, sum_b, numbers) → group (0/1)`
- **Reference solutions**: greedy + move/swap local search

---

</details>

### 🧩 How to Add a Custom Problem Scenario

Follow any scenario above and create a new directory under `problems/` with the following files:

```
problems/<new_problem>/
├── __init__.py              # empty file, marks the package
├── heuristic.py             # default heuristic algorithm
├── train_eval.py            # training evaluator (must export heuristic_solve_dynamic)
├── test_eval.py             # test evaluator (must export heuristic_solve_static)
├── start_evo.py             # CLI entry script
├── image.py                 # visualization function (optional)
├── generate_datasets.py     # dataset generation script
├── datasets/                # pre-generated datasets (.pkl)
└── result/                  # output directory
```

Then add the corresponding config to `PROBLEM_CONFIG_MAP` in `app.py`; the Web UI will load it automatically.

---

## 📜 Origin

This project is the code implementation of the **graduation thesis: LLM-Based Generation Mechanism for Heuristic Combinatorial Optimization Algorithms**.

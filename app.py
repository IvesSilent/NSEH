# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os
import json
import threading
import time
import csv
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime

from core.evolution import EvolutionFramework
from core.generator import generator
from core.tag_memory import TagMemory, summarize_features
import pickle
import numpy as np

app = Flask(__name__)
app.secret_key = 'nseh_secret_key_2026'

# ── 全局状态 ────────────────────────────────────────────
evolution = None
evolution_thread = None
evolution_paused = False
evolution_stopped = False
evolution_completed = False
population_data = []
current_population_index = 0
present_status = ''
user_name = None
user_id = None
user_best_score = None
evolution_start_time = None
evolution_total_generations = 0
evolution_current_gen = 0
evolution_loaded_population = None  # 保存已加载的种群
evolution_loaded_generation = 0     # 从第几代开始续训
population_loaded_from = None       # 来源文件路径

# 线程安全锁
from threading import Lock
evolution_lock = Lock()
db_lock = Lock()

PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / 'nseh.db'
CONFIG_CACHE_PATH = PROJECT_ROOT / '.config_cache.json'

# 加载缓存的配置
_cached_config = None
def load_cached_config():
    global _cached_config
    if CONFIG_CACHE_PATH.exists():
        try:
            _cached_config = json.loads(CONFIG_CACHE_PATH.read_text(encoding='utf-8'))
        except Exception:
            _cached_config = None
def save_cached_config(config):
    try:
        # 只缓存非敏感配置
        safe = {k: v for k, v in config.items() if k != 'api_key'}
        CONFIG_CACHE_PATH.write_text(json.dumps(safe, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception as e:
        print(f"缓存配置失败: {e}")

load_cached_config()

# ── LLM 预设模型库 ────────────────────────────────────────
LLM_PRESETS = {
    "deepseek-chat": {
        "name": "DeepSeek V3",
        "base_url": "https://api.deepseek.com/v1",
        "provider": "DeepSeek"
    },
    "deepseek-reasoner": {
        "name": "DeepSeek R1",
        "base_url": "https://api.deepseek.com/v1",
        "provider": "DeepSeek"
    },
    "gpt-4o": {
        "name": "GPT-4o",
        "base_url": "https://api.openai.com/v1",
        "provider": "OpenAI"
    },
    "gpt-4o-mini": {
        "name": "GPT-4o Mini",
        "base_url": "https://api.openai.com/v1",
        "provider": "OpenAI"
    },
    "gpt-4-turbo": {
        "name": "GPT-4 Turbo",
        "base_url": "https://api.openai.com/v1",
        "provider": "OpenAI"
    },
    "gpt-3.5-turbo": {
        "name": "GPT-3.5 Turbo",
        "base_url": "https://api.openai.com/v1",
        "provider": "OpenAI"
    },
    "claude-sonnet-4-20250514": {
        "name": "Claude Sonnet 4",
        "base_url": "https://api.anthropic.com/v1",
        "provider": "Anthropic"
    },
    "claude-3-5-sonnet-20241022": {
        "name": "Claude 3.5 Sonnet",
        "base_url": "https://api.anthropic.com/v1",
        "provider": "Anthropic"
    },
    "claude-3-5-haiku-20241022": {
        "name": "Claude 3.5 Haiku",
        "base_url": "https://api.anthropic.com/v1",
        "provider": "Anthropic"
    },
    "gemini-2.0-flash": {
        "name": "Gemini 2.0 Flash",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "provider": "Google"
    },
    "gemini-1.5-pro": {
        "name": "Gemini 1.5 Pro",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "provider": "Google"
    },
    "qwen-turbo": {
        "name": "Qwen Turbo",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "provider": "Alibaba"
    },
    "qwen-plus": {
        "name": "Qwen Plus",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "provider": "Alibaba"
    },
    "qwen-max": {
        "name": "Qwen Max",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "provider": "Alibaba"
    },
    "glm-4-plus": {
        "name": "GLM-4 Plus",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "provider": "Zhipu"
    },
    "glm-4-flash": {
        "name": "GLM-4 Flash",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "provider": "Zhipu"
    },
    "moonshot-v1-8k": {
        "name": "Moonshot v1 8K",
        "base_url": "https://api.moonshot.cn/v1",
        "provider": "Moonshot"
    },
    "custom": {
        "name": "自定义模型",
        "base_url": "",
        "provider": "Custom"
    }
}

# ── 默认配置 ─────────────────────────────────────────────
default_problem_id = 'tsp'
default_config = {
    "population_capacity": 7,
    "num_generations": 5,
    "num_mutation": 3,
    "num_hybridization": 3,
    "num_reflection": 3,
    "api_key": "",
    "base_url": "https://api.deepseek.com/v1",
    "llm_model": "deepseek-chat",
    "problem": "TSP问题即，给定一组节点的坐标，您需要找到访问每个节点一次并返回起始点的最短路径。可以通过从当前节点开始逐步选择下一个节点来解决此任务。",
    "fun_name": "select_next_node",
    "fun_args": ["current_node", "destination_node", "unvisited_nodes", "distance_matrix"],
    "fun_return": ["next_node"],
    "fun_notes": "'current_node','destination_node', 'next_node', 和 'unvisited_nodes'是节点ID，distance_matrix是节点的距离矩阵。所有数据均为Numpy数组。",
    "ascend": True,
    "problem_path": "problems/tsp",
    "train_data": "train_data_tsp.pkl",
    "train_solution": "train_data_solution.pkl"
}

problem_path = default_config['problem_path']
current_problem_name = 'TSP (旅行商问题)'
current_problem_id = 'tsp'

# ── 预定义问题情景配置 ──────────────────────────────────
PROBLEM_CONFIG_MAP = {
    "tsp": {
        "name": "TSP (旅行商问题)",
        "problem": "TSP问题即，给定一组节点的坐标，您需要找到访问每个节点一次并返回起始点的最短路径。可以通过从当前节点开始逐步选择下一个节点来解决此任务。",
        "fun_name": "select_next_node",
        "fun_args": ["current_node", "destination_node", "unvisited_nodes", "distance_matrix"],
        "fun_return": ["next_node"],
        "fun_notes": "'current_node','destination_node', 'next_node', 和 'unvisited_nodes'是节点ID，distance_matrix是节点的距离矩阵。所有数据均为Numpy数组。",
        "ascend": True,
        "problem_path": "problems/tsp",
        "train_data": "train_data_tsp.pkl",
        "train_solution": "train_data_solution.pkl"
    },
    "cvrp": {
        "name": "CVRP (容量受限车辆路径问题)",
        "problem": "CVRP（容量受限车辆路径问题）：给定一个仓库和多个客户节点，每辆车有容量限制，需要为所有客户配送货物，目标是最小化总行驶距离。可以通过从当前节点开始逐步选择下一个要服务的客户来构建路线。如果车辆装不下当前客户需求，返回-1表示返回仓库。",
        "fun_name": "find_best_route",
        "fun_args": ["current_node", "remaining_demands", "vehicle_capacity", "current_load", "distance_matrix", "demand_list"],
        "fun_return": ["next_node"],
        "fun_notes": "'current_node'和'next_node'是节点ID。'remaining_demands'是布尔数组表示未服务节点。'vehicle_capacity'和'current_load'是标量。'distance_matrix'是距离矩阵。'demand_list'是各节点需求量。如果无合适节点则返回-1表示返回仓库。所有数据均为Numpy数组。",
        "ascend": True,
        "problem_path": "problems/cvrp",
        "train_data": "train_data_cvrp.pkl",
        "train_solution": "train_solution_cvrp.pkl"
    },
    "knapsack": {
        "name": "0/1 Knapsack (背包问题)",
        "problem": "0/1背包问题：给定一组物品，每个物品有重量和价值，在背包容量限制内选择物品使总价值最大。需要通过逐个物品决策来构建解，每个物品选择拿(1)或不拿(0)。",
        "fun_name": "select_item",
        "fun_args": ["current_index", "remaining_capacity", "weights", "values", "num_items"],
        "fun_return": ["take_item"],
        "fun_notes": "'current_index'是当前考虑的物品索引。'remaining_capacity'是背包剩余容量。'weights'和'values'是所有物品的重量和价值数组。'num_items'是物品总数。返回1表示拿该物品，0表示不拿。所有数据均为Numpy数组。",
        "ascend": True,
        "problem_path": "problems/knapsack",
        "train_data": "train_data_knapsack.pkl",
        "train_solution": "train_solution_knapsack.pkl"
    },
    "pfsp": {
        "name": "PFSP (置换流水车间调度)",
        "problem": "PFSP（置换流水车间调度问题）：给定n个作业和m台机器，每个作业需按相同顺序在所有机器上加工，目标是最小化最大完工时间(makespan)。可以通过逐个选择未调度的作业来构建调度序列。",
        "fun_name": "select_next_job",
        "fun_args": ["unscheduled_jobs", "current_schedule", "processing_times", "num_machines"],
        "fun_return": ["next_job"],
        "fun_notes": "'unscheduled_jobs'是未调度作业的索引数组。'current_schedule'是当前已调度的作业序列列表。'processing_times'是(n_jobs x num_machines)的加工时间矩阵。'num_machines'是机器数。返回要调度的下一个作业的索引。所有数据均为Numpy数组。",
        "ascend": True,
        "problem_path": "problems/pfsp",
        "train_data": "train_data_pfsp.pkl",
        "train_solution": "train_solution_pfsp.pkl"
    },
    "maxcut": {
        "name": "MaxCut (最大割问题)",
        "problem": "MaxCut问题：给定一个无向带权图，需要将节点分成两组（用0和1标记），使得连接不同组的边的权重之和最大。可以通过逐个分配节点到某一侧来构建划分。",
        "fun_name": "assign_node",
        "fun_args": ["node_id", "unassigned_nodes", "adjacency_matrix", "current_partition"],
        "fun_return": ["side"],
        "fun_notes": "'node_id'是当前需要分配的节点索引。'unassigned_nodes'是布尔数组表示尚未分配的节点。'adjacency_matrix'是带权邻接矩阵。'current_partition'是当前部分分配(-1=未分配, 0/1=已分配侧)。返回0或1表示分配到哪一侧。所有数据均为Numpy数组。",
        "ascend": True,
        "problem_path": "problems/maxcut",
        "train_data": "train_data_maxcut.pkl",
        "train_solution": "train_solution_maxcut.pkl"
    }
}


def get_available_problems():
    """从 problems/ 目录自动发现可用问题情景"""
    problems_dir = PROJECT_ROOT / 'problems'
    available = {}
    if problems_dir.exists():
        for p_dir in sorted(problems_dir.iterdir()):
            if p_dir.is_dir() and (p_dir / '__init__.py').exists():
                key = p_dir.name
                # 优先使用预定义配置
                if key in PROBLEM_CONFIG_MAP:
                    available[key] = PROBLEM_CONFIG_MAP[key]
                else:
                    # 自动发现：尝试读取 heuristic.py 的函数签名
                    available[key] = {
                        "name": key.upper(),
                        "problem_path": f"problems/{key}",
                        "fun_name": "heuristic_func",
                        "fun_args": [],
                        "fun_return": [],
                        "fun_notes": "",
                        "ascend": True,
                        "train_data": f"train_data_{key}.pkl",
                        "train_solution": f"train_solution_{key}.pkl"
                    }
    return available


# ════════════════════════════════════════════════════════
#  SQLite 数据库层
# ════════════════════════════════════════════════════════

def get_db():
    """获取数据库连接（timeout=10 防止多线程锁冲突）"""
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name   TEXT NOT NULL,
            user_id     TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            best_score  REAL,
            created_at  TEXT DEFAULT (datetime('now','localtime')),
            updated_at  TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS experiments (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         TEXT NOT NULL,
            config_json     TEXT NOT NULL,
            start_time      TEXT DEFAULT (datetime('now','localtime')),
            end_time        TEXT,
            status          TEXT DEFAULT 'running',
            best_objective  REAL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS population_snapshots (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_id   INTEGER NOT NULL,
            generation      INTEGER NOT NULL,
            status          TEXT,
            best_objective  REAL,
            snapshot_json   TEXT NOT NULL,
            created_at      TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tag_stats (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            tag         TEXT NOT NULL,
            positive_count INTEGER DEFAULT 0,
            negative_count INTEGER DEFAULT 0,
            last_seen   TEXT DEFAULT (datetime('now','localtime')),
            UNIQUE(tag)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tag_combinations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            combo_hash  TEXT NOT NULL UNIQUE,
            tags_json   TEXT NOT NULL,
            avg_objective REAL,
            sample_count INTEGER DEFAULT 1,
            is_positive  INTEGER DEFAULT 1,
            last_seen   TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        migrate_csv_to_db(conn)

    conn.commit()
    conn.close()


def migrate_csv_to_db(conn):
    """从 user_info.csv 迁移数据"""
    csv_path = PROJECT_ROOT / 'user_info.csv'
    if not csv_path.exists():
        return
    cursor = conn.cursor()
    with open(str(csv_path), 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 4:
                try:
                    score = float(row[3]) if row[3] not in ('null', '', 'None') else None
                    cursor.execute(
                        "INSERT OR IGNORE INTO users (user_name, user_id, password, best_score) VALUES (?, ?, ?, ?)",
                        (row[0], row[1], row[2], score)
                    )
                except (ValueError, sqlite3.IntegrityError):
                    continue
    conn.commit()
    print(f"[DB] CSV 数据已迁移至 SQLite ({DB_PATH})")


def update_tag_stats(tags, is_positive=True):
    if not tags:
        return
    conn = get_db()
    cursor = conn.cursor()
    for tag in tags:
        cursor.execute("""
            INSERT INTO tag_stats (tag, positive_count, negative_count, last_seen)
            VALUES (?, ?, ?, datetime('now','localtime'))
            ON CONFLICT(tag) DO UPDATE SET
                positive_count = CASE WHEN ? THEN positive_count + 1 ELSE positive_count END,
                negative_count = CASE WHEN ? THEN negative_count ELSE negative_count + 1 END,
                last_seen = datetime('now','localtime')
        """, (tag, 1 if is_positive else 0, 1 if is_positive else 0, is_positive, not is_positive))
    conn.commit()
    conn.close()


def update_tag_combo(tags, objective, is_positive):
    if not tags:
        return
    sorted_tags = sorted(tags)
    combo_hash = hashlib.md5(json.dumps(sorted_tags, ensure_ascii=False).encode()).hexdigest()
    tags_json = json.dumps(sorted_tags, ensure_ascii=False)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, avg_objective, sample_count FROM tag_combinations WHERE combo_hash = ?", (combo_hash,))
    row = cursor.fetchone()
    if row:
        new_count = row['sample_count'] + 1
        new_avg = (row['avg_objective'] * row['sample_count'] + objective) / new_count
        cursor.execute("""
            UPDATE tag_combinations SET avg_objective = ?, sample_count = ?,
                is_positive = ?, last_seen = datetime('now','localtime')
            WHERE combo_hash = ?
        """, (new_avg, new_count, 1 if is_positive else 0, combo_hash))
    else:
        cursor.execute("""
            INSERT INTO tag_combinations (combo_hash, tags_json, avg_objective, sample_count, is_positive)
            VALUES (?, ?, ?, 1, ?)
        """, (combo_hash, tags_json, objective, 1 if is_positive else 0))
    conn.commit()
    conn.close()


def load_user_info():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_name, user_id, password, best_score FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [
        {'user_name': r['user_name'], 'user_id': r['user_id'],
         'password': r['password'],
         'best_score': str(r['best_score']) if r['best_score'] is not None else 'null'}
        for r in rows
    ]


# ════════════════════════════════════════════════════════
#  路由
# ════════════════════════════════════════════════════════

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    try:
        db_ok = False
        try:
            conn = get_db()
            conn.execute("SELECT 1")
            conn.close()
            db_ok = True
        except Exception:
            pass
        return jsonify({
            'status': 'ok',
            'database': 'connected' if db_ok else 'disconnected',
            'evolution_running': evolution_thread is not None and evolution_thread.is_alive(),
            'evolution_completed': evolution_completed
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/get_problems', methods=['GET'])
def get_problems():
    """获取可用问题情景列表"""
    try:
        problems = get_available_problems()
        result = []
        for key, cfg in problems.items():
            result.append({
                'id': key,
                'name': cfg.get('name', key.upper()),
                'problem_path': cfg.get('problem_path', f'problems/{key}')
            })
        return jsonify({'problems': result})
    except Exception as e:
        print(f"获取问题列表失败: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/get_llm_presets', methods=['GET'])
def get_llm_presets():
    """获取LLM预设模型列表"""
    try:
        result = []
        for key, cfg in LLM_PRESETS.items():
            result.append({
                'id': key,
                'name': cfg['name'],
                'base_url': cfg['base_url'],
                'provider': cfg['provider']
            })
        return jsonify({'presets': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/get_current_problem', methods=['GET'])
def get_current_problem():
    """获取当前问题情景信息（进化页面显示用）"""
    global current_problem_name, current_problem_id
    return jsonify({
        'status': 'success',
        'problem_name': current_problem_name,
        'problem_id': current_problem_id
    })


@app.route('/api/generate_scenario', methods=['POST'])
def generate_scenario():
    """场景自适应：根据用户描述，由LLM生成问题情景组件"""
    try:
        data = request.json
        description = data.get('description', '').strip()
        scenario_name = data.get('scenario_name', '').strip()
        config = session.get('config') or default_config

        if not description:
            return jsonify({'status': 'error', 'message': '请描述你的问题场景'}), 400
        if not scenario_name:
            return jsonify({'status': 'error', 'message': '请为场景命名'}), 400

        # 校验名称合法性（只允许字母、数字、下划线）
        import re as re_mod
        if not re_mod.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', scenario_name):
            return jsonify({'status': 'error', 'message': '场景名只能包含字母、数字和下划线，且必须以字母开头'}), 400

        api_key = config.get('api_key', '').strip()
        base_url = config.get('base_url', '').strip()
        llm_model = config.get('llm_model', 'deepseek-chat').strip()

        if not api_key:
            return jsonify({'status': 'error', 'message': '请先配置API Key'}), 400
        if not base_url:
            base_url = 'https://api.deepseek.com/v1'

        # 创建场景目录
        problem_dir = Path(PROJECT_ROOT) / 'problems' / scenario_name
        datasets_dir = problem_dir / 'datasets'
        result_dir = problem_dir / 'result'

        if problem_dir.exists():
            return jsonify({
                'status': 'error',
                'message': f'场景目录 {scenario_name} 已存在，请换一个名称'
            }), 409

        problem_dir.mkdir(parents=True)
        datasets_dir.mkdir()
        result_dir.mkdir()

        # 使用LLM生成问题配置
        from core.llm_interface import llm_interface
        llm = llm_interface(api_key, base_url, llm_model, if_stream=False)

        # ── Phase 1: 生成问题配置 ──
        config_prompt = f"""你是一个组合优化专家。根据用户的描述，生成一个JSON格式的问题配置。

用户描述：{description}

请严格按照以下JSON格式输出，不要包含任何其他内容：
{{
  "problem": "问题的详细描述，包括目标、约束等",
  "fun_name": "启发式函数名",
  "fun_args": ["参数1", "参数2", ...],
  "fun_return": ["返回值1"],
  "fun_notes": "参数说明和类型说明。特别说明：所有数据均为Numpy数组。",
  "ascend": true,
  "has_capacity": false,
  "has_demands": false,
  "item_based": false
}}

要求：
- fun_name 应使用有意义的英文函数名
- fun_args 应包含函数需要的所有参数
- fun_return 应包含返回值
- fun_notes 应详细说明每个参数的含义和数据类型
- ascend: true表示适应度越小越好，false表示越大越好
- has_capacity: 是否有容量约束
- has_demands: 是否有需求量/价值量
- item_based: 是否为逐项决策型问题（背包类）
- 请确保生成的配置符合组合优化问题的标准形式"""

        message_list = [{"role": "user", "content": config_prompt}]
        config_response = llm.send_message(message_list)

        # 解析JSON
        import json as json_mod
        try:
            # 尝试从回复中提取JSON
            json_match = re_mod.search(r'\{[\s\S]*\}', config_response)
            if json_match:
                parsed_config = json_mod.loads(json_match.group())
            else:
                parsed_config = json_mod.loads(config_response)
        except Exception:
            # 如果解析失败，使用默认TSP配置作为回退
            parsed_config = {
                "problem": description,
                "fun_name": "heuristic_func",
                "fun_args": ["state"],
                "fun_return": ["action"],
                "fun_notes": "所有数据均为Numpy数组。",
                "ascend": True,
                "has_capacity": False,
                "has_demands": False,
                "item_based": False
            }

        fun_name = parsed_config.get('fun_name', 'heuristic_func')
        fun_args = parsed_config.get('fun_args', ['state'])
        fun_return = parsed_config.get('fun_return', ['action'])

        # ── Phase 2: 生成 __init__.py ──
        init_path = problem_dir / '__init__.py'
        init_path.write_text('', encoding='utf-8')

        # ── Phase 3: 生成 heuristic.py (缺省启发式) ──
        default_heuristic_prompt = f"""你是一个Python算法工程师。请为以下组合优化问题生成一个简单的缺省启发式算法。

问题描述：{parsed_config['problem']}

函数签名：
- 函数名: {fun_name}
- 参数: {fun_args}
- 返回值: {fun_return}

注意：{parsed_config.get('fun_notes', '所有数据均为Numpy数组。')}

请生成一个完整的Python文件，包含必要的import语句和函数的完整实现。
函数应该简单但功能完整，作为一个合理的baseline。
只输出Python代码，用```python标记包裹。"""

        message_list2 = [{"role": "user", "content": default_heuristic_prompt}]
        heuristic_response = llm.send_message(message_list2)

        code_match = re_mod.search(r'```python\s*([\s\S]*?)\s*```', heuristic_response)
        if not code_match:
            default_algorithm = 'import numpy as np\n\ndef ' + fun_name + '(*args):\n    return args[-1][0] if hasattr(args[-1], "__len__") else 0\n'
        else:
            default_algorithm = code_match.group(1).strip()

        heuristic_path = problem_dir / 'heuristic.py'
        heuristic_path.write_text(f"# Default heuristic for {scenario_name}\n# Generated by NSEH Scenario Generator\n{default_algorithm}", encoding='utf-8')

        # ── Phase 4: 生成 generate_datasets.py ──
        datagen_prompt = f"""你是一个Python算法工程师。请为以下组合优化问题生成数据集制备脚本。

问题描述：{parsed_config['problem']}
函数名: {fun_name}
参数: {fun_args}
返回值: {fun_return}

要求生成一个完整的Python脚本，用于生成训练和测试数据集。

脚本格式：
```python
import numpy as np
import pickle
import os

def generate_datasets():
    # 生成64组训练实例
    # 生成测试实例（不同规模各10组）
    # 计算并保存标准解（参考解）
    # 保存为 .pkl 文件
    pass

if __name__ == '__main__':
    generate_datasets()
```

要求：
- 训练数据保存为 train_data_{scenario_name}.pkl
- 训练标准解保存为 train_solution_{scenario_name}.pkl
- 测试数据保存为 test_data_{scenario_name}.pkl
- 测试标准解保存为 test_solution_{scenario_name}.pkl
- 数据集要真实可用，实例数量合理
- 使用np.random.seed(42)确保可重复性
- 所有数据集保存在当前目录下的datasets/文件夹中
- 为每个实例生成参考解（可以是贪心解或近似解）

只输出Python代码，用```python标记包裹。"""

        message_list3 = [{"role": "user", "content": datagen_prompt}]
        datagen_response = llm.send_message(message_list3)
        datagen_match = re_mod.search(r'```python\s*([\s\S]*?)\s*```', datagen_response)
        datagen_code = datagen_match.group(1).strip() if datagen_match else ''

        if datagen_code:
            datagen_path = problem_dir / 'generate_datasets.py'
            datagen_path.write_text(datagen_code, encoding='utf-8')

        # ── Phase 5: 生成 train_eval.py ──
        fun_notes_val = parsed_config.get('fun_notes', '所有数据均为Numpy数组。')
        train_eval_prompt = '''你是一个Python算法工程师。请为以下组合优化问题生成训练评估脚本。

问题描述：''' + str(parsed_config['problem']) + '''
函数名: ''' + fun_name + '''
参数: ''' + json_mod.dumps(fun_args) + '''
返回值: ''' + json_mod.dumps(fun_return) + '''

要求生成一个完整的Python脚本，输出一个函数 heuristic_solve_dynamic。

接口定义：
def heuristic_solve_dynamic(train_data_path, train_solution_path, algorithm_str, fun_name):
    # Args:
    #     train_data_path: 训练数据.pkl文件路径
    #     train_solution_path: 标准解.pkl文件路径
    #     algorithm_str: 启发式算法的Python源码字符串
    #     fun_name: 要执行的函数名
    # Returns:
    #     float: 适应度值（与标准解的偏差，越小越好）
    # 1. 加载训练数据
    # 2. 执行algorithm_str定义函数
    # 3. 对每个训练实例，用该函数求解
    # 4. 与标准解比较，计算适应度（平均相对偏差）
    # 5. 返回适应度值

重要说明：
- algorithm_str 是一个Python函数的源码，需要动态编译执行
- 使用exec()编译，然后用locals()获取函数
- 训练数据是list格式，每个元素是一个实例
- 标准解是list格式，每个元素是对应实例的参考解值
- 适应度 = mean(算法解 / 标准解 - 1) * 100，即平均相对偏差百分比
- 如果算法抛出异常，返回np.inf
- 如果问题有容量约束且has_capacity=True, 检查是否超容量

注意：
''' + fun_notes_val + '''

只输出完整的Python代码，用```python标记包裹。
代码中必须包含所有必要的import语句。'''

        message_list4 = [{"role": "user", "content": train_eval_prompt}]
        traineval_response = llm.send_message(message_list4)
        traineval_match = re_mod.search(r'```python\s*([\s\S]*?)\s*```', traineval_response)
        traineval_code = traineval_match.group(1).strip() if traineval_match else ''

        if traineval_code:
            train_eval_path = problem_dir / 'train_eval.py'
            train_eval_path.write_text(traineval_code, encoding='utf-8')

        # ── Phase 6: 生成 test_eval.py ──
        te_header = '# -*- coding: utf-8 -*-\n# test_eval.py for ' + scenario_name + '\n\n'
        te_body = '''import numpy as np
import pickle
import time
from train_eval import heuristic_solve_dynamic


def heuristic_solve_static(test_data_path, algorithm_str, fun_name):
    with open(test_data_path, 'rb') as f:
        test_data = pickle.load(f)
    
    results = []
    for instance in test_data:
        start = time.time()
        try:
            exec(algorithm_str)
            func = locals()[fun_name]
            result = 0
            elapsed = time.time() - start
            results.append({"objective": float(result), "time": elapsed, "feasible": True})
        except Exception as e:
            elapsed = time.time() - start
            results.append({"objective": np.inf, "time": elapsed, "feasible": False})
    return results
'''
        test_eval_path = problem_dir / 'test_eval.py'
        test_eval_path.write_text(te_header + te_body, encoding='utf-8')

        # ── Phase 7: 生成 start_evo.py ──
        problem_str = str(parsed_config.get('problem', '')).replace('\\n', '\n')
        fun_notes_str = str(parsed_config.get('fun_notes', '')).replace('\\n', '\n')
        se_lines = []
        se_lines.append('# -*- coding: utf-8 -*-')
        se_lines.append('# CLI启动脚本 - ' + scenario_name)
        se_lines.append('import sys\nimport os')
        se_lines.append('sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))')
        se_lines.append('')
        se_lines.append('from core.generator import generator')
        se_lines.append('from core.evolution import EvolutionFramework')
        se_lines.append('')
        se_lines.append('POPULATION_CAPACITY = 7')
        se_lines.append('NUM_GENERATIONS = 5')
        se_lines.append('NUM_MUTATION = 3')
        se_lines.append('NUM_HYBRIDIZATION = 3')
        se_lines.append('NUM_REFLECTION = 3')
        se_lines.append('')
        se_lines.append('API_KEY = "sk-your-api-key"')
        se_lines.append('BASE_URL = "https://api.deepseek.com/v1"')
        se_lines.append('LLM_MODEL = "deepseek-chat"')
        se_lines.append('')
        se_lines.append('PROBLEM = """' + problem_str + '"""')
        se_lines.append('FUN_NAME = "' + fun_name + '"')
        se_lines.append('FUN_ARGS = ' + json_mod.dumps(fun_args))
        se_lines.append('FUN_RETURN = ' + json_mod.dumps(fun_return))
        se_lines.append('FUN_NOTES = """' + fun_notes_str + '"""')
        se_lines.append('ASCEND = ' + str(parsed_config.get('ascend', True)))
        se_lines.append('')
        se_lines.append("if __name__ == '__main__':")
        se_lines.append("    os.environ[\"LOKY_MAX_CPU_COUNT\"] = \"4\"")
        se_lines.append('')
        se_lines.append('    gen = generator(')
        se_lines.append('        api_key=API_KEY,')
        se_lines.append('        base_url=BASE_URL,')
        se_lines.append('        llm_model=LLM_MODEL,')
        se_lines.append('        if_stream=False,')
        se_lines.append('        problem_path=".",')
        se_lines.append('        train_data_name="train_data_' + scenario_name + '.pkl",')
        se_lines.append('        train_solution_name="train_solution_' + scenario_name + '.pkl",')
        se_lines.append('        problem=PROBLEM,')
        se_lines.append('        fun_name=FUN_NAME,')
        se_lines.append('        fun_args=FUN_ARGS,')
        se_lines.append('        fun_return=FUN_RETURN,')
        se_lines.append('        fun_notes=FUN_NOTES')
        se_lines.append('    )')
        se_lines.append('')
        se_lines.append('    evo = EvolutionFramework(')
        se_lines.append('        problem_path=".",')
        se_lines.append('        generator=gen,')
        se_lines.append('        population_capacity=POPULATION_CAPACITY,')
        se_lines.append('        num_generations=NUM_GENERATIONS,')
        se_lines.append('        num_mutation=NUM_MUTATION,')
        se_lines.append('        num_hybridization=NUM_HYBRIDIZATION,')
        se_lines.append('        num_reflection=NUM_REFLECTION,')
        se_lines.append('        save_dir="result",')
        se_lines.append('        ascend=ASCEND')
        se_lines.append('    )')
        se_lines.append('')
        se_lines.append('    evo.run()')
        start_evo_code = '\n'.join(se_lines)
        start_evo_path = problem_dir / 'start_evo.py'
        start_evo_path.write_text(start_evo_code, encoding='utf-8')

        # ── 生成图片配置 ──
        image_lines = []
        image_lines.append('# -*- coding: utf-8 -*-')
        image_lines.append('import matplotlib.pyplot as plt')
        image_lines.append('import numpy as np')
        image_lines.append('')
        image_lines.append('')
        image_lines.append('def plot_solution(solution, save_path=None):')
        image_lines.append('    plt.figure(figsize=(10, 6))')
        image_lines.append('    plt.title("' + scenario_name + ' Solution")')
        image_lines.append('    if save_path:')
        image_lines.append('        plt.savefig(save_path)')
        image_lines.append('    plt.show()')
        image_path = problem_dir / 'image.py'
        image_path.write_text('\n'.join(image_lines), encoding='utf-8')

        # ── 生成 .gitkeep ──
        gitkeep_path = datasets_dir / '.gitkeep'
        gitkeep_path.write_text('', encoding='utf-8')

        scenario_name_display = scenario_name.upper()
        if 'problem' in parsed_config and parsed_config['problem']:
            first_line = parsed_config['problem'].split('。')[0].split('。')[0]
            if len(first_line) > 60:
                first_line = first_line[:60] + '...'
            scenario_name_display = first_line

        return jsonify({
            'status': 'success',
            'message': '场景 ' + scenario_name + ' 创建成功！请在设置页面选择并配置',
            'scenario': {
                'id': scenario_name,
                'name': scenario_name_display,
                'config': {
                    'problem': parsed_config.get('problem', ''),
                    'fun_name': fun_name,
                    'fun_args': fun_args,
                    'fun_return': fun_return,
                    'fun_notes': parsed_config.get('fun_notes', ''),
                    'ascend': parsed_config.get('ascend', True),
                    'problem_path': 'problems/' + scenario_name,
                    'train_data': 'train_data_' + scenario_name + '.pkl',
                    'train_solution': 'train_solution_' + scenario_name + '.pkl'
                }
            }
        })

    except Exception as e:
        print('场景生成失败: ' + str(e))
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/get_cached_config', methods=['GET'])
def get_cached_config():
    """获取缓存的配置（不含API Key）"""
    cfg = session.get('config') or _cached_config or default_config
    safe = {k: v for k, v in cfg.items() if k != 'api_key'}
    return jsonify({'config': safe})


@app.route('/api/list_saved_populations', methods=['POST'])
def list_saved_populations():
    """列出所有问题目录下的已保存种群文件"""
    global problem_path
    try:
        data = request.json or {}
        prob_path = data.get('problem_path', problem_path)
        scan_all = data.get('scan_all', False)

        populations = []

        if scan_all:
            # 扫描所有问题
            problems = get_available_problems()
            for key, cfg in problems.items():
                pp = cfg.get('problem_path', f'problems/{key}')
                result_base = os.path.join(str(PROJECT_ROOT), pp, 'result')
                if not os.path.exists(result_base):
                    continue
                for entry in sorted(os.listdir(result_base), reverse=True):
                    entry_path = os.path.join(result_base, entry)
                    if not os.path.isdir(entry_path) or not entry.startswith('population_'):
                        continue
                    date_str = entry.replace('population_', '')
                    for fname in sorted(os.listdir(entry_path)):
                        if not fname.endswith('.json'):
                            continue
                        fpath = os.path.join(entry_path, fname)
                        try:
                            gen_match = re.search(r'generation_(\d+)', fname)
                            gen_num = int(gen_match.group(1)) if gen_match else 0
                            mtime = os.path.getmtime(fpath)
                            size_kb = os.path.getsize(fpath) / 1024
                            populations.append({
                                'path': fpath,
                                'filename': fname,
                                'date': date_str,
                                'generation': gen_num,
                                'problem': key,
                                'problem_name': cfg.get('name', key.upper()),
                                'mtime': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M'),
                                'size_kb': round(size_kb, 1)
                            })
                        except Exception:
                            continue
        else:
            # 只扫描指定问题
            result_base = os.path.join(str(PROJECT_ROOT), prob_path, 'result')
            if os.path.exists(result_base):
                for entry in sorted(os.listdir(result_base), reverse=True):
                    entry_path = os.path.join(result_base, entry)
                    if not os.path.isdir(entry_path) or not entry.startswith('population_'):
                        continue
                    date_str = entry.replace('population_', '')
                    for fname in sorted(os.listdir(entry_path)):
                        if not fname.endswith('.json'):
                            continue
                        fpath = os.path.join(entry_path, fname)
                        try:
                            gen_match = re.search(r'generation_(\d+)', fname)
                            gen_num = int(gen_match.group(1)) if gen_match else 0
                            mtime = os.path.getmtime(fpath)
                            size_kb = os.path.getsize(fpath) / 1024
                            populations.append({
                                'path': fpath,
                                'filename': fname,
                                'date': date_str,
                                'generation': gen_num,
                                'problem': os.path.basename(prob_path),
                                'problem_name': os.path.basename(prob_path),
                                'mtime': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M'),
                                'size_kb': round(size_kb, 1)
                            })
                        except Exception:
                            continue

        # 按问题、日期、代数排序
        populations.sort(key=lambda x: (x.get('problem', ''), x['date'], x['generation']), reverse=True)
        return jsonify({'populations': populations[:80]})
    except Exception as e:
        print(f"列出种群文件失败: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/load_population', methods=['POST'])
def load_population():
    """加载指定的种群文件，准备继续进化"""
    global evolution_loaded_population, evolution_loaded_generation, population_loaded_from
    try:
        data = request.json
        filepath = data.get('path', '')
        if not filepath or not os.path.exists(filepath):
            return jsonify({'status': 'error', 'message': '文件不存在'}), 404

        with open(filepath, 'r', encoding='utf-8') as f:
            pop_data = json.load(f)

        # 验证数据格式
        if 'heuristics' not in pop_data or 'memory' not in pop_data:
            return jsonify({'status': 'error', 'message': '无效的种群文件格式'}), 400

        # 提取代数和日期
        fname = os.path.basename(filepath)
        gen_match = re.search(r'generation_(\d+)', fname)
        generation = int(gen_match.group(1)) if gen_match else 0

        evolution_loaded_population = pop_data
        evolution_loaded_generation = generation
        population_loaded_from = filepath

        heuristic_count = len(pop_data['heuristics'])
        pos_count = len(pop_data['memory'].get('positive_features', []))
        neg_count = len(pop_data['memory'].get('negative_features', []))

        return jsonify({
            'status': 'success',
            'message': f'已加载种群：{heuristic_count}个启发式，{pos_count}条积极特征，{neg_count}条消极特征',
            'generation': generation,
            'heuristic_count': heuristic_count,
            'memory_summary': {
                'positive_count': pos_count,
                'negative_count': neg_count
            }
        })
    except Exception as e:
        print(f"加载种群失败: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/get_evolution_progress', methods=['GET'])
def get_evolution_progress():
    """获取进化进度（用于进度条显示）"""
    global evolution_current_gen, evolution_total_generations, evolution_start_time
    return jsonify({
        'status': 'success',
        'current_gen': evolution_current_gen,
        'total_gens': evolution_total_generations,
        'elapsed': time.time() - evolution_start_time if evolution_start_time else 0
    })


@app.route('/api/get_problem_config', methods=['POST'])
def get_problem_config():
    """获取指定问题的默认配置"""
    global current_problem_name, current_problem_id
    try:
        data = request.json
        problem_id = data.get('problem_id', 'tsp')
        if not problem_id:
            return jsonify({'status': 'error', 'message': '问题ID为空'}), 400
        problems = get_available_problems()
        if problem_id in problems:
            cfg = problems[problem_id]
            current_problem_name = cfg.get('name', problem_id.upper())
            current_problem_id = problem_id
            return jsonify({'status': 'success', 'config': cfg, 'problem_name': current_problem_name})
        else:
            return jsonify({'status': 'error', 'message': f'未知问题: {problem_id}'}), 404
    except Exception as e:
        print(f"获取问题配置失败: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/login', methods=['POST'])
def user_login():
    global user_name, user_id, user_best_score
    try:
        data = request.json
        uid = data.get('userId')
        pwd = data.get('password')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ? AND password = ?", (uid, pwd))
        row = cursor.fetchone()
        conn.close()
        if row:
            session['user_id'] = row['user_id']
            session['user_name'] = row['user_name']
            raw_score = row['best_score']
            if raw_score is not None:
                try:
                    session['user_best_score'] = float(raw_score)
                except (ValueError, TypeError):
                    session['user_best_score'] = None
            else:
                session['user_best_score'] = None
            user_name = session['user_name']
            user_id = session['user_id']
            user_best_score = session['user_best_score']
            return jsonify({'status': 'success'})
        return jsonify({'status': 'error', 'message': '账号或密码错误，请重新输入'}), 401
    except Exception as e:
        print(f"登录错误: {e}")
        return jsonify({'status': 'error', 'message': '登录过程中出错'}), 500


@app.route('/api/logout', methods=['POST'])
def user_logout():
    try:
        global user_name, user_id, user_best_score
        session.clear()
        user_name = user_id = user_best_score = None
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/register', methods=['POST'])
def user_register():
    try:
        data = request.json
        uid = data.get('userId', '').strip()
        pwd = data.get('password', '').strip()
        uname = data.get('userName', '').strip() or uid
        if not uid or not pwd:
            return jsonify({'status': 'error', 'message': '账号和密码不能为空'}), 400
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (user_name, user_id, password) VALUES (?, ?, ?)", (uname, uid, pwd))
            conn.commit()
            conn.close()
            return jsonify({'status': 'success', 'message': '注册成功'})
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'status': 'error', 'message': '账号已存在'}), 409
    except Exception as e:
        print(f"注册错误: {e}")
        return jsonify({'status': 'error', 'message': '注册失败'}), 500


@app.route('/')
def index():
    global user_name, user_id, user_best_score
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_name = session.get('user_name')
    user_id = session.get('user_id')
    raw = session.get('user_best_score')
    if raw is not None:
        try:
            user_best_score = float(raw) if not isinstance(raw, str) else float(raw)
        except (ValueError, TypeError):
            user_best_score = None
    else:
        user_best_score = None
    return render_template('NSEH_main.html', config=default_config, page='setting')


@app.route('/login')
def login():
    session.clear()
    return render_template('NSEH_login.html')


@app.route('/evolution')
def evolution_page():
    return render_template('NSEH_main.html', config=default_config, page='evolution')


@app.route('/results')
def results_page():
    return render_template('NSEH_main.html', config=default_config, page='results')


@app.route('/rank')
def rank():
    return render_template('NSEH_rank.html')


@app.route('/api/save_config', methods=['POST'])
def save_config():
    global evolution, evolution_thread, evolution_paused, evolution_stopped, current_problem_name, current_problem_id
    try:
        config = request.json
        # 输入净化：移除非法字符
        safe_keys = ['population_capacity', 'num_generations', 'num_mutation', 'num_hybridization',
                     'num_reflection', 'api_key', 'base_url', 'llm_model', 'problem', 'fun_name',
                     'fun_args', 'fun_return', 'fun_notes', 'ascend', 'problem_path', 'train_data',
                     'train_solution', 'problem_name', 'problem_id']
        config = {k: v for k, v in config.items() if k in safe_keys}

        # 记录当前问题情景
        if 'problem_name' in config:
            current_problem_name = config['problem_name']
        if 'problem_id' in config:
            current_problem_id = config['problem_id']
        # 参数校验
        for key in ('population_capacity', 'num_generations', 'num_mutation', 'num_hybridization', 'num_reflection'):
            val = config.get(key)
            if not isinstance(val, int) or val < 0:
                return jsonify({'status': 'error', 'message': f'{key} 需为非负整数'}), 400

        api_key = config.get('api_key', '').strip()
        base_url = config.get('base_url', '').strip()
        llm_model = config.get('llm_model', '').strip()
        if not api_key:
            return jsonify({'status': 'error', 'message': 'API Key 不能为空，请在 LLM 配置中填写'}), 400
        if not base_url:
            return jsonify({'status': 'error', 'message': 'BASE_URL 不能为空'}), 400
        if not llm_model:
            return jsonify({'status': 'error', 'message': 'LLM Model 不能为空'}), 400

        problem_path_val = config.get('problem_path', '').strip()
        if not problem_path_val:
            return jsonify({'status': 'error', 'message': '问题目录不能为空'}), 400
        if not (PROJECT_ROOT / problem_path_val).exists():
            return jsonify({'status': 'error', 'message': f'问题目录不存在: {problem_path_val}'}), 400

        session['config'] = config
        save_cached_config(config)
        evolution = init_evolution(config)
        if evolution is None:
            return jsonify({'status': 'error', 'message': '进化框架初始化失败，请检查问题配置和API Key'}), 500
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"【报错】配置保存失败\nError: {e}")
        return jsonify({'status': 'error', 'message': f'配置保存失败: {str(e)}'}), 500


@app.route('/api/start_evolution', methods=['POST'])
def start_evolution():
    global evolution, evolution_thread, evolution_paused, evolution_stopped, evolution_completed
    global evolution_start_time
    try:
        with evolution_lock:
            if evolution_thread is not None and evolution_thread.is_alive():
                return jsonify({'status': 'error', 'message': '进化已在进行中，请勿重复启动'}), 400

            if evolution_thread is not None and not evolution_thread.is_alive():
                # 清理已结束的线程
                evolution_thread = None

            evolution_paused = False
            evolution_stopped = False
            evolution_completed = False
            app.config['evolution_completed'] = False

            if evolution is None:
                config = session.get('config')
                if not config:
                    return jsonify({'status': 'error', 'message': '请先保存配置'}), 400
                evolution = init_evolution(config)
                if evolution is None:
                    return jsonify({'status': 'error', 'message': '进化框架初始化失败，请检查配置和API Key'}), 500

            evolution_thread = threading.Thread(target=run_evolution, daemon=True)
            evolution_thread.start()
            evolution_start_time = time.time()
            return jsonify({'status': 'success'})
    except Exception as e:
        print(f"启动进化失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': f'启动失败: {str(e)}'}), 500


@app.route('/api/pause_evolution', methods=['POST'])
def pause_evolution():
    try:
        global evolution_paused, present_status
        evolution_paused = True
        present_status = population_data[-1]['status'] if population_data else ''
        if population_data:
            population_data[-1]['status'] = '已暂停'
        update_population_data()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/resume_evolution', methods=['POST'])
def resume_evolution():
    try:
        global evolution_paused, present_status
        evolution_paused = False
        if population_data:
            population_data[-1]['status'] = present_status
        update_population_data()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/stop_evolution', methods=['POST'])
def stop_evolution():
    try:
        global evolution_thread, evolution_paused, evolution_stopped
        evolution_stopped = True
        evolution_paused = False
        evolution_thread = None
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/get_population_data', methods=['GET'])
def get_population_data():
    try:
        return jsonify({'population_data': population_data, 'current_population_index': current_population_index})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/get_results_data', methods=['GET'])
def get_results_data():
    try:
        return jsonify({
            'generation_labels': list(range(len(population_data))),
            'objectives': [pop['best_objective'] for pop in population_data]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/check_evolution_status', methods=['GET'])
def check_evolution_status():
    try:
        completed = app.config.get('evolution_completed', False)
        thread_alive = evolution_thread is not None and evolution_thread.is_alive()
        if completed:
            return jsonify({'status': 'completed'})
        elif thread_alive:
            return jsonify({'status': 'running'})
        else:
            return jsonify({'status': 'idle'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/open_results_directory', methods=['GET'])
def open_results_directory():
    global problem_path
    try:
        parts = problem_path.split('/')
        results_dir = os.path.join(PROJECT_ROOT, *parts, 'result')
        if not os.path.exists(results_dir):
            os.makedirs(results_dir, exist_ok=True)
        os.system(f'explorer "{results_dir}"')
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/get_prompt_template', methods=['GET'])
def get_prompt_template():
    try:
        if evolution is None or evolution.generator is None:
            return jsonify({'status': 'error', 'message': '进化框架未初始化'}), 400
        pt = evolution.generator.prompt_template
        r1, r2, r3, r4, r5 = pt.altprompt_get()
        return jsonify({
            'fun_requirement': r1,
            'strategy_MUT': r2,
            'strategy_HYB': r3,
            'strategy_OPT': r4,
            'analyze': r5
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/update_prompt_template', methods=['POST'])
def update_prompt_template():
    try:
        if evolution is None or evolution.generator is None:
            return jsonify({'status': 'error', 'message': '进化框架未初始化'}), 400
        data = request.json
        evolution.generator.prompt_template.altprompt_set(
            data.get('fun_requirement'),
            data.get('strategy_MUT'),
            data.get('strategy_HYB'),
            data.get('strategy_OPT'),
            data.get('analyze')
        )
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/get_user_rank', methods=['GET'])
def get_user_rank():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT user_name, user_id, best_score FROM users WHERE best_score IS NOT NULL")
        rows = cursor.fetchall()
        conn.close()
        if evolution and hasattr(evolution, 'ascend'):
            if evolution.ascend:
                rows.sort(key=lambda x: float(x['best_score']) if x['best_score'] is not None else float('inf'))
            else:
                rows.sort(key=lambda x: float(x['best_score']) if x['best_score'] is not None else float('-inf'), reverse=True)
        else:
            rows.sort(key=lambda x: float(x['best_score']) if x['best_score'] is not None else float('inf'))
        return jsonify({'users': [
            {'user_name': r['user_name'], 'user_id': r['user_id'], 'best_score': r['best_score']}
            for r in rows
        ]})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/get_tag_stats', methods=['GET'])
def get_tag_stats():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tag_stats ORDER BY (positive_count - negative_count) DESC")
        rows = cursor.fetchall()
        conn.close()
        return jsonify({'tags': [
            {'tag': r['tag'], 'positive_count': r['positive_count'], 'negative_count': r['negative_count']}
            for r in rows
        ]})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/get_feature_tree', methods=['GET'])
def get_feature_tree():
    """返回当前场景的分类树 + 种群标签统计数据"""
    try:
        from core.tag_memory import SCENARIO_TAXONOMIES, GENERIC_TREE, get_taxonomy_info
        scenario_id = current_problem_id if current_problem_id else 'tsp'
        info = get_taxonomy_info(scenario_id)
        tree = SCENARIO_TAXONOMIES.get(scenario_id, {}).get("tree", GENERIC_TREE)
        
        # 从 population_data 中汇总标签
        tag_stats = {}
        tag_pairs = []  # 共现标签对
        for pop in population_data:
            for h in pop.get('heuristics', []):
                tags = h.get('tags', [])
                if isinstance(tags, list) and tags:
                    for tag in tags:
                        s = tag_stats.setdefault(tag, {"count": 0, "objectives": []})
                        s["count"] += 1
                    
                    # 收集共现对
                    for i in range(len(tags)):
                        for j in range(i+1, len(tags)):
                            pair = tuple(sorted([tags[i], tags[j]]))
                            tag_pairs.append(pair)
        
        # 统计共现频率
        from collections import Counter
        pair_freq = Counter(tag_pairs)
        top_pairs = [{"tags": list(p), "count": c} for p, c in pair_freq.most_common(20)]
        
        # 统计积极/消极特征
        pos_tags = Counter()
        neg_tags = Counter()
        for pop in population_data:
            for feat_list in pop.get('memory', {}).get('positive_features', []):
                if isinstance(feat_list, list):
                    for t in feat_list:
                        pos_tags[t] += 1
            for feat_list in pop.get('memory', {}).get('negative_features', []):
                if isinstance(feat_list, list):
                    for t in feat_list:
                        neg_tags[t] += 1
        
        return jsonify({
            'status': 'success',
            'scenario': info,
            'tree': tree,
            'tags': {t: s for t, s in tag_stats.items()},
            'positive_tags': dict(pos_tags),
            'negative_tags': dict(neg_tags),
            'co_occurrence': top_pairs
        })
    except Exception as e:
        print(f"获取特征树失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/get_experiment_history', methods=['GET'])
def get_experiment_history():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, config_json, start_time, end_time, status, best_objective
            FROM experiments ORDER BY id DESC LIMIT 20
        """)
        rows = cursor.fetchall()
        conn.close()
        return jsonify({'experiments': [
            {'id': r['id'], 'user_id': r['user_id'], 'start_time': r['start_time'],
             'end_time': r['end_time'], 'status': r['status'], 'best_objective': r['best_objective']}
            for r in rows
        ]})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ════════════════════════════════════════════════════════
#  内部函数
# ════════════════════════════════════════════════════════

def init_evolution(config):
    global problem_path
    try:
        problem_path = config['problem_path']
        print(f"[初始化] problem_path={problem_path}")
        gen = generator(
            api_key=config['api_key'],
            base_url=config['base_url'],
            llm_model=config['llm_model'],
            if_stream=False,
            problem_path=problem_path,
            train_data_name=config['train_data'],
            train_solution_name=config['train_solution'],
            problem=config['problem'],
            fun_name=config['fun_name'],
            fun_args=config['fun_args'],
            fun_return=config['fun_return'],
            fun_notes=config['fun_notes']
        )
        evo = EvolutionFramework(
            problem_path=problem_path,
            generator=gen,
            population_capacity=config['population_capacity'],
            num_generations=config['num_generations'],
            num_mutation=config['num_mutation'],
            num_hybridization=config['num_hybridization'],
            num_reflection=config['num_reflection'],
            save_dir=os.path.join(problem_path, "result"),
            ascend=config['ascend']
        )
        return evo
    except Exception as e:
        print(f"初始化进化框架时出错: {e}")
        import traceback
        traceback.print_exc()
        return None


def update_user_best_score():
    global user_id, user_best_score
    if not user_id or user_best_score is None:
        return
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT best_score FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        update_needed = False
        if row is None:
            update_needed = True
        else:
            current = row['best_score']
            if current is None:
                update_needed = True
            else:
                try:
                    ubs = float(user_best_score)
                    if (evolution and evolution.ascend and ubs < current) or \
                       (evolution and not evolution.ascend and ubs > current):
                        update_needed = True
                except (ValueError, TypeError):
                    pass
        if update_needed:
            cursor.execute(
                "UPDATE users SET best_score = ?, updated_at = datetime('now','localtime') WHERE user_id = ?",
                (float(user_best_score), user_id)
            )
            conn.commit()
            print(f"用户 {user_id} 最佳适应度更新为 {user_best_score}")
        conn.close()
    except Exception as e:
        print(f"更新最佳适应度时出错: {e}")


def update_population_data():
    global evolution, population_data, current_population_index, user_best_score
    try:
        population_data[current_population_index]['heuristics'] = [h.copy() for h in evolution.population['heuristics']]
        # 根据进化方向正确计算最优适应度，而非假设 heuristics[0] 是排好序的
        objs = [h['objective'] for h in evolution.population['heuristics'] if h.get('objective') is not None and h['objective'] != np.inf]
        if objs:
            best_obj = min(objs) if evolution.ascend else max(objs)
        else:
            best_obj = None
        population_data[current_population_index]['best_objective'] = best_obj
        population_data[current_population_index]['memory']['positive_features'] = evolution.population['memory']['positive_features']
        population_data[current_population_index]['memory']['negative_features'] = evolution.population['memory']['negative_features']

        for i in range(len(population_data[current_population_index]['heuristics'])):
            h = population_data[current_population_index]['heuristics'][i]
            feat = h.get('feature', [])
            feat_display = ' + '.join(feat) if isinstance(feat, list) else str(feat)
            population_data[current_population_index]['heuristics'][i] = {
                'index': i + 1,
                'concept': h['concept'],
                'feature': feat_display,
                'algorithm': h['algorithm'],
                'objective': h['objective'],
                'tags': h.get('feature', []) if isinstance(h.get('feature', []), list) else []
            }

        # 更新全局最佳分数
        if evolution.population['heuristics']:
            current_best = evolution.population['heuristics'][0]['objective']
            if user_best_score is None:
                user_best_score = current_best
            else:
                try:
                    ubs = float(user_best_score)
                    if (evolution.ascend and current_best < ubs) or \
                       (not evolution.ascend and current_best > ubs):
                        user_best_score = current_best
                except (ValueError, TypeError):
                    user_best_score = current_best

        update_user_best_score()
        app.config['population_data'] = population_data
        app.config['current_population_index'] = current_population_index

        # 记录快照
        try:
            conn = get_db()
            cursor = conn.cursor()
            gen_idx = population_data[current_population_index]['index']
            status = population_data[current_population_index].get('status', '')
            best_obj = population_data[current_population_index].get('best_objective')
            if best_obj == 'null' or best_obj is None:
                best_obj = None
            cursor.execute("""
                SELECT id FROM experiments WHERE user_id = ? AND status = 'running'
                ORDER BY id DESC LIMIT 1
            """, (user_id or 'anonymous',))
            exp_row = cursor.fetchone()
            if not exp_row:
                cursor.execute("""
                    INSERT INTO experiments (user_id, config_json, status) VALUES (?, '{}', 'running')
                """, (user_id or 'anonymous',))
                exp_id = cursor.lastrowid
            else:
                exp_id = exp_row['id']
            cursor.execute("""
                INSERT INTO population_snapshots (experiment_id, generation, status, best_objective, snapshot_json)
                VALUES (?, ?, ?, ?, ?)
            """, (exp_id, gen_idx, status, best_obj,
                  json.dumps(population_data[current_population_index], ensure_ascii=False, default=str)))
            for h in evolution.population['heuristics']:
                tags = h.get('feature', [])
                if isinstance(tags, list) and tags:
                    idx_pos = h.get('index', 1)
                    is_pos = idx_pos <= evolution.num_reflection
                    update_tag_stats(tags, is_pos)
                    if h['objective'] != np.inf:
                        update_tag_combo(tags, float(h['objective']), is_pos)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[DB] 记录快照时出错: {e}")
    except Exception as e:
        print(f"更新种群数据时出错: {e}")


def EvoFrame_initialize_population():
    global evolution, population_data, current_population_index, evolution_paused, evolution_stopped
    if evolution is None:
        return

    try:
        population_data = []
        current_population_index = 0
        new_pop = {
            'index': 0,
            'title': '初始化种群',
            'status': '正在生成',
            'best_objective': 'null',
            'memory': {
                'positive_features': evolution.population['memory']['positive_features'],
                'negative_features': evolution.population['memory']['negative_features']
            },
            'heuristics': []
        }
        population_data.append(new_pop)
        app.config['population_data'] = population_data
        app.config['current_population_index'] = current_population_index

        # 生成初始启发式
        try:
            if_inf = True
            retry_count = 0
            max_retries = 2  # 减少重试次数
            while if_inf and not evolution_stopped and retry_count < max_retries:
                new_heuristic = evolution.generator.initial_heuristic()
                if new_heuristic and new_heuristic.get('objective', np.inf) != np.inf:
                    if_inf = False
                else:
                    retry_count += 1
                    print(f"初始生成失败 (尝试 {retry_count}/{max_retries})，重试...")

            if if_inf:
                print("初始启发式生成失败，使用缺省启发式")
                # 使用一个简单的回退策略
                new_heuristic = {
                    'concept': '缺省启发式 - 最近邻',
                    'feature': ['缺省'],
                    'algorithm': '',
                    'objective': np.inf
                }
        except Exception as e:
            print(f"初始启发式生成异常: {e}")
            return

        evolution.population['heuristics'].append(new_heuristic)
        update_population_data()
        print(f"初始启发式: feature={new_heuristic['feature']}, objective={new_heuristic['objective']}")

        # 补充种群
        while len(evolution.population['heuristics']) < evolution.population_capacity:
            if evolution_stopped:
                break
            try:
                new_heuristic = evolution.generator.evol_heuristic(
                    'MUTATION', evolution.population['heuristics'], evolution.population['memory']
                )
                if new_heuristic['objective'] != np.inf:
                    evolution.population['heuristics'].append(new_heuristic)
                else:
                    evolution.population['memory']['negative_features'].append(new_heuristic['feature'])
                update_population_data()
            except Exception as e:
                print(f"生成失败: {str(e)}")

        evolution._sort_population()
        update_population_data()
        evolution._save_population(0)
        population_data[current_population_index]['status'] = '已完成'
    except Exception as e:
        print(f"【报错】初始化失败\nError: {e}")


def EvoFrame_single_evo(strategy, base_heuristics):
    global evolution, population_data, current_population_index, evolution_paused, evolution_stopped
    max_retries = 1  # 合并后单次即可，不再重试
    success = False
    new_heuristic = None

    for _ in range(max_retries):
        if evolution_stopped or evolution_paused:
            return
        try:
            new_heuristic = evolution.generator.evol_heuristic(strategy, base_heuristics, evolution.population['memory'])
            if new_heuristic and new_heuristic.get('objective', np.inf) != np.inf:
                evolution.population['heuristics'].append(new_heuristic)
                success = True
                break
            else:
                print(f"启发式不适于该情形，弃用")
        except Exception as e:
            print(f"【报错】{strategy} 生成失败: {e}")

    if not success and new_heuristic is not None:
        evolution.population['memory']['negative_features'].append(new_heuristic['feature'])
    try:
        update_population_data()
    except Exception:
        pass


def EvoFrame_single_generation():
    global evolution, population_data, current_population_index, evolution_paused, evolution_stopped

    current_population_index += 1
    new_pop = {
        'index': current_population_index,
        'title': f'第{current_population_index}代种群',
        'status': '开始生成',
        'best_objective': 'null',
        'memory': {'positive_features': [], 'negative_features': []},
        'heuristics': []
    }
    population_data.append(new_pop)

    # 突变
    try:
        population_data[current_population_index]['status'] = '正在进行 突变'
        for _ in range(evolution.num_mutation):
            if evolution_stopped:
                break
            while evolution_paused and not evolution_stopped:
                time.sleep(0.5)
            if evolution_stopped:
                break
            EvoFrame_single_evo('MUTATION', evolution.population['heuristics'])
        update_population_data()
    except Exception as e:
        print(f"突变阶段失败: {e}")

    # 杂交
    try:
        population_data[current_population_index]['status'] = '正在进行 杂交'
        parents = evolution.population['heuristics'][:evolution.num_hybridization]
        for i in range(len(parents)):
            for j in range(i + 1, len(parents)):
                if evolution_stopped:
                    break
                while evolution_paused and not evolution_stopped:
                    time.sleep(0.5)
                if evolution_stopped:
                    break
                EvoFrame_single_evo('HYBRIDIZATION', [parents[i], parents[j]])
        update_population_data()
    except Exception as e:
        print(f"杂交阶段失败: {e}")

    # 优化
    try:
        population_data[current_population_index]['status'] = '正在进行 优化'
        for _ in range(len(evolution.population['heuristics'])):
            if evolution_stopped:
                break
            while evolution_paused and not evolution_stopped:
                time.sleep(0.5)
            if evolution_stopped:
                break
            EvoFrame_single_evo('OPTIMIZATION', evolution.population['heuristics'])
        update_population_data()
    except Exception as e:
        print(f"优化阶段失败: {e}")

    # 筛选与反思
    try:
        population_data[current_population_index]['status'] = '正在进行 筛选与反思'
        evolution._selection_and_reflection(current_population_index)
        update_population_data()
        population_data[current_population_index]['status'] = '已完成'
    except Exception as e:
        print(f"筛选阶段失败: {e}")


def run_evolution():
    global evolution, population_data, current_population_index, evolution_paused, evolution_stopped, evolution_completed
    global evolution_start_time, evolution_total_generations, evolution_current_gen
    global evolution_loaded_population, evolution_loaded_generation

    if evolution is None:
        print("run_evolution: evolution为None，退出")
        return

    evolution_start_time = time.time()
    evolution_current_gen = 0

    max_total_time = 36000  # 10小时总超时

    # ── 判断是从头开始还是续训 ──
    is_resume = evolution_loaded_population is not None

    if is_resume:
        # ── 续训：加载已有种群 ──
        print(f"[续训] 从第 {evolution_loaded_generation} 代继续进化...")
        evolution.population = evolution_loaded_population
        evolution._sort_population()

        start_gen = evolution_loaded_generation
        evolution_total_generations = evolution.num_generations + start_gen

        # 已加载的种群放入 population_data
        population_data = []
        current_population_index = 0
        loaded_pop = {
            'index': start_gen,
            'title': f'续训起点 (第{start_gen}代)',
            'status': '已加载',
            'best_objective': evolution.population['heuristics'][0]['objective'] if evolution.population['heuristics'] else 'null',
            'memory': {
                'positive_features': evolution.population['memory'].get('positive_features', []),
                'negative_features': evolution.population['memory'].get('negative_features', [])
            },
            'heuristics': []
        }
        for i, h in enumerate(evolution.population['heuristics']):
            feat = h.get('feature', [])
            feat_display = ' + '.join(feat) if isinstance(feat, list) else str(feat)
            loaded_pop['heuristics'].append({
                'index': i + 1,
                'concept': h['concept'],
                'feature': feat_display,
                'algorithm': h['algorithm'],
                'objective': h['objective'],
                'tags': feat if isinstance(feat, list) else []
            })
        population_data.append(loaded_pop)
        app.config['population_data'] = population_data
        app.config['current_population_index'] = current_population_index
        evolution_loaded_population = None
        print(f"[续训] 已加载 {len(evolution.population['heuristics'])} 个启发式，将继续 {evolution.num_generations} 代")
    else:
        # ── 从头开始 ──
        evolution_total_generations = evolution.num_generations
        try:
            while not evolution_stopped:
                if not evolution_paused:
                    EvoFrame_initialize_population()
                    break
                time.sleep(0.5)
                if time.time() - evolution_start_time > max_total_time:
                    print("[超时] 初始化超时")
                    evolution_stopped = True
                    break
        except Exception as e:
            print(f"初始化异常: {e}")

    # ── 进化循环 ──
    for gen in range(evolution.num_generations):
        if evolution_stopped:
            break
        if time.time() - evolution_start_time > max_total_time:
            print("[超时] 总时间超时")
            evolution_stopped = True
            break

        gen_display = gen + 1
        if is_resume:
            gen_display += start_gen
        evolution_current_gen = gen_display
        gen_start = time.time()
        gen_timeout = 600

        while True:
            if evolution_stopped:
                break
            if not evolution_paused:
                break
            time.sleep(0.5)
        if evolution_stopped:
            break

        try:
            EvoFrame_single_generation()
        except Exception as e:
            print(f"进化_{gen} 失败: {e}")
            import traceback
            traceback.print_exc()

        if time.time() - gen_start > gen_timeout:
            print(f"[超时] 第{gen_display}代超时")
            continue

    if not evolution_stopped:
        evolution_completed = True
        app.config['evolution_completed'] = True
        update_user_best_score()
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE experiments SET end_time = datetime('now','localtime'), status = 'completed',
                    best_objective = ?
                WHERE user_id = ? AND status = 'running'
            """, (evolution.population['heuristics'][0]['objective'] if evolution.population['heuristics'] else None,
                  user_id or 'anonymous'))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[DB] 更新实验状态出错: {e}")
    else:
        print("[进化] 被终止或超时")
        evolution_completed = False
        app.config['evolution_completed'] = False
        evolution_start_time = None
    evolution_loaded_population = None
    evolution_loaded_generation = 0


# ════════════════════════════════════════════════════════
#  启动
# ════════════════════════════════════════════════════════

if __name__ == '__main__':
    os.environ["LOKY_MAX_CPU_COUNT"] = "4"
    init_db()
    print(f"[NSEH] 启动服务器: http://0.0.0.0:5000")
    print(f"[NSEH] 可用问题: {list(get_available_problems().keys())}")
    app.run(debug=True, host='0.0.0.0', port=5000)

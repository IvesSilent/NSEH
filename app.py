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

PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / 'nseh.db'

# ── 默认配置 ─────────────────────────────────────────────
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

# ════════════════════════════════════════════════════════
#  SQLite 数据库层
# ════════════════════════════════════════════════════════

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_db()
    cursor = conn.cursor()

    # 用户表
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

    # 实验记录表
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

    # 种群快照表
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

    # 标签统计表（标签管理种群的优劣势）
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

    # 标签组合表（记录哪些标签组合表现好/差）
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

    # 将 CSV 数据迁移到 SQLite（如果存在 CSV 且表为空）
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
    """更新标签统计数据"""
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
    """更新标签组合统计"""
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
            UPDATE tag_combinations SET
                avg_objective = ?, sample_count = ?, is_positive = ?, last_seen = datetime('now','localtime')
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
    """从 SQLite 加载用户信息"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_name, user_id, password, best_score FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'user_name': row['user_name'],
            'user_id': row['user_id'],
            'password': row['password'],
            'best_score': str(row['best_score']) if row['best_score'] is not None else 'null'
        }
        for row in rows
    ]


# ════════════════════════════════════════════════════════
#  路由
# ════════════════════════════════════════════════════════

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
    global user_name, user_id, user_best_score
    session.clear()
    user_name = user_id = user_best_score = None
    return jsonify({'status': 'success'})


@app.route('/api/register', methods=['POST'])
def user_register():
    """用户注册 API"""
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
            cursor.execute(
                "INSERT INTO users (user_name, user_id, password) VALUES (?, ?, ?)",
                (uname, uid, pwd)
            )
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


@app.route('/api/save_config', methods=['POST'])
def save_config():
    global evolution, evolution_thread, evolution_paused, evolution_stopped
    config = request.json

    for key in ('population_capacity', 'num_generations', 'num_mutation', 'num_hybridization', 'num_reflection'):
        val = config.get(key)
        if not isinstance(val, int) or val < 0:
            return jsonify({'status': 'error', 'message': f'{key} 需为非负整数'}), 400

    if not config.get('api_key') or not config.get('base_url') or not config.get('llm_model'):
        return jsonify({'status': 'error', 'message': 'LLM配置有误，请确保API_key可用且跟所选LLM匹配'}), 400

    session['config'] = config

    try:
        evolution = init_evolution(config)
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"【报错】配置保存失败\n-----------\nError: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/start_evolution', methods=['POST'])
def start_evolution():
    global evolution, evolution_thread, evolution_paused, evolution_stopped
    if evolution_thread is None or not evolution_thread.is_alive():
        evolution_paused = False
        evolution_stopped = False

        if evolution is None:
            config = session.get('config')
            if config:
                evolution = init_evolution(config)
            else:
                return jsonify({'status': 'error', 'message': '进化框架初始化失败，请检查配置'}), 500

        if evolution is not None:
            evolution_thread = threading.Thread(target=run_evolution)
            evolution_thread.daemon = True
            evolution_thread.start()
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': '进化框架初始化失败，请检查配置'}), 500
    return jsonify({'status': 'success'})


@app.route('/api/pause_evolution', methods=['POST'])
def pause_evolution():
    global evolution_paused, present_status
    evolution_paused = True
    present_status = population_data[-1]['status'] if population_data else ''
    if population_data:
        population_data[-1]['status'] = '已暂停'
    update_population_data()
    return jsonify({'status': 'success'})


@app.route('/api/resume_evolution', methods=['POST'])
def resume_evolution():
    global evolution_paused, present_status
    evolution_paused = False
    if population_data:
        population_data[-1]['status'] = present_status
    update_population_data()
    return jsonify({'status': 'success'})


@app.route('/api/stop_evolution', methods=['POST'])
def stop_evolution():
    global evolution_thread, evolution_paused, evolution_stopped
    evolution_stopped = True
    evolution_paused = False
    evolution_thread = None
    return jsonify({'status': 'success'})


@app.route('/api/get_population_data', methods=['GET'])
def get_population_data():
    return jsonify({'population_data': population_data, 'current_population_index': current_population_index})


@app.route('/api/get_results_data', methods=['GET'])
def get_results_data():
    results_data = {
        'generation_labels': list(range(len(population_data))),
        'objectives': [pop['best_objective'] for pop in population_data]
    }
    return jsonify(results_data)


@app.route('/api/check_evolution_status', methods=['GET'])
def check_evolution_status():
    return jsonify({'status': 'completed' if app.config.get('evolution_completed', False) else 'running'})


@app.route('/api/open_results_directory', methods=['GET'])
def open_results_directory():
    global problem_path
    try:
        parts = problem_path.split('/')
        results_dir = os.path.join(PROJECT_ROOT, *parts, 'result')
        os.system(f'explorer "{results_dir}"')
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/get_prompt_template', methods=['GET'])
def get_prompt_template():
    try:
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


@app.route('/rank')
def rank():
    return render_template('NSEH_rank.html')


@app.route('/api/get_user_rank', methods=['GET'])
def get_user_rank():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT user_name, user_id, best_score FROM users WHERE best_score IS NOT NULL")
        rows = cursor.fetchall()
        conn.close()

        if evolution and evolution.ascend:
            rows.sort(key=lambda x: float(x['best_score']) if x['best_score'] is not None else float('inf'))
        else:
            rows.sort(key=lambda x: float(x['best_score']) if x['best_score'] is not None else float('-inf'), reverse=True)

        users_json = [
            {
                'user_name': r['user_name'],
                'user_id': r['user_id'],
                'best_score': r['best_score']
            }
            for r in rows
        ]
        return jsonify({'users': users_json})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ── 标签统计 API（新的架构支持） ──────────────────────────

@app.route('/api/get_tag_stats', methods=['GET'])
def get_tag_stats():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tag_stats ORDER BY (positive_count - negative_count) DESC")
        rows = cursor.fetchall()
        conn.close()
        return jsonify({
            'tags': [
                {
                    'tag': r['tag'],
                    'positive_count': r['positive_count'],
                    'negative_count': r['negative_count']
                }
                for r in rows
            ]
        })
    except Exception as e:
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
        return jsonify({
            'experiments': [
                {
                    'id': r['id'],
                    'user_id': r['user_id'],
                    'start_time': r['start_time'],
                    'end_time': r['end_time'],
                    'status': r['status'],
                    'best_objective': r['best_objective']
                }
                for r in rows
            ]
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ════════════════════════════════════════════════════════
#  内部函数
# ════════════════════════════════════════════════════════

def init_evolution(config):
    global problem_path
    try:
        problem_path = config['problem_path']
        print("Starting initialize the generator.")
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
        return None


def load_user_info():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_name, user_id, password, best_score FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            'user_name': r['user_name'],
            'user_id': r['user_id'],
            'password': r['password'],
            'best_score': str(r['best_score']) if r['best_score'] is not None else 'null'
        }
        for r in rows
    ]


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

    population_data[current_population_index]['heuristics'] = [
        h.copy() for h in evolution.population['heuristics']
    ]
    population_data[current_population_index]['best_objective'] = \
        evolution.population['heuristics'][0]['objective']
    population_data[current_population_index]['memory']['positive_features'] = \
        evolution.population['memory']['positive_features']
    population_data[current_population_index]['memory']['negative_features'] = \
        evolution.population['memory']['negative_features']

    for i in range(len(population_data[current_population_index]['heuristics'])):
        h = population_data[current_population_index]['heuristics'][i]
        feat = h.get('feature', [])
        if isinstance(feat, list):
            feat_display = ' + '.join(feat)
        else:
            feat_display = str(feat)

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

    # 记录实验快照到 SQLite
    try:
        conn = get_db()
        cursor = conn.cursor()
        gen_idx = population_data[current_population_index]['index']
        status = population_data[current_population_index].get('status', '')
        best_obj = population_data[current_population_index].get('best_objective')
        if best_obj == 'null' or best_obj is None:
            best_obj = None

        # 获取或创建实验记录
        cursor.execute("""
            SELECT id FROM experiments WHERE user_id = ? AND status = 'running'
            ORDER BY id DESC LIMIT 1
        """, (user_id or 'anonymous',))
        exp_row = cursor.fetchone()
        if not exp_row:
            cursor.execute("""
                INSERT INTO experiments (user_id, config_json, status)
                VALUES (?, '{}', 'running')
            """, (user_id or 'anonymous',))
            exp_id = cursor.lastrowid
        else:
            exp_id = exp_row['id']

        cursor.execute("""
            INSERT INTO population_snapshots (experiment_id, generation, status, best_objective, snapshot_json)
            VALUES (?, ?, ?, ?, ?)
        """, (
            exp_id,
            gen_idx,
            status,
            best_obj,
            json.dumps(population_data[current_population_index], ensure_ascii=False, default=str)
        ))

        # 更新标签统计
        for h in evolution.population['heuristics']:
            tags = h.get('feature', [])
            if isinstance(tags, list) and tags:
                idx_pos = h.get('index', 1)
                is_positive = idx_pos <= evolution.num_reflection
                update_tag_stats(tags, is_positive)
                if h['objective'] != np.inf:
                    update_tag_combo(tags, float(h['objective']), is_positive)

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] 记录快照时出错: {e}")


def EvoFrame_initialize_population():
    global evolution, population_data, current_population_index, evolution_paused, evolution_stopped
    if evolution is None:
        return

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

    try:
        if_inf = True
        while if_inf and not evolution_stopped:
            new_heuristic = evolution.generator.initial_heuristic()
            if new_heuristic['objective'] != np.inf:
                if_inf = False
            else:
                print("生成失败，重试")

        evolution.population['heuristics'].append(new_heuristic)
        update_population_data()
        print(f"初始启发式生成完成 | 特征: {new_heuristic['feature']} | 适应度: {new_heuristic['objective']}")
        update_population_data()

        while len(evolution.population['heuristics']) < evolution.population_capacity:
            if evolution_stopped:
                break
            start_time = time.time()
            try:
                new_heuristic = evolution.generator.evol_heuristic(
                    'MUTATION',
                    evolution.population['heuristics'],
                    evolution.population['memory']
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
        print(f"【报错】初始化失败\n-----------\nError: {e}")


def EvoFrame_single_evo(strategy, base_heuristics):
    global evolution, population_data, current_population_index, evolution_paused, evolution_stopped
    max_retries = 3
    success = False
    new_heuristic = None

    for _ in range(max_retries):
        if evolution_stopped or evolution_paused:
            return
        try:
            new_heuristic = evolution.generator.evol_heuristic(
                strategy, base_heuristics, evolution.population['memory']
            )
            if new_heuristic['objective'] != np.inf:
                evolution.population['heuristics'].append(new_heuristic)
                success = True
                break
        except Exception as e:
            print(f"【报错】生成失败: {e}")

    if not success and new_heuristic is not None:
        evolution.population['memory']['negative_features'].append(new_heuristic['feature'])
    update_population_data()


def EvoFrame_single_generation():
    global evolution, population_data, current_population_index, evolution_paused, evolution_stopped

    current_population_index += 1
    new_pop = {
        'index': current_population_index,
        'title': f'第{current_population_index}代种群',
        'status': '开始生成',
        'best_objective': 'null',
        'memory': {
            'positive_features': [],
            'negative_features': []
        },
        'heuristics': []
    }
    population_data.append(new_pop)

    try:
        # 突变
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
        print(f"突变失败: {e}")

    try:
        # 杂交
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
        print(f"杂交失败: {e}")

    try:
        # 优化
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
        print(f"优化失败: {e}")

    # 筛选
    population_data[current_population_index]['status'] = '正在进行 筛选与反思'
    evolution._selection_and_reflection(current_population_index)
    update_population_data()
    population_data[current_population_index]['status'] = '已完成'


def run_evolution():
    global evolution, population_data, current_population_index, evolution_paused, evolution_stopped, evolution_completed
    if evolution is None:
        return

    try:
        while not evolution_stopped:
            if not evolution_paused:
                EvoFrame_initialize_population()
                break
            else:
                time.sleep(0.5)
    except Exception as e:
        print(f"初始化失败: {e}")

    for gen in range(evolution.num_generations):
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
            print(f"进化轮次_{gen} 失败: {e}")

    if not evolution_stopped:
        evolution_completed = True
        app.config['evolution_completed'] = True
        update_user_best_score()

        # 更新实验结束时间
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


# ════════════════════════════════════════════════════════
#  启动
# ════════════════════════════════════════════════════════

if __name__ == '__main__':
    os.environ["LOKY_MAX_CPU_COUNT"] = "4"
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

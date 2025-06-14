from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os
from pathlib import Path
import json
import threading
import time
from core.evolution import EvolutionFramework
from core.generator import generator
import pickle
import numpy as np
import csv  # 添加csv模块，用于处理用户信息文件

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于 session

# 全局变量
evolution = None
evolution_thread = None
evolution_paused = False
evolution_stopped = False
evolution_completed = False
population_data = []
current_population_index = 0
current_heuristic_index = 0
present_status = ''

# 用户信息
user_name = None       # 用户名
user_id = None         # 用户ID
user_best_score = None # 用户最佳分数

# 用户信息文件路径
user_info_file = 'user_info.csv'

# 项目根目录路径
PROJECT_ROOT = Path(__file__).parent

# 默认配置
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

# API：用户登录
@app.route('/api/login', methods=['POST'])
def user_login():
    global user_name, user_id, user_best_score
    try:
        data = request.json
        user_id = data.get('userId')
        password = data.get('password')

        # print(f"data = {data}")
        # print(f"user_id = {user_id}")
        # print(f"password = {password}")
        # breakpoint()

        # 读取用户信息
        users = load_user_info()
        # print(f"users = {users}")

        # 查找用户
        for user in users:
            if user['user_id'] == user_id and user['password'] == password:
                # 登录成功
                session['user_id'] = user_id
                session['user_name'] = user['user_name']
                session['user_best_score'] = user['best_score'] if user['best_score'] != 'null' else None

                # 同步到全局变量
                user_name = session['user_name']
                user_id = session['user_id']
                user_best_score = session['user_best_score']

                return jsonify({'status': 'success'})

        # 登录失败
        return jsonify({'status': 'error', 'message': '账号或密码错误，请重新输入'}), 401

    except Exception as e:
        print(f"登录错误: {e}")
        return jsonify({'status': 'error', 'message': '登录过程中出错'}), 500

# API：用户退出登录
@app.route('/api/logout', methods=['POST'])
def user_logout():
    global user_name, user_id, user_best_score  # 声明全局变量
    # 清除会话中的用户信息
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_best_score', None)

    # 清空全局变量
    user_name = None
    user_id = None
    user_best_score = None
    return jsonify({'status': 'success'})

# 路由：设置页面
@app.route('/')
def index():
    global user_name, user_id, user_best_score
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if 'user_id' in session:
        # print(f"已有session中user_id\nuser_id = {session['user_id']}")
        # breakpoint()
        user_name = session['user_name']
        user_id = session['user_id']
        user_best_score = session['user_best_score']
    return render_template('NSEH_main.html', config=default_config, page='setting')


# 路由：登录页面
@app.route('/login')
def login():
    # 清除会话中的用户信息
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_best_score', None)
    return render_template('NSEH_login.html')

# 路由：进化页面
@app.route('/evolution')
def evolution_page():
    return render_template('NSEH_main.html', config=default_config, page='evolution')


# 路由：结果页面
@app.route('/results')
def results_page():
    return render_template('NSEH_main.html', config=default_config, page='results')


# API：保存配置
@app.route('/api/save_config', methods=['POST'])

def save_config():
    global evolution, evolution_thread, evolution_paused, evolution_stopped
    config = request.json

    # 【修改内容start】
    # 检查进化参数
    if (not isinstance(config.get('population_capacity'), int) or config.get('population_capacity') < 0 or
            not isinstance(config.get('num_generations'), int) or config.get('num_generations') < 0 or
            not isinstance(config.get('num_mutation'), int) or config.get('num_mutation') < 0 or
            not isinstance(config.get('num_hybridization'), int) or config.get('num_hybridization') < 0 or
            not isinstance(config.get('num_reflection'), int) or config.get('num_reflection') < 0):
        return jsonify({'status': 'error', 'message': '进化参数需为非负整数'}), 400

    # 检查LLM配置
    if not config.get('api_key') or not config.get('base_url') or not config.get('llm_model'):
        return jsonify({'status': 'error', 'message': 'LLM配置有误，请确保API_key可用且跟你所选的LLM匹配'}), 400

    # 【修改内容end】

    # print("Received config:", config)  # 添加调试信息
    # breakpoint()

    # 保存配置到 session
    session['config'] = config


    try:
        # 初始化进化框架
        evolution = init_evolution(config)

        # print("Evolution initialized")  # 添加调试信息
        # breakpoint()
        return jsonify({'status': 'success'})

    except Exception as e:
        print(f"【报错】配置保存失败\n-----------\nError in save_config: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# API：开始进化
@app.route('/api/start_evolution', methods=['POST'])
def start_evolution():
    global evolution, evolution_thread, evolution_paused, evolution_stopped
    if evolution_thread is None or not evolution_thread.is_alive():
        evolution_paused = False
        evolution_stopped = False

        # 检查进化是否初始化成功
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
        else:
            return jsonify({'status': 'error', 'message': '进化框架初始化失败，请检查配置'}), 500

        # evolution_thread = threading.Thread(target=run_evolution)
        # evolution_thread.daemon = True
        # evolution_thread.start()
    return jsonify({'status': 'success'})


# API：暂停进化
@app.route('/api/pause_evolution', methods=['POST'])
def pause_evolution():
    global evolution_paused, present_status
    evolution_paused = True

    present_status = population_data[-1]['status']

    # 更新当前种群状态为"已暂停"
    if population_data:
        population_data[-1]['status'] = '已暂停'

    update_population_data()

    return jsonify({'status': 'success'})


# API：继续进化
@app.route('/api/resume_evolution', methods=['POST'])
def resume_evolution():
    global evolution_paused, present_status
    evolution_paused = False
    # 更新当前种群状态为"进行中"
    if population_data:
        population_data[-1]['status'] = present_status

    update_population_data()

    return jsonify({'status': 'success'})


# API：终止进化
@app.route('/api/stop_evolution', methods=['POST'])
def stop_evolution():
    global evolution_thread, evolution_paused, evolution_stopped
    evolution_stopped = True
    evolution_paused = False
    evolution_thread = None
    return jsonify({'status': 'success'})


# API：获取种群数据
@app.route('/api/get_population_data', methods=['GET'])
def get_population_data():
    return jsonify({'population_data': population_data, 'current_population_index': current_population_index})

# API：获取结果数据
@app.route('/api/get_results_data', methods=['GET'])
def get_results_data():
    # 假设 results_data 是一个全局变量，存储每代的最优适应度
    results_data = {
        'generation_labels': list(range(len(population_data))),
        'objectives': [pop['best_objective'] for pop in population_data]
    }
    return jsonify(results_data)

# API：检查进化状态
@app.route('/api/check_evolution_status', methods=['GET'])
def check_evolution_status():
    return jsonify({'status': 'completed' if app.config.get('evolution_completed', False) else 'running'})

# API：打开结果目录
@app.route('/api/open_results_directory', methods=['GET'])
def open_results_directory():
    global problem_path
    try:
        # 获取结果目录路径
        # results_dir = os.path.join(PROJECT_ROOT, problem_path, 'result', 'population')
        problem_path_parts = problem_path.split('/')
        results_dir = os.path.join(PROJECT_ROOT, *problem_path_parts, 'result')

        # 打开文件资源管理器
        os.system(f'explorer "{results_dir}"')
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error opening results directory: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 获取当前提示词模版的内容
@app.route('/api/get_prompt_template', methods=['GET'])
def get_prompt_template():
    try:
        prompt_template = evolution.generator.prompt_template
        fun_requirement, strategy_MUT, strategy_HYB, strategy_OPT, analyze = prompt_template.altprompt_get()
        return jsonify({
            'fun_requirement': fun_requirement,
            'strategy_MUT': strategy_MUT,
            'strategy_HYB': strategy_HYB,
            'strategy_OPT': strategy_OPT,
            'analyze': analyze
        })
    except Exception as e:
        print(f"Error getting prompt template: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 更新提示词模版的内容
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
        print(f"Error updating prompt template: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# 路由：排行榜页面
@app.route('/rank')
def rank():
    return render_template('NSEH_rank.html')

# API：获取用户排行榜数据
@app.route('/api/get_user_rank', methods=['GET'])
def get_user_rank():
    try:
        users = load_user_info()

        # 根据最佳适应度排序
        if evolution.ascend:
            # 升序排列（适应度越小越好）
            users.sort(key=lambda x: float(x['best_score']) if x['best_score'] != 'null' else float('inf'))
        else:
            # 降序排列（适应度越大越好）
            users.sort(key=lambda x: float(x['best_score']) if x['best_score'] != 'null' else -float('inf'), reverse=True)

        # 将用户数据转换为JSON格式
        users_json = [
            {
                'user_name': user['user_name'],
                'user_id': user['user_id'],
                'best_score': user['best_score'] if user['best_score'] != 'null' else None
            } for user in users
        ]

        return jsonify({'users': users_json})

    except Exception as e:
        print(f"获取用户排行榜时出错: {e}")
        return jsonify({'status': 'error', 'message': '获取排行榜数据出错'}), 500

### 【待修改：这里需要修改以在未能成功初始化时返回重新初始化】

# 初始化进化框架
def init_evolution(config):
    global problem_path

    try:
        # 获取问题路径
        # problem_path = os.path.join(PROJECT_ROOT, config['problem_path'])
        problem_path = config['problem_path']

        print(f"Starting initialize the generator.")

        # 初始化生成器
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

        # print(f"Starting initialize the evolution framework.")

        # 初始化进化框架
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

        # print(f"Initializing completed.")

        return evo

    except Exception as e:
        print(f"初始化进化框架时出错: {e}")
        # 返回到配置页面并显示错误
        return None





# # 重构EvolutionFramework()的_sort_population()方法
# def EvoFrame_sort_population():
#     global evolution, population_data, current_population_index
#     evolution._sort_population()
#     for i in range(len(population_data[-1]['heuristics'])):
#         population_data[-1]['heuristics'][i] = {
#             'index': i + 1,
#             'concept': evolution.population['heuristics'][i]['concept'],
#             'feature': evolution.population['heuristics'][i]['feature'],
#             'algorithm': evolution.population['heuristics'][i]['algorithm'],
#             'objective': evolution.population['heuristics'][i]['objective']
#         }



# 加载用户信息
def load_user_info():
    global user_info_file
    users = []
    if not os.path.exists(user_info_file):
        return users

    with open(user_info_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >=4:
                users.append({
                    'user_name': row[0],
                    'user_id': row[1],
                    'password': row[2],
                    'best_score': row[3]
                })
    return users

# 更新用户信息
def update_user_best_score():
    global user_id, user_best_score,user_info_file
    #
    # print("开始进行update_user_best_score()")
    # print(f"user_id = {user_id}")
    # print(f"user_best_score = {user_best_score}")
    # print(f"user_info_file = {user_info_file}")
    # breakpoint()

    if user_id and user_best_score is not None:
        try:
            users = load_user_info()  # 使用之前定义的load_user_info函数

            # print("开始查找当前用户信息")
            # breakpoint()

            # 查找当前用户并更新最佳适应度
            updated = False
            # print(f"user_id = {user_id}")
            # print(f"users = {users}")
            # breakpoint()

            for i, user in enumerate(users):
                if user['user_id'] == user_id:
                    if user['best_score'] == 'null':
                        user['best_score'] = str(user_best_score)
                        updated = True
                    else:
                        current_best = float(user['best_score'])
                        if evolution.ascend:
                            if user_best_score < current_best:
                                user['best_score'] = str(user_best_score)
                                updated = True
                        else:
                            if user_best_score > current_best:
                                user['best_score'] = str(user_best_score)
                                updated = True
            # print(f"updated = {updated}")
            # print(f"users = {users}")
            # breakpoint()

            if updated:
                # 保存更新后的用户信息到文件
                with open(user_info_file, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    for user in users:
                        writer.writerow([
                            user['user_name'],
                            user['user_id'],
                            user['password'],
                            user['best_score']
                        ])
                print(f"用户 {user_id} 的最佳适应度已更新为 {user_best_score}")
            else:
                print(f"用户 {user_id} 的最佳适应度未更新")

        except Exception as e:
            print(f"更新用户最佳适应度时出错: {e}")


def update_population_data():
    global evolution, population_data, current_population_index, user_best_score
    # evolution._sort_population()

    # population_data[current_population_index]['heuristics'] = evolution.population['heuristics']
    population_data[current_population_index]['heuristics'] = [h.copy() for h in evolution.population['heuristics']]

    population_data[current_population_index]['best_objective'] = evolution.population['heuristics'][0]['objective']
    population_data[current_population_index]['memory']['positive_features'] = evolution.population['memory'][
        'positive_features']
    population_data[current_population_index]['memory']['negative_features'] = evolution.population['memory'][
        'negative_features']
    for i in range(len(population_data[current_population_index]['heuristics'])):
        population_data[current_population_index]['heuristics'][i] = {
            'index': i + 1,
            'concept': population_data[current_population_index]['heuristics'][i]['concept'],
            'feature': population_data[current_population_index]['heuristics'][i]['feature'],
            'algorithm': population_data[current_population_index]['heuristics'][i]['algorithm'],
            'objective': population_data[current_population_index]['heuristics'][i]['objective']
        }

    # 更新user_best_score为当前种群的最优适应度
    if evolution.population['heuristics']:
        current_best_objective = evolution.population['heuristics'][0]['objective']
        if user_best_score is None:
            user_best_score = current_best_objective
        else:
            if evolution.ascend:
                # 如果适应度越小越好，且当前最优适应度小于user_best_score，则更新
                if current_best_objective < user_best_score:
                    user_best_score = current_best_objective
            else:
                # 如果适应度越大越好，且当前最优适应度大于user_best_score，则更新
                if current_best_objective > user_best_score:
                    user_best_score = current_best_objective

    # print("update_population_data中更新最优适应度")
    # print(f"user_best_score = {user_best_score}")
    # breakpoint()
    # 调用保存用户最佳适应度的函数
    update_user_best_score()

    # 前端更新
    app.config['population_data'] = population_data
    app.config['current_population_index'] = current_population_index




# 重构EvolutionFramework()的_initialize_population()方法
def EvoFrame_initialize_population():
    global evolution, population_data, current_population_index, evolution_paused, evolution_stopped
    if evolution is None:
        return

    start_time = time.time()

    population_data = []
    current_population_index = 0
    population_data.clear()  # 清空历史数据
    # 添加初始化种群数据
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

    # 前端更新
    app.config['population_data'] = population_data
    app.config['current_population_index'] = current_population_index

    try:
        if_inf = True

        while(if_inf):
            new_heuristic = evolution.generator.initial_heuristic()

            if new_heuristic['objective'] != np.inf:
                if_inf = False

            print("生成失败，重试")

        # new_heuristic = evolution.generator.initial_heuristic()
        #
        # if new_heuristic['objective'] == np.inf:
        #     new_heuristic['objective'] = 'inf'

        evolution.population['heuristics'].append(new_heuristic)


        # 数据同步与前端更新

        update_population_data()

        print(f"初始启发式生成完成 | 耗时: {time.time() - start_time:.1f}s")
        print(f"特征: {new_heuristic['feature']}")
        print(f"适应度: {new_heuristic['objective']}")

        update_population_data()

        # 补全种群数量
        while len(evolution.population['heuristics']) < evolution.population_capacity:
            start_time = time.time()
            try:

                new_heuristic = evolution.generator.evol_heuristic(
                    'MUTATION',
                    evolution.population['heuristics'],
                    evolution.population['memory']
                )

                if new_heuristic['objective'] != np.inf:
                    evolution.population['heuristics'].append(new_heuristic)
                    # print(
                        # f"启发式 {len(evolution.population['heuristics'])} 生成成功 | 耗时: {time.time() - start_time:.1f}s")
                else:
                    evolution.population['memory']['negative_features'].append(new_heuristic['feature'])

                # 前端更新
                update_population_data()


            except Exception as e:
                evolution.population['memory']['negative_features'].append(new_heuristic['feature'])
                print(f"生成失败: {str(e)}")

        evolution._sort_population()

        update_population_data()
        evolution._save_population(0)

        # 生成完成
        population_data[current_population_index]['status'] = '已完成'

        # print(f"初始化阶段已完成，current_population_index = {current_population_index}")

    except Exception as e:
        print(f"【报错】初始化失败\n-----------\nError in initializing: {e}")


def EvoFrame_single_evo(strategy, base_heuristics):
    global evolution, population_data, current_population_index, evolution_paused, evolution_stopped

    # print("【检查点】突变函数EvoFrame_single_evo()内，开始生成新启发式")
    # print(f"检查参数：\n\nstrategy = {strategy}\n\nbase_heuristics = {base_heuristics}\n\nevolution.population['memory'] = {evolution.population['memory']}\n")

    max_retries = 3
    success = False
    new_heuristic = None


    for _ in range(max_retries):
        if evolution_stopped or evolution_paused:  # 增加中断检查
            return
        try:
            new_heuristic = evolution.generator.evol_heuristic(strategy, base_heuristics,
                                                           evolution.population['memory'])
            if new_heuristic['objective'] != np.inf:
                evolution.population['heuristics'].append(new_heuristic)
                success = True
                break  # 成功则退出循环

        except Exception as e:
            print(f"【报错】启发式生成失败\n-----------\nError generating heuristic: {e}")

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

    # print("【检查点】开始进行突变阶段")
    try:
        # 突变阶段
        population_data[current_population_index]['status'] = '正在进行 突变'
        #
        # print(f"突变阶段已开始，current_population_index = {current_population_index}")
        # print(f"population_data = {population_data}")

        for _ in range(evolution.num_mutation):
            if evolution_stopped:
                break
            while evolution_paused:
                time.sleep(0.5)
                if evolution_stopped:
                    break
            if evolution_stopped:
                break


            EvoFrame_single_evo('MUTATION', evolution.population['heuristics'])

            if evolution_stopped:
                break
        update_population_data()
    except Exception as e:
        print(f"【报错】进化阶段_突变 失败\n-----------\nError in mutation: {e}")

    try:
        # print("【检查点】开始进行杂交阶段")
        # 杂交阶段
        population_data[current_population_index]['status'] = '正在进行 杂交'
        parents = evolution.population['heuristics'][:evolution.num_hybridization]
        for i in range(len(parents)):
            for j in range(i + 1, len(parents)):
                if evolution_stopped:
                    break
                while evolution_paused:
                    time.sleep(0.5)
                    if evolution_stopped:
                        break
                if evolution_stopped:
                    break
                EvoFrame_single_evo('HYBRIDIZATION', [parents[i], parents[j]])
                if evolution_stopped:
                    break

        update_population_data()
    except Exception as e:
        print(f"【报错】进化阶段_繁殖 失败\n-----------\nError in hybridization: {e}")

    try:
        # print("【检查点】开始进行优化阶段")

        # 优化阶段
        population_data[current_population_index]['status'] = '正在进行 优化'
        for _ in range(len(evolution.population['heuristics'])):
            if evolution_stopped:
                break
            while evolution_paused:
                time.sleep(0.5)
                if evolution_stopped:
                    break
            if evolution_stopped:
                break
            EvoFrame_single_evo('OPTIMIZATION', evolution.population['heuristics'])
            if evolution_stopped:
                break
        update_population_data()
    except Exception as e:
        print(f"【报错】进化阶段_优化 失败\n-----------\nError in optimization: {e}")

    # print("【检查点】开始进行筛选与反思阶段")
    # 筛选和反思阶段
    population_data[current_population_index]['status'] = '正在进行 筛选与反思'
    evolution._selection_and_reflection(current_population_index)
    # evolution._sort_population()
    update_population_data()
    population_data[current_population_index]['status'] = '已完成'


# 运行进化过程
def run_evolution():
    global evolution, population_data, current_population_index, evolution_paused, evolution_stopped, evolution_completed
    if evolution is None:
        return

    # 种群初始化
    try:
        while not evolution_stopped:
            if not evolution_paused:
                EvoFrame_initialize_population()
                break
            else:
                time.sleep(0.5)

        # EvoFrame_initialize_population()
    except Exception as e:
        print(f"【报错】初始化失败\n-----------\nError in initialization: {e}\n")

    # 进化迭代
    for gen in range(evolution.num_generations):
        # 在每个进化阶段前检查暂停状态
        while True:
            if evolution_stopped:
                break
            if not evolution_paused:
                break
            time.sleep(0.5)

        try:
            # print("【检查点】开始单轮次进化")
            EvoFrame_single_generation()
        except Exception as e:
            print(f"【报错】进化轮次_{gen} 失败\n-----------\nError in initialization: {e}\n")

    # 进化完成
    if not evolution_stopped:
        # 跳转到结果页面
        print("【检查点】进化完成，跳转到结果页面")
        # 这里可以添加跳转逻辑，例如设置一个标志位，前端定期检查
        evolution_completed = True
        app.config['evolution_completed'] = True

        # 更新用户最佳适应度
        update_user_best_score()

    #
    # except Exception as e:
    #     print(f"Error in evolution: {e}")


if __name__ == '__main__':
    # 防止joblib警告
    os.environ["LOKY_MAX_CPU_COUNT"] = "4"  # 设置为你的核心数

    # print(f"PROJECT_ROOT = {PROJECT_ROOT}")
    # breakpoint()
    app.run(debug=True)






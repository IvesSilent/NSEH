# -*- coding: utf-8 -*-
# core/evolution.py

import json
import time
import os
from typing import Dict, List
import numpy as np
from core.generator import generator
import datetime
import pickle

class EvolutionFramework:
    def __init__(self,
                 problem_path: str,
                 generator: generator,
                 population_capacity: int = 7,
                 num_generations: int = 5,
                 num_mutation: int = 3,
                 num_hybridization: int = 3,
                 num_reflection: int = 3,
                 save_dir: str = "result/population",
                 ascend: bool = True):

        """
        进化框架主类
            参数:
            problem_path: 问题情景路径
            generator: 初始化好的生成器实例
            population_capacity: 种群容量
            num_generations: 进化代数
            num_mutation: 每代突变次数
            num_hybridization: 每代杂交次数
            num_reflection: 每代反思特征数量
            save_dir: 种群保存路径
        """

        self.generator = generator
        self.population = {
            'heuristics': [],
            'memory': {
                'positive_features': [],
                'negative_features': []
            }
        }
        self.population_capacity = population_capacity
        self.num_generations = num_generations
        self.num_mutation = num_mutation
        self.num_hybridization = num_hybridization
        self.num_reflection = num_reflection
        # self.save_dir = save_dir
        self.save_dir = os.path.join(save_dir,f'population_{datetime.datetime.now().strftime("%Y-%m-%d")}')
        self.ascend = ascend  # TSP问题适应度越小越好

        self.problem_path = problem_path  # 添加此行

        # 添加初始化 current_generation
        self.current_generation = 0

        # 创建保存目录
        os.makedirs(self.save_dir, exist_ok=True)


    def _sort_population(self):
        """按适应度排序种群"""
        self.population['heuristics'].sort(
            key=lambda x: x['objective'],
            reverse=not self.ascend
        )

    def _save_population(self, generation: int):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        """保存当前种群状态"""
        filename = f"generation_{generation:03d}_{current_time}.json"
        filepath = os.path.join(self.save_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(self.population, f, indent=2)

    # [应用模式新增]
    def _get_current_population(self):
        """返回当前种群状态"""
        return {
            "generation": self.current_generation,
            "heuristics": self.population['heuristics'],
            "memory": self.population['memory']
        }

    def _initialize_population(self):
        """初始化种群阶段"""
        print("\n### Phase 0 - 种群初始化 ###")

        # 生成初始启发式
        start_time = time.time()
        new_heuristic = self.generator.initial_heuristic()
        self.population['heuristics'].append(new_heuristic)
        print(f"初始启发式生成完成 | 耗时: {time.time() - start_time:.1f}s")
        print(f"特征: {new_heuristic['feature']}")
        print(f"适应度: {new_heuristic['objective']}")

        # 补全种群数量
        while len(self.population['heuristics']) < self.population_capacity:
            start_time = time.time()
            try:

                new_heuristic = self.generator.evol_heuristic(
                    'MUTATION',
                    self.population['heuristics'],
                    self.population['memory']
                )
                if new_heuristic['objective'] != np.inf:
                    self.population['heuristics'].append(new_heuristic)
                    print(
                        f"启发式 {len(self.population['heuristics'])} 生成成功 | 耗时: {time.time() - start_time:.1f}s")
                else:
                    self.population['memory']['negative_features'].append(new_heuristic['feature'])
            except Exception as e:
                print(f"生成失败: {str(e)}")

        self._sort_population()
        self._save_population(0)

    def _evolution_phase(self, generation: int):
        """执行单次进化迭代"""
        print(f"\n### Generation {generation + 1} - 进化阶段 ###")

        # 阶段1: 突变
        print("\n## 突变阶段 ##")
        for _ in range(self.num_mutation):
            self._evolve('MUTATION')

        # 阶段2: 杂交
        print("\n## 杂交阶段 ##")
        parents = self.population['heuristics'][:self.num_hybridization]
        for i in range(len(parents)):
            for j in range(i + 1, len(parents)):
                self._evolve('HYBRIDIZATION', [parents[i], parents[j]])

        # 阶段3: 优化
        print("\n## 优化阶段 ##")
        for heuristic in self.population['heuristics'][:self.population_capacity]:
            self._evolve('OPTIMIZATION', [heuristic])

        # 筛选和反思
        self._selection_and_reflection(generation)

        # 保存当前种群状态到内存
        self.current_generation = generation + 1

    def _evolve(self, strategy: str, parents: List[Dict] = None):
        """执行单个进化操作"""

        # 待优化：一直优化直到生成的新启发式适应度并非inf
        try:

            max_retries = 3
            success = False
            for _ in range(max_retries):
                start_time = time.time()
                new_heuristic = self.generator.evol_heuristic(
                    strategy,
                    parents or self.population['heuristics'],
                    self.population['memory']
                )
                if new_heuristic['objective'] != np.inf:
                    self.population['heuristics'].append(new_heuristic)
                    print(f"{strategy} 生成成功 | 耗时: {time.time() - start_time:.1f}s")
                    print(f"特征: {new_heuristic['feature']}")
                    print(f"适应度: {new_heuristic['objective']}")
                    success = True
                    break  # 成功则退出循环
            if not success:
                self.population['memory']['negative_features'].append(new_heuristic['feature'])

            # start_time = time.time()
            # new_heuristic = self.generator.evol_heuristic(
            #     strategy,
            #     parents or self.population['heuristics'],
            #     self.population['memory']
            # )
            # if new_heuristic['objective'] != np.inf:
            #     self.population['heuristics'].append(new_heuristic)
            #     print(f"{strategy} 生成成功 | 耗时: {time.time() - start_time:.1f}s")
            #     print(f"特征: {new_heuristic['feature']}")
            #     print(f"适应度: {new_heuristic['objective']}")
            # else:
            #     self.population['memory']['negative_features'].append(new_heuristic['feature'])
        except Exception as e:
            print(f"{strategy} 进化失败: {str(e)}")

    def _selection_and_reflection(self, generation: int):
        """筛选和反思阶段"""
        print("\n## 筛选阶段 ##")
        # 排序并截取
        self._sort_population()
        survivors = self.population['heuristics'][:self.population_capacity]

        # 记录特征
        good = survivors[:self.num_reflection]
        bad = self.population['heuristics'][-self.num_reflection:]

        self.population['memory']['positive_features'].extend(
            [h['feature'] for h in good]
        )
        self.population['memory']['negative_features'].extend(
            [h['feature'] for h in bad]
        )

        # 去重
        self.population['memory']['positive_features'] = list(
            set(self.population['memory']['positive_features'])
        )
        self.population['memory']['negative_features'] = list(
            set(self.population['memory']['negative_features'])
        )

        # 仅保留最后五项
        self.population['memory']['negative_features'] = self.population['memory']['negative_features'][-5:]

        # 更新种群
        self.population['heuristics'] = survivors
        self._save_population(generation + 1)  # generation从0开始

        print(f"种群更新完成 | 当前最佳适应度: {survivors[0]['objective']}")

    def run(self):
        """执行完整进化流程"""
        self._initialize_population()

        for gen in range(self.num_generations):
            print(f"\n{'#' * 40}")
            print(f"## 开始第 {gen + 1}/{self.num_generations} 代进化 ##")
            print(f"{'#' * 40}")
            self._evolution_phase(gen)
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
        self.save_dir = os.path.join(
            save_dir, f'population_{datetime.datetime.now().strftime("%Y-%m-%d")}'
        )
        self.ascend = ascend
        self.problem_path = problem_path
        self.current_generation = 0
        os.makedirs(self.save_dir, exist_ok=True)

    # ── 兼容性访问器 ──────────────────────────────────────
    @property
    def feature_count(self):
        """返回所有启发式的标签（去重）"""
        tags = set()
        for h in self.population['heuristics']:
            feat = h.get('feature', [])
            if isinstance(feat, list):
                tags.update(feat)
            elif isinstance(feat, str) and feat:
                tags.add(feat)
        return len(tags)

    def _sort_population(self):
        self.population['heuristics'].sort(
            key=lambda x: x['objective'],
            reverse=not self.ascend
        )

    def _save_population(self, generation: int):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"generation_{generation:03d}_{current_time}.json"
        filepath = os.path.join(self.save_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(self.population, f, indent=2, ensure_ascii=False)

    def _get_current_population(self):
        return {
            "generation": self.current_generation,
            "heuristics": self.population['heuristics'],
            "memory": self.population['memory']
        }

    def _initialize_population(self):
        print("\n### Phase 0 - 种群初始化 ###")
        start_time = time.time()
        new_heuristic = self.generator.initial_heuristic()
        self.population['heuristics'].append(new_heuristic)
        print(f"初始启发式生成完成 | 耗时: {time.time() - start_time:.1f}s")
        print(f"标签: {new_heuristic['feature']}")
        print(f"适应度: {new_heuristic['objective']}")

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
                    print(f"启发式 {len(self.population['heuristics'])} 生成成功 | 耗时: {time.time() - start_time:.1f}s")
                else:
                    self.population['memory']['negative_features'].append(new_heuristic['feature'])
            except Exception as e:
                print(f"生成失败: {str(e)}")

        self._sort_population()
        self._save_population(0)

    def _evolution_phase(self, generation: int):
        print(f"\n### Generation {generation + 1} - 进化阶段 ###")

        print("\n## 突变阶段 ##")
        for _ in range(self.num_mutation):
            self._evolve('MUTATION')

        print("\n## 杂交阶段 ##")
        parents = self.population['heuristics'][:self.num_hybridization]
        for i in range(len(parents)):
            for j in range(i + 1, len(parents)):
                self._evolve('HYBRIDIZATION', [parents[i], parents[j]])

        print("\n## 优化阶段 ##")
        for heuristic in self.population['heuristics'][:self.population_capacity]:
            self._evolve('OPTIMIZATION', [heuristic])

        self._selection_and_reflection(generation)
        self.current_generation = generation + 1

    def _evolve(self, strategy: str, parents: List[Dict] = None):
        try:
            max_retries = 3
            success = False
            new_heuristic = None
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
                    print(f"标签: {new_heuristic['feature']}")
                    print(f"适应度: {new_heuristic['objective']}")
                    success = True
                    break
            if not success and new_heuristic is not None:
                self.population['memory']['negative_features'].append(new_heuristic['feature'])
        except Exception as e:
            print(f"{strategy} 进化失败: {str(e)}")

    def _selection_and_reflection(self, generation: int):
        print("\n## 筛选阶段 ##")
        self._sort_population()
        survivors = self.population['heuristics'][:self.population_capacity]

        good = survivors[:self.num_reflection]
        bad = self.population['heuristics'][-self.num_reflection:]

        self.population['memory']['positive_features'].extend(
            [h['feature'] for h in good]
        )
        self.population['memory']['negative_features'].extend(
            [h['feature'] for h in bad]
        )

        # 特征去重（list of lists → tuple → set 去重）
        def dedup_features(features):
            seen = set()
            result = []
            for f in features:
                key = tuple(f) if isinstance(f, list) else f
                if key not in seen:
                    seen.add(key)
                    result.append(f)
            return result

        self.population['memory']['positive_features'] = dedup_features(
            self.population['memory']['positive_features']
        )
        self.population['memory']['negative_features'] = dedup_features(
            self.population['memory']['negative_features']
        )

        # 仅保留最后五项
        self.population['memory']['negative_features'] = \
            self.population['memory']['negative_features'][-5:]

        self.population['heuristics'] = survivors
        self._save_population(generation + 1)

        print(f"种群更新完成 | 当前最佳适应度: {survivors[0]['objective']}")

    def run(self):
        self._initialize_population()
        for gen in range(self.num_generations):
            print(f"\n{'#' * 40}")
            print(f"## 开始第 {gen + 1}/{self.num_generations} 代进化 ##")
            print(f"{'#' * 40}")
            self._evolution_phase(gen)

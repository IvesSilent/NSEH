# -*- coding: utf-8 -*-
# core/tag_memory.py — 分层标签记忆系统（场景感知版）

"""
分层标签记忆系统，解决原有记忆机制的核心问题：
1. ❌ 暴力遗忘（只保留最后5条）→ ✅ 分层归档，上层精华保留，下层细节按需修剪
2. ❌ 扁平无结构 → ✅ 按策略类别组织，LLM 提示时结构化呈现
3. ❌ 跨场景混淆 → ✅ 每个问题情景有自己的标签分类树
"""

# ════════════════════════════════════════════════════════
#  场景感知标签分类树
# ════════════════════════════════════════════════════════

SCENARIO_TAXONOMIES = {
    "tsp": {
        "name": "旅行商问题 TSP",
        "description": "给定节点坐标，找最短哈密顿回路",
        "tree": {
            "构造型": {
                "keywords": ["构造","构建","逐步","build","construction","sequential"],
                "children": {
                    "最近邻类": {
                        "keywords": ["最近邻","nearest","NN","贪心","greedy"],
                        "leaf": ["最近邻","最远插入","最远邻","最短边","最便宜插入","随机最近邻"]
                    },
                    "聚类引导": {
                        "keywords": ["聚类","cluster","质心","centroid","凸包","密度"],
                        "leaf": ["质心导向","聚类优先","凸包分解","密度聚类","K-means"]
                    },
                    "随机构造": {
                        "keywords": ["随机","random","shuffle","抖动","蒙特卡洛"],
                        "leaf": ["随机最近邻","随机插入","随机扰动","蒙特卡洛树"]
                    }
                }
            },
            "改进型": {
                "keywords": ["改进","优化","improve","refine","局部","local"],
                "children": {
                    "k-opt类": {
                        "keywords": ["2-opt","3-opt","k-opt","opt","边交换","edge"],
                        "leaf": ["2-opt","3-opt","Or-opt","Lin-Kernighan","边交换"]
                    },
                    "节点重排": {
                        "keywords": ["交换","swap","插入","insert","relocate","move"],
                        "leaf": ["节点交换","边插入","路径重连","双桥扰动"]
                    },
                    "方向引导": {
                        "keywords": ["方向","direction","势能","potential","熵","entropy"],
                        "leaf": ["方向引导","势能场","信息熵引导","路径平滑"]
                    }
                }
            },
            "元启发式": {
                "keywords": ["遗传","退火","蚁群","粒子","禁忌","gene","annealing","aco"],
                "children": {
                    "进化计算": {
                        "keywords": ["遗传","进化","交叉","变异","种群","crossover","mutation"],
                        "leaf": ["遗传算法","精英保留","锦标赛选择","边重组交叉"]
                    },
                    "模拟退火": {
                        "keywords": ["退火","annealing","温度","降温","Metropolis"],
                        "leaf": ["模拟退火","自适应退火","回火策略"]
                    },
                    "群体智能": {
                        "keywords": ["蚁群","信息素","ant","pheromone","蜂群","粒子群"],
                        "leaf": ["蚁群优化","粒子群","人工蜂群"]
                    }
                }
            }
        }
    },

    "cvrp": {
        "name": "容量受限车辆路径 CVRP",
        "description": "多车辆容量约束下最小化总路径",
        "tree": {
            "构造型": {
                "keywords": ["构造","构建","逐步","build","construction"],
                "children": {
                    "节约类": {
                        "keywords": ["节约","saving","Clarke","Wright","CW","合并"],
                        "leaf": ["Clarke-Wright节约","修正节约","最大节约","序贯节约"]
                    },
                    "扫描类": {
                        "keywords": ["扫描","sweep","扇形","角度","极坐标"],
                        "leaf": ["扫描法","扇形划分","角度聚类"]
                    },
                    "插入类": {
                        "keywords": ["插入","insert","最远插入","最近插入","最便宜"],
                        "leaf": ["最近插入","最远插入","最便宜插入","时间窗插入"]
                    },
                    "容量感知": {
                        "keywords": ["容量","capacity","载重","装载","load","填充率"],
                        "leaf": ["容量约束引导","装载率优先","剩余容量感知"]
                    }
                }
            },
            "改进型": {
                "keywords": ["改进","优化","improve","refine","路径","route"],
                "children": {
                    "路径内优化": {
                        "keywords": ["2-opt","3-opt","路径内","intra-route","边交换"],
                        "leaf": ["2-opt","Or-opt","路径反向"]
                    },
                    "路径间优化": {
                        "keywords": ["路径间","inter-route","交换","relocate","cross","exchange"],
                        "leaf": ["Relocate","Exchange","Cross-Exchange","路径间交换"]
                    },
                    "多路径混合": {
                        "keywords": ["多路径","混合","合并","拆分","split","merge"],
                        "leaf": ["路径合并","路径拆分","2-opt*","ICROSS"]
                    }
                }
            },
            "元启发式": {
                "keywords": ["遗传","退火","禁忌","蚁群","gene","tabulocal","annealing"],
                "children": {
                    "遗传算法": {
                        "keywords": ["遗传","进化","交叉","crossover","种群"],
                        "leaf": ["遗传算法","顺序交叉","部分映射交叉","精英策略"]
                    },
                    "禁忌搜索": {
                        "keywords": ["禁忌","tabu","邻域","候选"],
                        "leaf": ["禁忌搜索","自适应禁忌","并行禁忌"]
                    },
                    "变邻域搜索": {
                        "keywords": ["变邻域","VNS","多邻域","shake"],
                        "leaf": ["变邻域搜索","偏变邻域","广义VNS"]
                    }
                }
            }
        }
    },

    "knapsack": {
        "name": "0/1背包问题",
        "description": "容量约束下选择物品最大化总价值",
        "tree": {
            "贪婪型": {
                "keywords": ["贪婪","贪心","greedy","排序","sort"],
                "children": {
                    "价值密度": {
                        "keywords": ["密度","density","性价比","ratio","单位价值"],
                        "leaf": ["价值密度","价值/重量比","性价比优先","修正密度"]
                    },
                    "价值优先": {
                        "keywords": ["价值","value","降序","最大价值"],
                        "leaf": ["价值降序","最大价值优先","加权价值"]
                    },
                    "重量优先": {
                        "keywords": ["重量","weight","轻","轻量","最小重量"],
                        "leaf": ["最小重量优先","轻物优先","重量约束感知"]
                    }
                }
            },
            "搜索型": {
                "keywords": ["搜索","search","回溯","分支","bound"],
                "children": {
                    "动态规划启发": {
                        "keywords": ["动态","DP","规划","递推","状态"],
                        "leaf": ["DP启发","分级DP","滚动优化"]
                    },
                    "分支定界": {
                        "keywords": ["分支","bound","定界","上下界","剪枝"],
                        "leaf": ["分支定界","贪心定界","LP松弛定界"]
                    }
                }
            },
            "进化型": {
                "keywords": ["遗传","进化","退火","蚁群","gene"],
                "children": {
                    "遗传算法": {
                        "keywords": ["遗传","交叉","变异","种群","crossover"],
                        "leaf": ["遗传算法","均匀交叉","修复算子","精英保留"]
                    },
                    "局部搜索": {
                        "keywords": ["局部","邻域","交换","翻转","flip"],
                        "leaf": ["位翻转","邻域搜索","贪心修复","随机扰动"]
                    }
                }
            }
        }
    },

    "pfsp": {
        "name": "置换流水车间调度 PFSP",
        "description": "n作业×m机器，最小化最大完工时间",
        "tree": {
            "构造型": {
                "keywords": ["构造","构建","排序","order","sequence"],
                "children": {
                    "NEH类": {
                        "keywords": ["NEH","Nawaz","Enscore","Ham","总加工时间","插入"],
                        "leaf": ["NEH","修正NEH","NEHedd","加权NEH","快速NEH"]
                    },
                    "Johnson类": {
                        "keywords": ["Johnson","两机","虚拟","转化"],
                        "leaf": ["Johnson规则","虚拟两机","Slope排序"]
                    },
                    "优先规则": {
                        "keywords": ["优先","priority","SPT","LPT","EDD","关键比"],
                        "leaf": ["SPT","LPT","LPT-SPT混合","关键比","最小松弛"]
                    }
                }
            },
            "改进型": {
                "keywords": ["改进","优化","局部","邻域","insertion","exchange"],
                "children": {
                    "插入邻域": {
                        "keywords": ["插入","insert","shift","移动","移除"],
                        "leaf": ["插入邻域","移除再插入","循环插入"]
                    },
                    "交换邻域": {
                        "keywords": ["交换","swap","exchange","互換"],
                        "leaf": ["交换邻域","相邻交换","全交换"]
                    },
                    "多步改进": {
                        "keywords": ["多步","迭代","multi-step","多移动","级联"],
                        "leaf": ["迭代改进","多移动insert","变深度搜索"]
                    }
                }
            },
            "元启发式": {
                "keywords": ["遗传","退火","迭代","IG","annealing"],
                "children": {
                    "迭代贪婪": {
                        "keywords": ["迭代贪婪","IG","破坏重建","destruction","construction"],
                        "leaf": ["迭代贪婪","破坏重建","LR-Heuristic","ILS"]
                    },
                    "遗传算法": {
                        "keywords": ["遗传","进化","交叉","crossover","变异"],
                        "leaf": ["遗传算法","部分映射交叉","作业顺序交叉","秩序交叉"]
                    },
                    "混合策略": {
                        "keywords": ["混合","hybrid","结合","GRASP"],
                        "leaf": ["GRASP","模拟退火贪婪","遗传局部搜索"]
                    }
                }
            }
        }
    },

    "maxcut": {
        "name": "最大割问题 MaxCut",
        "description": "划分节点使跨组边权和最大",
        "tree": {
            "划分型": {
                "keywords": ["划分","partition","分割","split","分组","赋值"],
                "children": {
                    "单侧构建": {
                        "keywords": ["单侧","一侧","seed","种子","生长","grow"],
                        "leaf": ["种子生长","单侧构建","贪心划分"]
                    },
                    "平衡划分": {
                        "keywords": ["平衡","balanced","均匀","等分","平分"],
                        "leaf": ["均匀划分","等分","平衡分裂"]
                    }
                }
            },
            "搜索型": {
                "keywords": ["搜索","局部","flip","翻转","交换"],
                "children": {
                    "位翻转": {
                        "keywords": ["翻转","flip","位","bit","单点"],
                        "leaf": ["单点翻转","贪心翻转","随机翻转"]
                    },
                    "多翻转": {
                        "keywords": ["多翻转","multi-flip","block","块"],
                        "leaf": ["块翻转","双点交换","K-flip"]
                    }
                }
            },
            "元启发式": {
                "keywords": ["遗传","退火","模拟","进化","突发"],
                "children": {
                    "遗传算法": {
                        "keywords": ["遗传","进化","交叉","种群","gene"],
                        "leaf": ["遗传算法","均匀交叉","单点交叉","自适应变异"]
                    },
                    "模拟退火": {
                        "keywords": ["退火","annealing","温度","冷却"],
                        "leaf": ["模拟退火","快速退火","自适应退火"]
                    },
                    "突发搜索": {
                        "keywords": ["突发","burst","临界","多邻域"],
                        "leaf": ["突发邻域搜索","多邻域搜索","偏随机搜索"]
                    }
                }
            }
        }
    }
}

# 通用分类树（场景未知时使用）
GENERIC_TREE = {
    "构造型": {
        "keywords": ["构造","构建","逐步","sequential","build","construction","贪心","greedy"],
        "children": {
            "贪心策略": {"keywords": ["贪心","最近邻","最远","最短","贪婪","greedy","nearest","farthest"], "leaf": ["贪心","最近邻","最远插入","最短边"]},
            "随机策略": {"keywords": ["随机","random","抖动","shake","shuffle","采样"], "leaf": ["随机","随机抖动","随机采样","蒙特卡洛"]},
            "聚类策略": {"keywords": ["聚类","cluster","质心","centroid","密度","k-means"], "leaf": ["聚类引导","质心引导","密度聚类"]}
        }
    },
    "改进型": {
        "keywords": ["改进","优化","improve","refine","局部","local","邻域"],
        "children": {
            "局部搜索": {"keywords": ["局部","邻域","2-opt","3-opt","swap","交换","insert","插入"], "leaf": ["局部搜索","2-opt","节点交换","插入优化"]},
            "方向优化": {"keywords": ["方向","势能","引导","guide","potential","熵"], "leaf": ["方向引导","势能场","熵优化"]}
        }
    },
    "元启发式": {
        "keywords": ["遗传","退火","蚁群","进化","gene","annealing","aco","粒子群","禁忌"],
        "children": {
            "进化算法": {"keywords": ["遗传","进化","交叉","变异","种群","crossover","mutation"], "leaf": ["遗传算法","进化策略","精英保留","锦标赛"]},
            "模拟退火": {"keywords": ["退火","annealing","温度","降温","Metropolis"], "leaf": ["模拟退火","自适应退火"]},
            "群体/禁忌": {"keywords": ["蚁群","粒子群","蜂群","禁忌","tabu"], "leaf": ["蚁群","粒子群","禁忌搜索"]}
        }
    },
    "自适应型": {
        "keywords": ["自适应","动态","adaptive","dynamic","权重","阈值","密度","势能","熵"],
        "children": {
            "参数自适应": {"keywords": ["权重","阈值","参数","动态","自适应"], "leaf": ["动态加权","自适应权重","动态阈值"]},
            "环境感知": {"keywords": ["密度","势能","拓扑","熵","感知","多尺度"], "leaf": ["密度感知","势能场","拓扑势能","多尺度"]},
            "混合型": {"keywords": ["混合","结合","组合","hybrid","阶段","phase","协同"], "leaf": ["多策略混合","阶段切换","协同进化" ]}
        }
    }
}


# ════════════════════════════════════════════════════════
#  场景感知核心函数
# ════════════════════════════════════════════════════════

def get_taxonomy(scenario_id="tsp"):
    """根据场景ID获取对应的标签分类树"""
    if scenario_id in SCENARIO_TAXONOMIES:
        return SCENARIO_TAXONOMIES[scenario_id]["tree"]
    return GENERIC_TREE


def get_taxonomy_info(scenario_id="tsp"):
    """获取场景分类树信息"""
    if scenario_id in SCENARIO_TAXONOMIES:
        return {"name": SCENARIO_TAXONOMIES[scenario_id]["name"],
                "description": SCENARIO_TAXONOMIES[scenario_id]["description"]}
    return {"name": "通用", "description": "通用组合优化问题"}


def classify_tag(tag_name, scenario_id="tsp"):
    """将标签归入指定场景的分类树，返回完整路径"""
    tree = get_taxonomy(scenario_id)
    for category, cat_data in tree.items():
        if any(kw in tag_name for kw in cat_data["keywords"]):
            for subcat, sub_data in cat_data.get("children", {}).items():
                if any(kw in tag_name for kw in sub_data["keywords"]):
                    for leaf in sub_data.get("leaf", []):
                        if leaf in tag_name or tag_name in leaf:
                            return [category, subcat, leaf]
                    return [category, subcat, None]
            return [category, None, None]
    return ["未分类", None, None]


def organize_features(feature_list, scenario_id="tsp"):
    """按场景分类树组织特征"""
    organized = {}
    for feat in feature_list:
        tags = feat if isinstance(feat, list) else [feat]
        primary_tag = tags[0] if tags else ""
        path = classify_tag(primary_tag, scenario_id)
        cat, subcat = path[0], path[1]
        if cat not in organized:
            organized[cat] = {}
        if subcat not in organized[cat]:
            organized[cat][subcat] = []
        organized[cat][subcat].append(tags)
    return organized


def summarize_features(feature_list, max_total=15, scenario_id="tsp"):
    """智能摘要（场景感知版）"""
    if not feature_list:
        return []
    organized = organize_features(feature_list, scenario_id)
    cat_counts = {}
    for cat, subcats in organized.items():
        cat_counts[cat] = sum(len(items) for items in subcats.values())
    sorted_cats = sorted(cat_counts.keys(), key=lambda c: cat_counts[c], reverse=True)
    result = []
    remaining = max_total
    for cat in sorted_cats:
        if remaining <= 0:
            break
        flat_items = []
        for items in organized[cat].values():
            flat_items.extend(items)
        if len(flat_items) <= remaining:
            result.extend(flat_items)
            remaining -= len(flat_items)
        elif len(flat_items) <= remaining + 2:
            result.extend(flat_items[:remaining])
            remaining = 0
        else:
            result.append([cat])
            remaining -= 1
    return result


def format_for_prompt(feature_list, label="积极特征", scenario_id="tsp"):
    """格式化特征用于 LLM 提示词（场景感知）"""
    if not feature_list:
        return ""
    organized = organize_features(feature_list, scenario_id)
    lines = [f"### {label}"]
    for category, subcats in organized.items():
        cat_items = []
        for items in subcats.values():
            for tags in items:
                cat_items.append(" + ".join(tags))
        if not cat_items:
            continue
        non_none_subcats = [s for s in subcats.keys() if s is not None]
        if non_none_subcats:
            for subcat, items in subcats.items():
                if items:
                    name = subcat if subcat else category
                    strs = [" + ".join(tags) for tags in items]
                    line = f"  [{name}] {', '.join(strs[:3])}"
                    if len(strs) > 3:
                        line += f" ... (+{len(strs)-3})"
                    lines.append(line)
        else:
            strs = [" + ".join(tags) for tags in cat_items]
            line = f"  [{category}] {', '.join(strs[:3])}"
            if len(strs) > 3:
                line += f" ... (+{len(strs)-3})"
            lines.append(line)
    return "\n".join(lines)


class TagMemory:
    """场景感知标签记忆管理器"""
    
    def __init__(self, positive_capacity=20, negative_capacity=12, scenario_id="tsp"):
        self.positive = []
        self.negative = []
        self.pos_cap = positive_capacity
        self.neg_cap = negative_capacity
        self.scenario_id = scenario_id
        self.tag_stats = {}
    
    def add_positive(self, features, objective=None):
        if isinstance(features, list) and len(features) > 0:
            self.positive.append(features)
            for tag in features:
                s = self.tag_stats.setdefault(tag, {"pos": 0, "neg": 0, "total": 0, "avg_obj": 0})
                s["pos"] += 1
                s["total"] += 1
                if objective is not None and objective != float('inf'):
                    s["avg_obj"] = (s["avg_obj"] * (s["total"] - 1) + objective) / s["total"]
        self._prune('positive')
    
    def add_negative(self, features):
        if isinstance(features, list) and len(features) > 0:
            self.negative.append(features)
            for tag in features:
                s = self.tag_stats.setdefault(tag, {"pos": 0, "neg": 0, "total": 0, "avg_obj": 0})
                s["neg"] += 1
                s["total"] += 1
        self._prune('negative')
    
    def _prune(self, which):
        lst = self.positive if which == 'positive' else self.negative
        cap = self.pos_cap if which == 'positive' else self.neg_cap
        if len(lst) <= cap:
            return
        # 去重
        seen = set()
        deduped = []
        for feat in reversed(lst):
            key = tuple(feat) if isinstance(feat, list) else str(feat)
            if key not in seen:
                seen.add(key)
                deduped.append(feat)
        deduped.reverse()
        lst.clear()
        lst.extend(deduped)
        if len(lst) <= cap:
            return
        # 智能摘要
        summarized = summarize_features(lst, cap, self.scenario_id)
        lst.clear()
        lst.extend(summarized)
    
    def get_positive(self):
        return self.positive
    
    def get_negative(self):
        return self.negative
    
    def to_dict(self):
        return {"positive_features": self.positive, "negative_features": self.negative}
    
    def format_prompt_section(self):
        parts = []
        pos_str = format_for_prompt(self.positive, "积极经验", self.scenario_id)
        neg_str = format_for_prompt(self.negative, "消极经验", self.scenario_id)
        hot = sorted([(t, s["pos"], s["avg_obj"])
                     for t, s in self.tag_stats.items() if s["pos"] >= 2],
                    key=lambda x: x[1], reverse=True)[:5]
        if hot:
            sline = "### 高频标签排名\n"
            for tag, cnt, obj in hot:
                sline += f"  [{tag}] 出现{cnt}次"
                if obj > 0:
                    sline += f", 平均适应度 {obj:.3f}"
                sline += "\n"
            parts.append(sline)
        if pos_str:
            parts.append(pos_str)
        if neg_str:
            parts.append(neg_str)
        return "\n\n".join(parts)

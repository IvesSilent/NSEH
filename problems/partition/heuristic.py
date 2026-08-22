# example heuristic
# replace it with your own heuristic designed by EoH
import numpy as np


def assign_number(number_id, sum_a, sum_b, numbers):
    """
    示例启发式：贪心（Greedy）
    将当前数字分配给当前总和较小的组（0=A组, 1=B组）。
    """
    return 0 if sum_a <= sum_b else 1

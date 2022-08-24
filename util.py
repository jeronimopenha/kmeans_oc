from veriloggen import *


def create_reduce_tree(n: int):
    n_st = 0
    dict_idx = 0
    final_dict = {}
    queue = []
    for i in range(n):
        queue.append(i)

    while len(queue) > 1:
        queue_tmp = queue.copy()
        queue.clear()
        while queue_tmp:
            a = queue_tmp.pop(0)
            b = None
            if queue_tmp:
                b = queue_tmp.pop(0)

            if b is None:
                final_dict[dict_idx] = [n_st, a]
            else:
                final_dict[dict_idx] = [n_st, a, b]
            queue.append(dict_idx)
            dict_idx += 1
        n_st += 1
    return final_dict, n_st


def initialize_regs(module: Module, values=None):
    regs = []
    if values is None:
        values = {}
    flag = False
    for r in module.get_vars().items():
        if module.is_reg(r[0]):
            regs.append(r)
            if r[1].dims:
                flag = True

    if len(regs) > 0:
        if flag:
            i = module.Integer("i_initial")
        s = module.Initial()
        for r in regs:
            if values:
                if r[0] in values.keys():
                    value = values[r[0]]
                else:
                    value = 0
            else:
                value = 0
            if r[1].dims:
                genfor = For(i(0), i < r[1].dims[0], i.inc())(r[1][i](value))
                s.add(genfor)
            else:
                s.add(r[1](value))

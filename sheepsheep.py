import random

#--------------------------- 全局变量 -----------------------------
# 游戏设置
conf = {
    'compose_num': 3,     # 集齐几个同类块可触发消除
    'type_num': 12,       # 用到几种不同块
    'random_blocks':[9,9],# 随机区块数（数组长度代表随机区数量，值表示每个随机区生产多少块）
    'level_num': 6,       # 分层区共有几层
    'level_block_num': 15,# 每层几个块
    'boarder_step': 1,    # 边界收缩步长
    'slot_num': 7,        # 槽容量
    'patterns': range(20), # 块的类型（即不同图案）
}
# 游戏数据
# 状态：0 - 准备, 1 - 进行中, 2 - 失败, 3 - 胜利
game_status = 0
# 各层块
level_blocks_val = []
# 随机区块
random_blocks_val = []
# 插槽区
slot_area_val = [None for i in range(conf['slot_num'])]
# 当前槽占用数
curr_slot_num = 0
# 保存所有块（包括随机块）
all_blocks = []
block_data = {}
# 总块数
total_block_num = 0
# 已消除块数
clear_block_num = 0
# 总共划分 24 x 24 的格子，每个块占 3 x 3 的格子，
# 生成的起始 x 和 y 坐标范围均为 0 ~ 21
box_width_num = 24
box_height_num = 24
# 保存整个 "棋盘" 的每个格子状态（下标为格子起始点横纵坐标）
chess_board = []
# 操作历史（存储点击的块）
op_history = []

# ---------------------------- 操作 ------------------------------
def set_config(game_level):
    # 第一关
    conf_0 = {
        'type_num': 6,       
        'level_num': 3,      
        'level_block_num': 9,
    }
    # 第二关
    conf_1 = {
        'type_num': 12,       
        'level_num': 6,       
        'level_block_num': 15,
    }
    # 第三关
    conf_2 = {
        'type_num': 12,       
        'level_num': 6,       
        'level_block_num': 12,
        'random_blocks':[12,12],
    }
    choices = [conf_0, conf_1, conf_2]
    conf.update(choices[game_level])

def init_chess_board(rows, cols):
    '''初始化指定大小的棋盘'''
    global chess_board
    chess_board = []
    for i in range(rows):
        chess_board.append([])
        for j in range(cols):
            chess_board[i].append({'blocks':[]})

def init_game(game_level=0):
    global game_status, level_blocks_val, random_blocks_val, slot_area_val, curr_slot_num, all_blocks, block_data, total_block_num, clear_block_num

    # 0. 重置参数和全局变量
    set_config(game_level)
    print('init game', conf)
    # 初始化棋盘
    init_chess_board(box_height_num, box_width_num)
    # 游戏状态：0 - 准备, 1 - 进行中, 2 - 失败, 3 - 胜利
    game_status = 0
    # 各层块
    level_blocks_val = []
    # 随机区块
    random_blocks_val = []
    # 插槽区
    slot_area_val = [None for i in range(conf['slot_num'])]
    # 当前槽占用数
    curr_slot_num = 0
    # 保存所有块（包括随机块）
    all_blocks = []
    block_data = {}
    # 总块数
    total_block_num = 0
    # 已消除块数
    clear_block_num = 0

    # 1. 规划块数
    # 块数单位（总块数必须是该值的倍数）
    block_num_unit = conf['compose_num'] * conf['type_num']
    # 随机生成的总块数
    total_random_block_num = sum(conf['random_blocks'])
    # 需要的最小块数
    min_block_num = conf['level_num'] * conf['level_block_num'] + total_random_block_num
    # 补齐到 block_num_unit 的倍数
    total_block_num = min_block_num
    if total_block_num % block_num_unit != 0:
        total_block_num = (min_block_num // block_num_unit + 1) * block_num_unit

    # 2. 初始化块，随机生成块的内容
    # 需要用到的pattern数组
    need_patterns = conf['patterns'][:conf['type_num']]
    # 保存所有块的数组
    pattern_blocks = [need_patterns[i % conf['type_num']] for i in range(total_block_num)]
    # 打乱数组
    random.shuffle(pattern_blocks)
    # 初始化
    for i in range(total_block_num):
        all_blocks.append(
            {
                'id': i,
                'status': 0,
                'level': 0,
                'type': pattern_blocks[i],
                'higher_level_blocks': [],
                'lower_level_blocks': [],
            }
        )
    # 下一个要塞入的块
    pos = 0

    # 3. 计算随机生成的块
    random_blocks = []
    for i, rand_block in enumerate(conf['random_blocks']):
        random_blocks.append([])
        for j in range(rand_block):
            random_blocks[i].append(all_blocks[pos])
            block_data[pos] = all_blocks[pos]
            pos += 1
    # 剩余块数
    left_block_num = total_block_num - total_random_block_num

    # 4. 计算有层级关系的块
    level_blocks = []
    # 分为 conf.level_num 批，依次生成，每批的边界不同
    for i in range(conf['level_num']):
        next_block_num = min(conf['level_block_num'], left_block_num)
        # 最后一批，分配所有 left_block_num
        if i == conf['level_num'] - 1:
            next_block_num = left_block_num
        next_gen_blocks = all_blocks[pos:pos+next_block_num]
        # 生成块的坐标
        gen_level_block_pos(next_gen_blocks, i)
        # 
        pos += next_block_num
        left_block_num -= next_block_num
        level_blocks.extend(next_gen_blocks)
        if left_block_num <= 0:
            break
    # 填充层级关系
    for block in level_blocks:
        gen_level_relation(block)

    # 5. 初始化空插槽
    slot_area = [None for i in range(conf['slot_num'])]
    return level_blocks, random_blocks, slot_area

def gen_level_block_pos(blocks, level):
    '''生成一批层级块（坐标）'''
    # 先在dXd的格子里分配位置，后面再（乘3）扩展为24X24的棋盘
    border = (conf['level_num'] - level) * conf['boarder_step']
    d = (box_width_num - border*2) // 3
    pos_num = d ** 2
    block_num = len(blocks)
    pos_list = random.sample(range(pos_num), block_num)
    for i in range(block_num):
        block = blocks[i]
        x, y = gen_xy(pos_list[i], d, border)
        block['x'] = x 
        block['y'] = y 
        block['level'] = level
        chess_board[x][y]['blocks'].append(block)

def gen_xy(pos, d, border):
    # 对应到坐标，并放大3倍
    x = (pos % d) * 3
    y = (pos // d) * 3
    # 平移
    x += border
    y += border
    return x, y

def gen_level_relation(block):
    '''给块绑定层级关系'''
    # 确定该块附近的格子坐标范围
    x_min = max(0, block['x'] - 2)
    y_min = max(0, block['y'] - 2)
    x_max = min(block['x'] + 3, box_width_num - 2)
    y_max = min(block['y'] + 3, box_width_num - 2)
    # 遍历该块附近的格子
    for i in range(x_min, x_max):
        for j in range(y_min, y_max):
            overlaps = chess_board[i][j]['blocks']
            for b in overlaps:
                if b['level'] < block['level']:
                    block['lower_level_blocks'].append(b)
                elif b['level'] > block['level']:
                    block['higher_level_blocks'].append(b)

def get_block(_id):
    for b in all_blocks:
        if b['id'] == _id:
            return b

def do_click_block(block_id):
    '''点击事件'''
    global curr_slot_num, game_status, clear_block_num, op_history, slot_area_val

    block = get_block(block_id)
    # 已经输了 | 已经被点击
    if curr_slot_num >= conf['slot_num'] or block['status'] > 0:
        return
    # 修改元素状态为已点击
    block['status'] = 1
    # 记录，用于撤回
    op_history.append(block)
    # 移除覆盖关系
    # for l in block['lower_level_blocks']:
    #     for h in l['higher_level_blocks']:
    #         if h['id'] == block['id']:
    #             l['higher_level_blocks'].remove(h)
    # 新元素加入插槽
    temp_slot_num = curr_slot_num
    slot_area_val[temp_slot_num] = block
    # 检查是否有可消除的
    _map = {}
    # 去除空槽
    temp_slot_area_val = [i for i in slot_area_val if i]
    for slot_block in temp_slot_area_val:
        _type = slot_block['type']
        if _type not in _map:
            _map[_type] = 1
        else:
            _map[_type] += 1
    # 得到新数组
    new_slot_area_val = [None for i in range(conf['slot_num'])]
    temp_slot_num = 0
    for slot_block in temp_slot_area_val:
        # 成功消除（不添加到新数组中）
        if _map[slot_block['type']] >= conf['compose_num']:
            # 块状态改为已消除
            slot_block['status'] = 2
            # 已消除块数 +1
            clear_block_num += 1
            # 清除操作记录，防止撤回
            op_history = []
        else:
            new_slot_area_val[temp_slot_num] = slot_block
            temp_slot_num += 1
    slot_area_val = new_slot_area_val
    curr_slot_num = temp_slot_num
    # 游戏结束
    if temp_slot_num >= conf['slot_num']:
        game_status = 2
        print('Game Over')
    if clear_block_num >= total_block_num:
        game_status = 3

def do_start(game_level):
    '''开始游戏'''
    level_blocks, random_blocks, slot_area = init_game(game_level)
    globals()['level_blocks_val'] = level_blocks
    globals()['random_blocks_val'] = random_blocks
    globals()['slot_area_val'] = slot_area
    globals()['game_status'] = 1

def do_undo():
    '''后退一步'''
    if len(op_history) < 1:
        return 
    if op_history[-1] in level_blocks_val:
        op_history[-1]['status'] = 0
        slot_area_val[curr_slot_num-1] = None


#------------------------------- test ------------------------------
# def do_shuffle():
#     '''随机重洗所有未被点击的块'''
#     # 遍历所有未消除的块
#     untouched_blocks = [i for i in all_blocks if i.status==0]
#     new_block_types = [i['type'] for i in untouched_blocks]
#     random.shuffle(new_block_types)
#     for i, block in enumerate(untouched_blocks):
#         block['type'] = new_block_types[i]

# def do_eliminate():
#     '''消除一组层级块'''
#     type_block_map = {}
#     blocks = [i for i in level_blocks_val if i['status'] == 0]
#     # 遍历所有未消除的层级块
#     for block in blocks:
#         _type = block['type']
#         if _type not in type_block_map:
#             type_block_map[_type] = []
#         type_block_map[_type].append(block)
#         # 有能消除的一组块
#         if len(type_block_map[_type]) >= conf['compose_num']:
#             for b in type_block_map[_type]:
#                 do_click_block(b, force=True)
#             break
        
# def do_remove():
#     '''移出块'''
#     # 移除第一个块
#     block = slot_area_val[0]
#     if not block: return 
#     # 槽移除块
#     for i in range(len(slot_area_val - 1)):
#         slot_area_val[i] = slot_area_val[i+1]
#     slot_area_val[-1] = None
#     # 改变新块的坐标
#     block['x'] = int(random.random() * (box_width_num - 2))
#     block['y'] = box_height_num - 2
#     block['status'] = 0
#     # 移除的是随机块的元素，移到层级区域
#     if block['level'] < 1:
#         block['level'] = 10000
#         level_blocks_val.append(block)
    
# def do_holy_light():
#     '''下一个块可以任意点击'''
#     globals()['is_holy_light'] = True

# def do_see_random():
#     '''可以看到随机块'''
#     globals()['can_see_random'] = not can_see_random

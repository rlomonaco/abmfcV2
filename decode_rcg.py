import pandas as pd
import numpy as np
with open('20191206170312-HELIOS_base_2-vs-usq-fc_3.rcg', 'r') as file:
    lines = file.readlines()
    server_params = [l.split(' ')[0] for l in lines[1][15:-3].split(')(')]
    server_params_values = [l.split(' ')[1] for l in lines[2][15:-3].split(')(')]
    player_params = [l.split(' ')[0] for l in lines[1][15:-3].split(')(')]
    player_params_values = [l.split(' ')[1] for l in lines[2][15:-3].split(')(')]
    player_type_headers = [l.split(' ')[0] for l in lines[3][14:-3].split(')(')]
    player_type = []
    for line in lines:
        if 'player_type ' in line:
            player_type.append([float(l.split(' ')[1]) for l in line[14:-3].split(')(')])
            ind = lines.index(line)
    player_df = pd.DataFrame(np.array(player_type), columns=player_type_headers)

    # show_num = []
    # ball_x = []
    # ball_y = []
    # ball_vx = []
    # ball_vy = []
    player_statline = []
    player_header = ['team', 'player index', 'base', 'x', 'y', 'vx', 'vy', 'pointing_x', 'pointing_y', 'view_quality', 'view_width', 'stamina', 'effort', 'recovery', 'stamina capacity', 'focus_side', 'focus_num', 'kick_count', 'dash_count', 'turn_count', 'catch_count', 'move_count', 'turn_count', 'change_view_count', 'say_count', 'tackle_count', 'pointo_count', 'attentionto_count']
    show_header = ['show_num', 'ball_x', 'ball_y', 'ball_vx', 'ball_vy']
    show_header.extend(player_header*22)
    count = 0
    for line in lines:
        if '(show ' in line:
            if count != 0:
                player_stat = [line[1:-2].split(' ((')[0].split(' ')[-1]]
                player_stat.extend(line[1:-2].split(' ((')[1][3:-1].split(' '))
                # show_num.append(int(line[1:-2].split(' ((')[0].split(' ')[-1]))
                # ball_x.append(float(line[1:-2].split(' ((')[1][3:-1].split(' ')[0]))
                # ball_y.append(float(line[1:-2].split(' ((')[1][3:-1].split(' ')[1]))
                # ball_vx.append(float(line[1:-2].split(' ((')[1][3:-1].split(' ')[2]))
                # ball_vy.append(float(line[1:-2].split(' ((')[1][3:-1].split(' ')[3]))
                for i in range(2, len(line[1:-2].split(' (('))):
                    player_stat.extend(line[1:-2].split(' ((')[i][:-2].replace('(','').replace(')','').replace('v ','').replace('c ','').replace('s ','').replace('f ','').split(' '))
                player_statline.append(player_stat)
            count +=1



print('done')

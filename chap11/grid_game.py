import random
from copy import deepcopy
import os
import time


def grid_game(players, n=5, limit=50):
    view = [['.'] * n for _ in range(n)]
    tmp = '\n'.join([''.join(i) for i in view])

    # board size
    board_size = (n, n)
    # print(board_size)
    # remember the last move for each player
    last_move = [-1, -1]

    # remember the player's locations
    location = [[random.randint(0, board_size[0]) % n, random.randint(0, board_size[1]) % n]]

    # put the second player at sufficient distance from the first
    location.append([(location[0][0] + 2) % n, (location[0][1] + 2) % n])

    # maximum of 50 moves before a tie
    for l in range(limit):
        # for each player
        for i in range(2):
            locs = location[i] + location[1 - i]
            locs.append(last_move[i])

            move = players[i].evaluate(locs) % 4

            # you lose if you move the same direction twice in a row
            if last_move[i] == move:
                print(f'game over: streak {l}')
                return 1 - i
            last_move[i] = move

            # 0 for upward move
            if move == 0:
                location[i][0] -= 1
                # board limits
                if location[i][0] < 0:
                    location[i][0] = 0

            # 1 for downward move
            if move == 1:
                location[i][0] += 1
                if location[i][0] >= board_size[0]:
                    location[i][0] = board_size[0] - 1

            # 2 for backward move
            if move == 2:
                location[i][1] -= 1
                if location[i][1] < 0:
                    location[i][1] = 0

            # 3 for forward move
            if move == 3:
                location[i][1] += 1
                if location[i][1] >= board_size[1]:
                    location[i][1] = board_size[1] - 1

            # if you have captured the other player, you win
            if location[i] == location[1 - i]:
                print(f'capture! streak {l}')
                return i

        now = deepcopy(view)
        a, b = location[0]
        c, d = location[1]

        now[b][a] = 'o'
        now[d][c] = 'x'
        res = '\n'.join([''.join(i) for i in now])

    return -1


def tournament(players, n=5):
    m = len(players)
    losses = [0] * m

    for i in range(m):
        for j in range(i + 1, m):
            # play game
            winner = grid_game([players[i], players[j]], n=n)

            # if player i wins
            if winner == 0:
                losses[j] += 2
            elif winner == -1:
                losses[i] += 2
            else:
                losses[i] += 1
                losses[j] += 1

    *res, = zip(losses, players)
    res.sort(key=lambda x: x[0])
    return res

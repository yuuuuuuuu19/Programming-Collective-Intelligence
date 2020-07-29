from chap5 import optimization
from PIL import Image, ImageDraw
import random
import math

people = ['Charlie',
          'Augustus',
          'Veruca',
          'Violet',
          'Mike',
          'Joe',
          'Willy',
          'Miranda']

links = [('Augustus', 'Willy'),
         ('Mike', 'Joe'),
         ('Miranda', 'Mike'),
         ('Violet', 'Augustus'),
         ('Miranda', 'Willy'),
         ('Charlie', 'Mike'),
         ('Veruca', 'Joe'),
         ('Miranda', 'Augustus'),
         ('Willy', 'Augustus'),
         ('Joe', 'Charlie'),
         ('Veruca', 'Augustus'),
         ('Miranda', 'Joe')]


def cross_count(sol):
    # convert the number list into a dictionary: name:(x, y)
    xs = sol[::2]
    ys = sol[1::2]
    loc = dict([(people[i], (x, y)) for i, (x, y) in enumerate(zip(xs, ys))])
    total = 0

    for i in range(len(links)):
        for j in range(i + 1, len(links)):

            (x1, y1), (x2, y2) = loc[links[i][0]], loc[links[i][1]]
            (x3, y3), (x4, y4) = loc[links[j][0]], loc[links[j][1]]

            den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
            if den == 0:
                continue

            ua = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / den
            ub = ((x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1)) / den

            if 0 < ua < 1 and 0 < ub < 1:
                total += 1

            d1 = math.sqrt(math.pow(x1 - x2, 2) + pow(y1 - y2, 2))
            d2 = math.sqrt(math.pow(x1 - x3, 2) + pow(y1 - y3, 2))
            d3 = math.sqrt(math.pow(x1 - x4, 2) + pow(y1 - y4, 2))
            d4 = math.sqrt(math.pow(x2 - x3, 2) + pow(y2 - y3, 2))
            d5 = math.sqrt(math.pow(x2 - x4, 2) + pow(y2 - y4, 2))
            d6 = math.sqrt(math.pow(x3 - x4, 2) + pow(y3 - y4, 2))
            total += sum(1 - d / 50 if d < 50 else 0 for d in [d1, d2, d3, d4, d5, d6])

    return total


def draw_network(sol, img_size=(400, 400), save_name='network'):
    img = Image.new('RGB', img_size, (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # draws links
    xs = sol[::2]
    ys = sol[1::2]
    pos = dict([(people[i], (x, y)) for i, (x, y) in enumerate(zip(xs, ys))])

    for a, b in links:
        draw.line((pos[a], pos[b]), fill=(0, 0, 0))

    for name, pos_ in pos.items():
        draw.text(pos_, name, (0, 0, 0))

    img.save(save_name + '.jpeg', 'JPEG')


domain = [(10, 370)] * len(people) * 2
s = optimization.random_optimization(domain, cross_count, iter_count=1000)
print(s, cross_count(s))
# t = optimization.annealing_optimize(domain, cross_count, step=50, cooling_rate=0.99)
# print(t, cross_count(t))
draw_network(s)

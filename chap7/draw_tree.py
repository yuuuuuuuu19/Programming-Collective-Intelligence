from PIL import Image, ImageDraw


def print_tree(node, indent='\t'):
    # is this node leaf or inner node?

    if node.results is not None:
        # leaf node
        print(str(node.results))
    else:
        # inner node
        print(f"{node.col}:{node.value}?")
        print(indent + 'o ->', end=' ')
        print_tree(node.true_branch, indent + '\t')
        print(indent + 'x ->', end=' ')
        print_tree(node.false_branch, indent + '\t')


def draw_tree(root, save_name):
    scale = 100
    offset = 120
    w = get_width(root) * scale
    h = get_depth(root) * scale + offset

    img = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw_node(draw, root, w / 2, 20, scale, 100)
    img.save(save_name + '.jpeg', 'JPEG')


def draw_node(draw, node, x, y, scale, interval):
    # is this node leaf or inner node?
    if node is None:
        return
    if node.results is None:
        w1 = get_width(node.true_branch) * scale
        w2 = get_width(node.false_branch) * scale

        # determine the size of draw area
        left = x - (w1 + w2) / 2
        right = x + (w1 + w2) / 2

        draw.text((x - 20, y - 10), f'{node.col}:{node.value}?', (0, 0, 0))
        draw.text((x + 20, y + 10), 'yes', (0, 0, 0))
        draw.text((x - 40, y + 10), 'no', (0, 0, 0))

        draw.line((x, y, left + w1 / 2, y + interval), fill=(255, 0, 0))
        draw.line((x, y, right - w2 / 2, y + interval), fill=(255, 0, 0))

        draw_node(draw, node.true_branch, left + w1 / 2, y + interval, scale, interval)
        draw_node(draw, node.false_branch, right - w2 / 2, y + interval, scale, interval)

    else:
        txt = f'\n'.join([f'{k}:{v}' for k, v in node.results.items()])
        draw.text((x - 20, y), txt, (0, 0, 0))


def get_width(node):
    if node.true_branch is None and node.false_branch is None:
        return 1
    return get_width(node.true_branch) + get_width(node.false_branch)


def get_depth(node):
    if node.true_branch is None and node.false_branch is None:
        return 0
    return max(get_depth(node.true_branch), get_depth(node.false_branch)) + 1

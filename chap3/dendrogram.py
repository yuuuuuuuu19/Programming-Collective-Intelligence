from PIL import Image, ImageDraw
from functools import lru_cache


@lru_cache()
def get_height(clust):
    if not clust.left and not clust.right:
        return 1
    else:
        height = get_height(clust.left) + get_height(clust.right)
        return height


@lru_cache()
def get_depth(clust):
    if not clust.left and not clust.right:
        return 0
    else:
        depth = max(get_depth(clust.left), get_depth(clust.right)) + clust.dist
        return depth


def draw_node(draw, clust, x, y, scale, labels):
    if clust.id >= len(labels):
        left_height = get_height(clust.left) * 20
        right_height = get_height(clust.right) * 20
        top = y - (left_height + right_height) / 2
        bottom = y + (left_height + right_height) / 2
        # line length
        line_len = clust.dist * scale
        # Vertical line from this cluster to children
        draw.line((x, top + left_height / 2, x, bottom - right_height / 2), fill=(255, 0, 0))

        # Horizontal line to left item
        draw.line((x, top + left_height / 2, x + line_len, top + left_height / 2), fill=(255, 0, 0))

        # Horizontal line to right item
        draw.line((x, bottom - right_height / 2, x + line_len, bottom - right_height / 2), fill=(255, 0, 0))

        # Call the function to draw the left and right nodes
        draw_node(draw, clust.left, x + line_len, top + left_height / 2, scale, labels)
        draw_node(draw, clust.right, x + line_len, bottom - right_height / 2, scale, labels)
    else:
        # If this is an endpoint, draw the item label
        draw.text((x + 5, y - 7), labels[clust.id], (0, 0, 0))


def draw_dendrogram(clust, labels, savename="clusters"):
    # height and width
    height = get_height(clust) * 20
    width = 1200
    depth = get_depth(clust)

    # width is fixed, so scale distances accordingly
    scale = float(width - 150) / depth

    # create a new image with a white background
    img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw.line((0, height / 2, 10, height / 2), fill=(255, 0, 0))

    # draw the first node
    draw_node(draw, clust, 10, height / 2, scale, labels)
    img.save(savename + '.jpeg', 'JPEG')

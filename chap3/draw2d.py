from PIL import Image, ImageDraw


def draw_2d(data, labels, savename='mds2s'):
    n = len(data)
    img = Image.new("RGB", (2000, 2000), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    for i in range(n):
        x = (data[i][0] + 0.5) * 1000
        y = (data[i][1] + 0.5) * 1000
        draw.text((x, y), labels[i], (0, 0, 0))

    img.save(savename + '.jpeg', 'JPEG')

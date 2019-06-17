import numpy
import cv2
import time
import curses
import os


def V2I(video_name, size, time, fps):
    img_lst = []
    cap = cv2.VideoCapture(video_name)
    i = 0
    while cap.isOpened():
        flag, frame = cap.read()
        if flag:
            gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            img_resize = cv2.resize(gray_img, size, interpolation=cv2.INTER_AREA)
            i += 1
            if i > time[0] * fps and i < time[1] * fps:
                img_lst.append(img_resize)
        else:
            break

    cap.release()

    return img_lst


pixels = " .,-'`:!1+*abcdefghijklmnopqrstuvwxyz<>()\/{}[]?234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ%&@#$"


def I2Char(img):
    res = []
    # 灰度是用8位表示的，最大值为255。
    # 这里将灰度转换到0-1之间
    # 使用 numpy 的逐元素除法加速，这里 numpy 会直接对 img 中的所有元素都除以 255
    percents = img / 255

    # 将灰度值进一步转换到 0 到 (len(pixels) - 1) 之间，这样就和 pixels 里的字符对应起来了
    # 同样使用 numpy 的逐元素算法，然后使用 astype 将元素全部转换成 int 值。
    indexes = (percents * (len(pixels) - 1)).astype(numpy.int)

    # 要注意这里的顺序和 之前的 size 刚好相反（numpy 的 shape 返回 (行数、列数)）
    height, width = img.shape
    for row in range(height):
        line = ""
        for col in range(width):
            index = indexes[row][col]
            # 添加字符像素（最后面加一个空格，是因为命令行有行距却没几乎有字符间距，用空格当间距）
            line += pixels[index] + " "
        res.append(line)

    return res


def imgs2chars(imgs):
    video_chars = []
    for img in imgs:
        video_chars.append(I2Char(img))

    return video_chars


def play_video(video_chars):
    """
    播放字符视频，
    :param video_chars: 字符画的列表，每个元素为一帧
    :return: None
    """
    # 获取字符画的尺寸
    width, height = len(video_chars[0][0]), len(video_chars[0])

    # 初始化curses，这个是必须的，直接抄就行
    stdscr = curses.initscr()
    curses.start_color()
    try:
        # 调整窗口大小，宽度最好略大于字符画宽度。另外注意curses的height和width的顺序
        stdscr.resize(height, width * 2)

        for pic_i in range(len(video_chars)):
            # 显示 pic_i，即第i帧字符画
            for line_i in range(height):
                # 将pic_i的第i行写入第i列。(line_i, 0)表示从第i行的开头开始写入。最后一个参数设置字符为白色
                stdscr.addstr(line_i, 0, video_chars[pic_i][line_i], curses.COLOR_WHITE)
            stdscr.refresh()  # 写入后需要refresh才会立即更新界面

            time.sleep(1 / 25)  # 粗略地控制播放速度。更精确的方式是使用游戏编程里，精灵的概念
    finally:
        # curses 使用前要初始化，用完后无论有没有异常，都要关闭
        curses.endwin()
    return


if __name__ == "__main__":
    imgs = V2I("video.mp4", (112, 63), (6, 28), 25)
    video_chars = imgs2chars(imgs)
    input("`转换完成！按enter键开始播放")

    play_video(video_chars)

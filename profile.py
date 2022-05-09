import cv2
import urllib
import requests
import numpy as np
from PIL import Image, ImageDraw

from typing import Optional
import math
import time
import os
from random import randint
from uuid import uuid4

from general import profile_img_upload
from db import *

plain = cv2.imread("plain.jpg")[:751, :583]

shape = (plain.shape[1], plain.shape[0])
# shape = (583, 751)
image_bcg = plain[:403, :367]
image_block = (image_bcg.shape[1], image_bcg.shape[0])

title_bcg = plain[:110, :405]
title_block = (title_bcg.shape[1], title_bcg.shape[0])

d = cv2.imread("blue_stat.jpg")
detail_bcg = d[:160, :454]
detail__block = (detail_bcg.shape[1], detail_bcg.shape[0])

"""
Red: excitement, danger, energy, courage, strength, anger.
Orange: creativity, enthusiasm, health, happiness, encouragement, balance.
Yellow: sunshine, hope, optimism, light, positivity, freshness.
Green: health, nature, renewal, generosity, freshness, environment.
Blue: freedom, trust, expansiveness, dependability, faith, inspiration.
Purple: royalty, luxury, power, pride, creativity, mystery.
"""


# METHOD #1: OpenCV, NumPy, and urllib
def url_to_image(url):
    # resp = urllib.urlopen(url)
    resp = requests.get(url)
    image = np.asarray(bytearray(resp.content), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image


def ran_background(url: str = ""):
    # return all files as a list
    l = []
    a = "s\s"
    full_path = r"C:\Users\salman\Desktop\pythonproject2\cv2\first\picsum2.0" + a[1]
    for file in os.listdir(full_path):
        # print(file)
        l.append(str(file))
    num = randint(3, 700)
    image_name = str(l[num])
    # print(image_name)
    while True:
        try:
            if url:
                bcg_img = url_to_image(url)
            else:
                bcg_img = cv2.imread(full_path + image_name)

            # print("background pure", bcg_img.shape)
            ksize = (10, 10)

            image = cv2.blur(bcg_img, ksize)
            # print("background blured", image.shape)
            break
        except:
            continue

    return image


def avg_color(cv2_image):
    average_color_row = np.average(cv2_image, axis=0)
    average_color = np.average(average_color_row, axis=0)
    print("this is formated as BGR", average_color)

    return average_color
    # d_img = np.ones((312, 312, 3), dtype=np.uint8)
    #
    # d_img[:, :] = average_color
    #
    # cv2.imshow('Source image', cv2_image)
    # cv2.imshow('Average Color', d_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()


def write_to_image(cv2_image: cv2, title: str = "", ran_text: list[str] = [""]):
    l_title = len(title)
    font = cv2.FONT_HERSHEY_COMPLEX
    # wt = cv2.putText(cv2_image, title, (65, 270), font, 2, (0, 0, 0), 2, cv2.LINE_AA)
    if l_title < 8:
        f = 2
        h = 270
        new_title = title
    else:
        f = 1
        h = 250
        new_title = title[:7] + "..."
    wt = cv2.putText(img=cv2_image, text=title, org=(65, h), fontFace=font, fontScale=f,
                     color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)
    t = (100, 250)
    av = avg_color(cv2_image)
    l = 0
    for i in ran_text:
        wt = cv2.putText(img=cv2_image, text=i, org=(25, 320 + l), fontFace=font, fontScale=1,
                         color=(0, av[1] - 50, av[2] - 20), thickness=2, lineType=cv2.LINE_AA)
        l += 45
    l = len(ran_text)
    return wt


def write_to_title(cv2_image: cv2, title: str = "", property: str = ""):
    l_title = len(title)
    font = cv2.FONT_HERSHEY_COMPLEX
    # wt = cv2.putText(cv2_image, title, (65, 270), font, 2, (0, 0, 0), 2, cv2.LINE_AA)
    if l_title < 8:
        f = 2
        h = 48
        w = 65
        new_title = title
    else:
        f = 1
        h = 50
        w = 60
        new_title = title[:7] + "..."

    wt = cv2.putText(img=cv2_image, text=title, org=(w, h), fontFace=font, fontScale=f,
                     color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)

    wt = cv2.putText(img=cv2_image, text=property, org=(40, 48 + 45), fontFace=font, fontScale=1,
                     color=(100, 100, 100), thickness=1, lineType=cv2.LINE_AA)

    return wt


def write_to_detail(detail, d: dict):
    level = d.get("level") if d.get("level") else "?"
    zenni = d.get("zenni") if d.get("zenni") else "?"
    post = d.get("post") if d.get("post") else "?"
    con = [level, "level", zenni, "zenni", post, "post"]

    font = cv2.FONT_HERSHEY_COMPLEX
    d_h = detail.shape[0]
    d_w = detail.shape[1]

    w = 70
    h = 60
    f = 1

    l = [con[0], con[1]]
    wp = 0
    for i in range(0, 3):

        wi = wp if wp else w
        wt = cv2.putText(img=detail, text=str(l[0]), org=(wi, h), fontFace=font, fontScale=f,
                         color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)

        wt = cv2.putText(img=detail, text=str(l[1]), org=(w - 29, h + 50), fontFace=font, fontScale=f,
                         color=(0, 0, 0), thickness=3, lineType=cv2.LINE_AA)

        if i == 0:
            w = 200
            h = 50
            f = 1
            l = [con[2], con[3]]

        elif i == 1:
            w = 350
            wp = 340
            h = 60
            f = 1
            l = [con[4], con[5]]

    return wt


def reshape_cal(t: tuple, f: bool = True, shape_in_func=shape):
    x = t[1]
    y = t[0]

    shape = shape_in_func
    new_x = shape[0] / x
    # print("new_x", new_x)
    if f == True:
        new_y = (shape[1] / y) * (0.39)
        # print("new_y", new_y)

    elif f == False:
        new_y = shape[1] / y
        # print("new_y", new_y)
    return (new_x, new_y)


def make_circular(img):
    # Open the input image as numpy array, convert to RGB
    img = Image.open(img).convert("RGB")
    npImage = np.array(img)
    h, w = img.size

    # Create same size alpha layer with circle
    alpha = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(alpha)
    draw.pieslice([0, 0, h, w], 0, 360, fill=255)

    # Convert alpha Image to numpy array
    npAlpha = np.array(alpha)

    # Add alpha layer to RGB
    npImage = np.dstack((npImage, npAlpha))

    # Save with alpha
    Image.fromarray(npImage).save('result.png')


def run():
    print("this is plain", plain.shape)
    # img1 = cv2.imread("your_boy.jpg")
    # make_circular("your_boy.jpg")
    img1 = cv2.imread("image/result.png")
    background = cv2.imread("image/308.jpg")
    b_reshape = reshape_cal(background.shape, f=False)

    backgound = cv2.resize(background, None, fx=b_reshape[0], fy=b_reshape[1], interpolation=cv2.INTER_LINEAR)

    print("this is background", background.shape)
    new_size = reshape_cal(img1.shape)
    rez = cv2.resize(img1, None, fx=new_size[0], fy=new_size[1], interpolation=cv2.INTER_LINEAR)
    # plain[0: 212, 0: 417] = rez
    # plain[ :, :] = rez
    backgound[0: 212, 0: 417] = rez
    text_image = write_to_image(backgound, title="Makima Carue",
                                ran_text=["level: 3",
                                          "post: 34",
                                          "stat: lover",
                                          "zenni: 263",
                                          "power: eat ass"])
    cv2.imwrite("profile_your_boy.png", text_image)
    cv2.imshow("rez on plain", text_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print(rez.shape)


def new_rez(link: str = "", img_path: str = "", title_text: str = "",
            property: str = "", zenni="?", level="?", post="?",file = ""):
    print("this is new rez",file)
    height = 48
    # *********this is background*****
    background = ran_background()
    new_size = reshape_cal(t=background.shape, f=False)
    base = cv2.resize(background, None, fx=new_size[0], fy=new_size[1], interpolation=cv2.INTER_LINEAR)
    # print(base.shape)
    # cv2.imshow("base", base)
    # cv2.waitKey(1000)

    # *********this is main image*****
    if link:
        img = url_to_image(link)
    elif img_path:
        img = cv2.imread(img_path)
    else:
        return None
    new_size = reshape_cal(t=img.shape, f=False, shape_in_func=image_block)
    rez = cv2.resize(img, None, fx=new_size[0], fy=new_size[1], interpolation=cv2.INTER_LINEAR)
    rez_shape = rez.shape
    # print("this is reduced image", rez.shape)
    # cv2.imwrite("rez_new_cars.png", rez)
    # cv2.imshow("hope", rez)
    # cv2.waitKey(0)

    base[height: (height + rez_shape[0]), 108: (108 + rez_shape[1])] = rez

    height = (height + rez_shape[0]) - 30

    # cv2.imwrite("progress/rez_on_base.png", base)
    # cv2.imshow("rez_on_base", base)
    # cv2.waitKey(0)

    # *********this is title block*****

    title = title_bcg
    written = write_to_title(title, title=title_text, property=property)
    written_shape = written.shape
    base[height: (height + written_shape[0]), 91: (91 + written_shape[1])] = written

    height = height + written_shape[0]

    # cv2.imwrite("progress/title_on_base.png", base)
    # cv2.imshow("title_on_base", base)

    # *********this is stat bloc*****

    detail = detail_bcg
    written = write_to_detail(detail, d={"level": level, "zenni": zenni, "post": post})
    written_shape = written.shape
    base[height: (height + written_shape[0]), 67: (67 + written_shape[1])] = written

    height = height + written_shape[0]

    cv2.imwrite(file, base)
    # cv2.imshow("detail_on_base", base)

    # cv2.waitKey(0)

    # cv2.destroyAllWindows()
    return base


def upload_profile_to_db(chat_id, link: str = "", img_path: str = "images.jpg", title_text: str = "",
                         property: str = "hello, world", zenni="?", level="?"):
    post_db = sync_bot["post"]
    post_num = post_db["post"].count({"user_id": int(chat_id)})
    file = str(uuid4()) + ".png"
    i = new_rez(img_path=img_path, title_text=title_text, link=link,property=property,
                zenni=zenni, post=post_num, level=level,file=f"progress/{file}")
    p = profile_img_upload(name=title_text + ".png",file_obj=f"progress/{file}")
    if not p:
        print("fuck, upload didn't work")
        return False
    elif p:
        bot_doc.update_one({"chat_id": str(chat_id)}, {"$set": {"profile_card": p['url']}})
        return p['url']

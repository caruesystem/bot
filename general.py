from datetime import datetime
import time
from pprint import pprint
from imagekitio import ImageKit

from db import *
from db import bot_state


def unix_time():
    dtime = datetime.now()
    unix_time = time.mktime(dtime.timetuple())
    return float(unix_time)


def check_user_exist(chat_id):
    user = bot_doc.count({"chat_id": str(chat_id)})
    print(user)
    if user:
        print("nice")
        return True
    else:
        print("u re a failure")
        return False




def get_state(id, all_data: bool) -> dict:
    """
    params
    """
    user_state = bot_state.find_one({"chat_id": str(id)})
    if user_state:
        if all_data:
            return user_state
        else:
            return user_state["state"][-1]
    return create_state(user_id=str(id), d={"doing": None})


def update_state(user_id, d: dict):
    user_state = bot_state.find_one({"chat_id": str(user_id)})
    if user_state:
        if len(user_state["state"]) > 4:
            pprint(user_state["state"])
            user_state["state"].pop(0)

        the_time = unix_time()
        d.update({"created": the_time})
        user_state["last_update"] = the_time
        user_state["state"].append(d)
        return bot_state.update_one({"chat_id": str(user_id)}, {"$set": user_state})
    else:
        return create_state(user_id, d)


def create_state(user_id, d: dict):
    the_time = unix_time()
    ds = {"created": the_time,
          }
    ds.update(d)
    do = {"chat_id": str(user_id),
          "last_update": the_time,
          "created": the_time,
          "state": [ds]
          }
    return bot_state.insert_one(do)


PRIVATE_KEY = config("PRIVATE_KEY")
PUBLIC_KEY = config("PUBLIC_KEY")
URL_ENDPOINT = config("URL_ENDPOINT")

imagekit = ImageKit(
    private_key=PRIVATE_KEY,
    public_key=PUBLIC_KEY,
    url_endpoint=URL_ENDPOINT
)


def upload_image(name, link="", file_obj=""):
    print("this is upload", file_obj)
    file = ""
    if link:
        file = link
    elif file_obj:
        file = open(file_obj, "rb")
    elif not link and not file_obj:
        file = open("/progress/detail_on_base.png","rb")

    upload = imagekit.upload_file(
            file=file,
            file_name=name,
            options={"folder": "/display_pic/"},
        )
    if file_obj:
        file.close()
    elif not link and not file_obj:
        file.close()

    if dict(upload)["error"]:
        pprint(dict(upload)["error"])
        return False
    elif not dict(upload)["error"]:
        return dict(upload)["response"]


def profile_img_upload(name, file_obj="progress/detail_on_base.png"):
    return upload_image(name=name,file_obj=file_obj)

def dp_image_upload(name, link):
    return upload_image(name=name,link=link)

def update_doc(chat_id, d: dict):
    return bot_doc.update_one({"chat_id": str(chat_id)}, {"$set": d})


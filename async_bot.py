from aiogram import Bot, types, executor, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,\
                    ReplyKeyboardRemove, ParseMode



from db import *
from profile import *
from animesenai import entry
import general
from start import stater
from general import get_state, update_state, check_user,\
    check_user_exist, dp_image_upload, update_doc
from send import save

from pprint import pprint

login_url = config("login_url")
API_TOKEN = config("API_TOKEN")
st = ("news", "help", "start", )
# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


remove_keys = ReplyKeyboardRemove()


#
# @dp.message_handler()
# async def return_state_for_dabugging(msg: types.Message):
#     # tex = msg.text.split()[1:]
#     sent = await msg.answer("hello")
#     await bot.delete_message(sent.chat.id, sent.message_id - 2)
#
#     pprint(sent)

async def not_signed_up(message: types.Message):
    rep = f"<a href='{login_url}/signup'>click me to signup </a>"
    await message.reply(rep, parse_mode=ParseMode.HTML, reply_markup=remove_keys)



All = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
itembtn1 = types.KeyboardButton('/post')
itembtn2 = types.KeyboardButton('/news')
itembtn3 = types.KeyboardButton('/love')
itembtn4 = types.KeyboardButton('/profile')
All.add(itembtn1, itembtn2, itembtn3, itembtn4)

"""
=========================================================================
                this is where salman logic start
=========================================================================
"""

def prof_vote(message: types.Message):
    d = get_state(message.chat.id, all_data=False)
    if dict(d).get("doing") == "profile-vote":
        if message.text == 'yes use default pic' or 'send dp instead':
            return True
        return False
    return False

@dp.message_handler(prof_vote)
async def deb(msg: types.Message):
    await bot.copy_message()
    user = check_user(msg.chat.id)
    if msg.text == 'yes use default pic':
        await msg.answer("okay",reply_markup=All)
        update_state(msg.chat.id, {"doing": "create-profile-card","from": "default"})


        u = upload_profile_to_db(chat_id=str(msg.chat.id), title_text=user["dp_name"],zenni=user["balance"]["zenni"])
        if u:
            print(u)
            await msg.answer_photo(u, reply_markup=All)
        elif not u:
            await msg.answer("something went wrong when creating profile card")
    elif msg.text == 'send dp instead':
        update_state(msg.chat.id, {"doing": "creating-profile-redirect"})
        await msg.answer("send in your picture",reply_markup=All)


def profile_photo(message: types.Message):
    g = get_state(message.chat.id,False)
    if g["doing"] == "creating-profile-redirect":
        return True
    return False


@dp.message_handler(profile_photo,content_types="photo")
async def add_dp_pic(msg: types.Message):
    u = check_user(msg.chat.id)
    pic = await bot.get_file(msg.photo[-1].file_id)
    url = f"https://api.telegram.org/file/bot{config('API_TOKEN')}/{pic['file_path']}?file_id={pic['file_unique_id']}"
    print(url)
    p = dp_image_upload(u["dp_name"],link=url)
    print(p)
    await msg.answer("something went wrong when creating profile card")
    update_doc(msg.chat.id, {"display_pic": p})

    u = upload_profile_to_db(chat_id=str(msg.chat.id), link=p, title_text=u["dp_name"])
    if u:
        print(u)
        await msg.answer_photo(u, reply_markup=All)
    elif not u:
        await msg.answer("something went wrong when creating profile card")


@dp.message_handler(commands=["love"])
async def deb(msg: types.Message):
    while True:
        await msg.answer("hello, world")
        time.sleep(5.0)


@dp.message_handler(commands=["state$makima2334"])
async def return_state_for_dabugging(msg: types.Message):
    tex = msg.text.split()[1:]
    await msg.answer(str(update_state(msg.chat.id, {"doing": str(tex[0])})))
    await msg.answer(str(get_state(msg.chat.id, all_data=True)))


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    print("stater reached")
    await stater(message)


@dp.message_handler(commands=["news", "n"])
async def news(message: types.Message):
    if bot_doc.find_one({"chat_id": str(message.chat.id)}):
        # if True:
        e = {}
        for i in range(1, 5):  # why i did this is still a mystery, perhaps i was drunk while coding 😂
            try:
                e = entry()
            except:
                continue
            else:
                break

        for i in e:
            long_str = f"""
                    <strong><a href="{i["link"]}">{i["title"]}</a></strong>
    {i["date"]}
source:          {i["source"]}
                    """

            await message.answer_photo(i["img"], caption=long_str, parse_mode=ParseMode.HTML)

    else:
        await not_signed_up(message)


@dp.message_handler(commands=["help"])
async def help(msg: types.Message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    itembtn1 = types.KeyboardButton('/post')
    itembtn2 = types.KeyboardButton('/news')
    itembtn3 = types.KeyboardButton('/love')
    itembtn4 = types.KeyboardButton('/profile')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)

    if check_user_exist(str(msg.chat.id)):

        ret = open("help.txt", "r")

        await bot.send_message(msg.chat.id, str(ret.read()), reply_markup=markup)
        ret.close()
        await bot.send_message(msg.chat.id, "Choose one letter:", reply_markup=markup)
        update_state(str(msg.chat.id), {"help" : True})
    else:
        rep = f"<a href='{login_url}/signup'>click me to signup </a>"
        await msg.reply(rep, parse_mode=ParseMode.HTML, reply_markup=remove_keys)


@dp.message_handler(commands=["my_profile","profile"])
async def profile(message: types.Message):
    if check_user_exist(message.chat.id):

        Vote = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        itembtn1 = types.KeyboardButton('/help')
        itembtn2 = types.KeyboardButton('!makima')
        Vote.add(itembtn1, itembtn2)

        profile = message.text[1:]

        rez = bot_doc.find_one({"chat_id": str(message.chat.id)})

        pe = dict(rez)
        print("i got here")
        if bool(pe.get("profile_card")):
        # if False:
            print("yes the profile pic was seen but it was not sent")
            update_state(message.chat.id,{"doing": "profile-card-True"})
            await message.answer_photo(pe["profile_card"], reply_markup=Vote)

        elif bool(pe.get("display_pic")) and not bool(pe.get("profile_card")):
            print("yes the display pic was seen but profile was hmm")

            update_state(message.chat.id, {"doing": "create-profile-card"})

            dp_link = pe.get("display_pic")
            print(dp_link)
            u = upload_profile_to_db(chat_id=str(message.chat.id), link=dp_link,title_text=rez["dp_name"])
            if u:
                print(u)
                await message.answer_photo(u, reply_markup=Vote)
            elif not u:
                await message.answer("something went wrong when creating profile card")

        elif not bool(pe.get("display_pic")) and not bool(pe.get("profile_card")):
            Vote = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
            itembtn1 = types.KeyboardButton('yes use default pic')
            itembtn2 = types.KeyboardButton('send dp instead')
            Vote.add(itembtn1, itembtn2)
            update_state(message.chat.id, d = {"doing": "profile-vote"})
            await message.answer("you do not have a display picture\ndo you want to use a default",
                                 reply_markup=Vote)

        elif not bool(pe.get("profile_card")):
        # elif True:
            # salman we have not concluded what to do here
            update_state(message.chat.id,{"profile-dey": False})
            await message.answer("")

            u = upload_profile_to_db(chat_id=str(message.chat.id),title_text=rez["dp_name"])
            if u:
                print(u)
                await message.answer_photo(u, reply_markup=Vote)
            elif not u:
                await message.answer("something went wrong when uploading")
    else:
        await not_signed_up(message)


@dp.message_handler(regexp="^!")
async def profile(message: types.Message):
    Vote = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    itembtn1 = types.KeyboardButton('/news')
    itembtn2 = types.KeyboardButton('!makima')
    Vote.add(itembtn1, itembtn2)

    profile = message.text[1:]

    rez = bot_doc.find_one({"dp_name": profile})
    if rez:
        pe = dict(rez)
        if pe["profile_card"]:
            await message.answer_photo(pe["profile_card"], reply_markup=Vote)

        else:

            await message.answer(f"couldn't find any one with name{profile}")

    else:
        await message.answer(f"couldn't find any one with name{profile}")


"""
=========================================================================
                this is where salman logic end
=========================================================================
"""



"""
=========================================================================
                this is where gaming logic start
=========================================================================
"""


@dp.message_handler(commands=["play$makima2334"])
async def play_game(msg: types.Message):
    game = play_game(msg)
    if game:
        update_state(msg.chat.id, {"doing": "playing"})
        if game["content_type"] == "audio":
            options = []
            Option_key = ReplyKeyboardMarkup(resize_keyboard=True,
                                             one_time_keyboard=True,
                                             selective=True)
            for i in game["options"]:
                Option_key.add(KeyboardButton(i))

            await msg.answer_audio(game["content"], caption=game["question"], reply_markup=Option_key)

        elif game["content_type"] == "audio":
            options = []
            Option_key = ReplyKeyboardMarkup(resize_keyboard=True,
                                             one_time_keyboard=True,
                                             selective=True)
            for i in game["options"]:
                Option_key.add(KeyboardButton(i))

            await msg.answer_audio(game["content"], caption=game["question"], reply_markup=Option_key)


def is_create_game(msg: types.Message):
    get_user_state = get_state(msg.chat.id, all_data=False)
    if get_user_state:
        print("this is the user state", get_user_state)
        if get_user_state["doing"] == "crg-track":
            return True
    return False


@dp.message_handler(content_types=["audio"])
async def track_entry(msg: types.Message):
    pprint(dict(msg))
    track = await bot.get_file(file_id=msg.audio["file_id"])  # get file path
    print("\n\nget file info")
    pprint(dict(track))

    audio_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{track.file_path}?file_id={track.file_id}"
    print(audio_url)


@dp.message_handler(content_types=["photo"])
async def image_entry(msg: types.Message):
    pprint(dict(msg))

    photo = await bot.get_file(file_id=msg.photo[2]["file_id"])  # get file path
    print("\n\nget file info")
    pprint(dict(photo))
    await bot.forward_message(1120987514, from_chat_id=msg.chat.id, message_id=msg.message_id)

    # photo_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{photo.file_path}?file_id={photo.file_id}"
    # print(photo_url)
    # await bot.send_photo(msg.chat.id, photo_url)


def is_for_game(msg: types.Message):
    print(msg.text)
    if msg.text == "image📷" or msg.text == 'track📻' or msg.text == "my first time":
        g = get_state(msg.chat.id, all_data=False)
        print("it passed this part")

        if g["doing"] == "crg":
            return True
        return False
    else:
        return False


@dp.message_handler(is_for_game)
async def for_gamer(msg: types.Message):
    if msg.text == 'track📻':
        game = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        itembtn1 = types.KeyboardButton("my first time")
        itembtn2 = types.KeyboardButton('change to track📻')
        game.add(itembtn1, itembtn2)
        await msg.answer("bruh send in that tra-ack\njust send in your track", reply_markup=remove_keys)
        # await msg.delete()
        # await msg.delete_reply_markup()
        update_state(msg.chat.id, {"doing": "crg-image"})
    elif msg.text == "image📷":
        await msg.answer("bruh send in that jp-iic\njust send your picture", reply_markup=remove_keys)
        # await msg.delete()
        # await msg.delete_reply_markup()
        update_state(msg.chat.id, {"doing": "crg-track"})
    elif msg.text == "my first time":
        with open("game_help.txt", "r") as g_help:
            await msg.answer(g_help.read())  # oh yh also this
            await msg.delete()  # I jus added this after


@dp.message_handler(commands=["create_game", "crg"])
async def create_game(msg: types.Message):
    game = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    itembtn1 = types.KeyboardButton('image📷')
    itembtn2 = types.KeyboardButton('track📻')
    game.add(itembtn1, itembtn2)
    itembtn3 = types.KeyboardButton("my first time")
    game.add(itembtn3)

    user = bot_doc.find_one({"chat_id": str(msg.chat.id)})
    if user:  # check if user exist and if he his above level 3
        if user["level"] > 3:

            stat: dict = bot_state.find_one({"chat_id": str(msg.chat.id)})  # what do you think
            print("this is stat")
            pprint(stat)
            if get_state(msg.chat.id, all_data=False)["doing"] == "crg":
                await msg.answer("go ahead select a nature", reply_markup=game)
            else:
                print("this is just before the update")
                update_state(msg.chat.id, {"doing": "crg"})

                # general.create_state(msg.chat.id, {"doing": "crg"})
                game_reply = """
                    Finally let's have fun
                choose the nature of your query
                audio or image 
                """
                await msg.answer(game_reply, reply_markup=game)
        else:
            await bot.send_message(chat_id=str(msg.chat.id),
                                   text="sorry bruh you must be above level 3 to create a game")

    else:
        rep = f"<a href='{login_url}/signup'>I have no clue who you are...\n gently tap me to signup </a>"
        await msg.reply(rep, parse_mode=ParseMode.HTML)


"""
=======================================================================
                    this is where gaming logic end
=======================================================================
"""


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)

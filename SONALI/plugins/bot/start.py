import time
import random
import asyncio
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from py_yt import VideosSearch

import config
from SONALI import app
from SONALI.misc import boot
from SONALI.plugins.sudo.sudoers import sudoers_list
from SONALI.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from SONALI.utils.decorators.language import LanguageStart
from SONALI.utils.formatters import get_readable_time
from SONALI.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string

# ---------------- EFFECTS ---------------- #

NEXI_VID = [
    "https://telegra.ph/file/1a3c152717eb9d2e94dc2.mp4",
    "https://files.catbox.moe/ln00jb.mp4",
    "https://graph.org/file/83ebf52e8bbf138620de7.mp4",
    "https://files.catbox.moe/0fq20c.mp4",
    "https://graph.org/file/318eac81e3d4667edcb77.mp4",
    "https://graph.org/file/7c1aa59649fbf3ab422da.mp4",
    "https://files.catbox.moe/t0nepm.mp4",
]

EFFECT_IDS = [
    5046509860389126442,
    5107584321108051014,
    5104841245755180586,
    5159385139981059251,
]

STICKERS = [
    "CAACAgUAAxkBAAIBO2i1Spi48ZdWCNehv-GklSI9aRYWAAJ9GAACXB-pVds_sm8brMEqHgQ",
    "CAACAgUAAxkBAAIBOmi1Sogwaoh01l5-e-lJkK1VNY6MAAIlGAACKI6wVVNEvN-6z3Z7HgQ",
]

REACTIONS = ["🔥", "❤️", "🎉", "😍", "😂", "⚡", "💯"]

async def react_random(msg: Message):
    try:
        await msg.react(random.choice(REACTIONS))
    except:
        pass

# ---------------- PRIVATE START ---------------- #

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    # 🔥 effects only
    await react_random(message)
    st = await message.reply_sticker(random.choice(STICKERS))
    await asyncio.sleep(1)
    await st.delete()

    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        if name.startswith("help"):
            keyboard = help_pannel(_)
            sent = await message.reply_video(
                random.choice(NEXI_VID),
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
                message_effect_id=random.choice(EFFECT_IDS),
            )
            await react_random(sent)
            return

        if name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} just started the bot to check sudolist.\n\nUser ID: {message.from_user.id}",
                )
            return

        if name.startswith("inf"):
            m = await message.reply_text("🔎")
            query = f"https://www.youtube.com/watch?v={name.replace('info_', '', 1)}"
            results = VideosSearch(query, limit=1)

            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]

            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )

            key = InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton(text=_["S_B_8"], url=link),
                    InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_CHAT),
                ]]
            )

            await m.delete()
            sent = await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
                message_effect_id=random.choice(EFFECT_IDS),
            )
            await react_random(sent)
            return

    # 🔁 NORMAL START (OLD LOGIC)
    out = private_panel(_)
    sent = await message.reply_video(
        random.choice(NEXI_VID),
        caption=_["start_2"].format(message.from_user.mention, app.mention),
        reply_markup=InlineKeyboardMarkup(out),
        message_effect_id=random.choice(EFFECT_IDS),
    )
    await react_random(sent)

# ---------------- GROUP START ---------------- #

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    uptime = int(time.time() - boot)

    sent = await message.reply_video(
        random.choice(NEXI_VID),
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
        message_effect_id=random.choice(EFFECT_IDS),
    )
    await react_random(sent)
    await add_served_chat(message.chat.id)

# ---------------- WELCOME ---------------- #

@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            _ = get_string(await get_lang(message.chat.id))

            if await is_banned_user(member.id):
                await message.chat.ban_member(member.id)
                return

            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    sent = await message.reply_text(_["start_4"])
                    await react_random(sent)
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    sent = await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    await react_random(sent)
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                sent = await message.reply_video(
                    random.choice(NEXI_VID),
                    caption=_["start_3"].format(
                        message.from_user.mention,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                    message_effect_id=random.choice(EFFECT_IDS),
                )
                await react_random(sent)
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception as ex:
            print(ex)

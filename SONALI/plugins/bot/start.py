import time
import random
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from py_yt import VideosSearch
import config
from SONALI import app
from SONALI.misc import _boot_
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


# 🔥 YOUR PREMIUM EMOJI ID
PREMIUM_EMOJI_ID = "5420163708674384414"


# ------------------ BUTTON UPGRADE (SAFE) ------------------

def upgrade_buttons(panel):
    if not panel:
        return panel

    for i, row in enumerate(panel):
        for btn in row:

            # First Row → Premium + Blue
            if i == 0:
                btn.icon_custom_emoji_id = PREMIUM_EMOJI_ID
                btn.style = "primary"

            # Third Row → Green
            elif i == 2:
                btn.style = "success"

            # Fourth Row → Red
            elif i == 3:
                btn.style = "danger"

    return panel


# --------------------------

NEXI_VID = [
    "https://telegra.ph/file/1a3c152717eb9d2e94dc2.mp4",
    "https://files.catbox.moe/ln00jb.mp4",
    "https://graph.org/file/83ebf52e8bbf138620de7.mp4",
    "https://files.catbox.moe/0fq20c.mp4",
    "https://graph.org/file/318eac81e3d4667edcb77.mp4",
]

REACTIONS = ["🔥", "❤️", "🎉", "😍", "😂", "⚡", "💯"]


async def react_random(msg: Message):
    try:
        await app.send_reaction(
            chat_id=msg.chat.id,
            message_id=msg.id,
            reaction=random.choice(REACTIONS),
        )
    except:
        pass


# ------------------ PRIVATE START ------------------

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    await add_served_user(message.from_user.id)

    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        # HELP PANEL
        if name.startswith("help"):
            keyboard = help_pannel(_)
            keyboard = upgrade_buttons(keyboard)

            sent = await message.reply_video(
                random.choice(NEXI_VID),
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            await react_random(sent)
            return

        # SUDO LIST
        if name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} checked sudolist.\nUser ID: {message.from_user.id}",
                )
            return

        # INFO QUERY
        if name.startswith("inf"):
            m = await message.reply_text("🔎")
            query = name.replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
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

            key = [
                [
                    InlineKeyboardButton(
                        text=_["S_B_8"],
                        url=link,
                        icon_custom_emoji_id=PREMIUM_EMOJI_ID,
                        style="primary",
                    ),
                    InlineKeyboardButton(
                        text=_["S_B_9"],
                        url=config.SUPPORT_CHAT,
                    ),
                ]
            ]

            await m.delete()
            sent = await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=InlineKeyboardMarkup(key),
            )
            await react_random(sent)
            return

    # NORMAL PRIVATE START
    out = private_panel(_)
    out = upgrade_buttons(out)

    sent = await message.reply_video(
        random.choice(NEXI_VID),
        caption=_["start_2"].format(
            message.from_user.mention,
            app.mention
        ),
        reply_markup=InlineKeyboardMarkup(out),
    )

    await react_random(sent)

    if await is_on_off(2):
        await app.send_message(
            chat_id=config.LOGGER_ID,
            text=f"{message.from_user.mention} started the bot.\nUser ID: {message.from_user.id}",
        )


# ------------------ GROUP START ------------------

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    out = start_panel(_)
    out = upgrade_buttons(out)

    uptime = int(time.time() - _boot_)

    sent = await message.reply_video(
        random.choice(NEXI_VID),
        caption=_["start_1"].format(
            app.mention,
            get_readable_time(uptime)
        ),
        reply_markup=InlineKeyboardMarkup(out),
    )

    await react_random(sent)
    await add_served_chat(message.chat.id)


# ------------------ WELCOME ------------------

@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass

            if member.id == app.id:

                if message.chat.type != ChatType.SUPERGROUP:
                    return await app.leave_chat(message.chat.id)

                if message.chat.id in await blacklisted_chats():
                    return await app.leave_chat(message.chat.id)

                out = start_panel(_)
                out = upgrade_buttons(out)

                sent = await message.reply_video(
                    random.choice(NEXI_VID),
                    caption=_["start_3"].format(
                        message.from_user.mention,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )

                await react_random(sent)
                await add_served_chat(message.chat.id)

        except Exception as ex:
            print(ex)

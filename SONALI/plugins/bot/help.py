from typing import Union
from pyrogram import filters, types
from pyrogram.types import InlineKeyboardMarkup, Message, InlineKeyboardButton
from SONALI import app
from SONALI.utils import help_pannel
from SONALI.utils.database import get_lang
from SONALI.utils.decorators.language import LanguageStart, languageCB
from SONALI.utils.inline.help import help_back_markup, private_help_panel
from config import BANNED_USERS, START_IMG_URL, SUPPORT_CHAT
from strings import get_string, helpers
from SONALI.utils.stuffs.buttons import BUTTONS
from SONALI.utils.stuffs.helper import Helper
import requests
import config


# =========================
# HYBRID CONFIG
# =========================

BOT_TOKEN = config.BOT_TOKEN
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def hybrid_help_color(chat_id, message_id, panel):
    new_keyboard = []

    for row in panel:
        new_row = []
        for btn in row:
            btn_data = {"text": btn.text}

            if btn.callback_data:
                btn_data["callback_data"] = btn.callback_data
            if btn.url:
                btn_data["url"] = btn.url

            # Default → Blue
            btn_data["style"] = "primary"

            # 🔴 Close & Back → Red
            if btn.callback_data in ["close", "settingsback_helper"]:
                btn_data["style"] = "danger"

            # 🟢 Arrow buttons (Next / Previous) → Green
            if btn.text.strip() in ["‹", "›", "<", ">", "«", "»"]:
                btn_data["style"] = "success"

            new_row.append(btn_data)

        new_keyboard.append(new_row)

    try:
        requests.post(
            f"{BASE_URL}/editMessageReplyMarkup",
            json={
                "chat_id": chat_id,
                "message_id": message_id,
                "reply_markup": {"inline_keyboard": new_keyboard},
            },
            timeout=5,
        )
    except Exception as e:
        print("Hybrid Help Error:", e)

# =========================
# PRIVATE HELP OPEN
# =========================

@app.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("settings_back_helper") & ~BANNED_USERS)
async def helper_private(
    client: app, update: Union[types.Message, types.CallbackQuery]
):
    is_callback = isinstance(update, types.CallbackQuery)

    if is_callback:
        try:
            await update.answer()
        except:
            pass

        chat_id = update.message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)
        keyboard = help_pannel(_, True)

        await update.edit_message_text(
            _["help_1"].format(SUPPORT_CHAT),
            reply_markup=keyboard
        )

        hybrid_help_color(
            update.message.chat.id,
            update.message.id,
            keyboard.inline_keyboard
        )

    else:
        try:
            await update.delete()
        except:
            pass

        language = await get_lang(update.chat.id)
        _ = get_string(language)
        keyboard = help_pannel(_)

        msg = await update.reply_photo(
            photo=START_IMG_URL,
            caption=_["help_1"].format(SUPPORT_CHAT),
            reply_markup=keyboard,
        )

        hybrid_help_color(
            update.chat.id,
            msg.id,
            keyboard.inline_keyboard
        )


# =========================
# GROUP HELP
# =========================

@app.on_message(filters.command(["help"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client, message: Message, _):
    keyboard = private_help_panel(_)
    await message.reply_text(
        _["help_2"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# HELP TOPIC CALLBACK (hb1–hb15)
# =========================

@app.on_callback_query(filters.regex("help_callback") & ~BANNED_USERS)
@languageCB
async def helper_cb(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    cb = callback_data.split(None, 1)[1]
    keyboard = help_back_markup(_)

    if cb == "hb1":
        text = helpers.HELP_1
    elif cb == "hb2":
        text = helpers.HELP_2
    elif cb == "hb3":
        text = helpers.HELP_3
    elif cb == "hb4":
        text = helpers.HELP_4
    elif cb == "hb5":
        text = helpers.HELP_5
    elif cb == "hb6":
        text = helpers.HELP_6
    elif cb == "hb7":
        text = helpers.HELP_7
    elif cb == "hb8":
        text = helpers.HELP_8
    elif cb == "hb9":
        text = helpers.HELP_9
    elif cb == "hb10":
        text = helpers.HELP_10
    elif cb == "hb11":
        text = helpers.HELP_11
    elif cb == "hb12":
        text = helpers.HELP_12
    elif cb == "hb13":
        text = helpers.HELP_13
    elif cb == "hb14":
        text = helpers.HELP_14
    elif cb == "hb15":
        text = helpers.HELP_15
    else:
        return

    await CallbackQuery.edit_message_text(text, reply_markup=keyboard)

    hybrid_help_color(
        CallbackQuery.message.chat.id,
        CallbackQuery.message.id,
        keyboard.inline_keyboard
    )


# =========================
# NEXT / PREVIOUS PAGE
# =========================

@app.on_callback_query(filters.regex("mbot_cb") & ~BANNED_USERS)
async def helper_cb_page(client, CallbackQuery):
    keyboard = InlineKeyboardMarkup(BUTTONS.MBUTTON)

    await CallbackQuery.edit_message_text(
        Helper.HELP_M,
        reply_markup=keyboard
    )

    hybrid_help_color(
        CallbackQuery.message.chat.id,
        CallbackQuery.message.id,
        keyboard.inline_keyboard
    )


# =========================
# MANAGE BACK
# =========================

@app.on_callback_query(filters.regex('managebot123') & ~BANNED_USERS)
async def on_back_button(client, CallbackQuery):
    language = await get_lang(CallbackQuery.message.chat.id)
    _ = get_string(language)
    keyboard = help_pannel(_, True)

    await CallbackQuery.edit_message_text(
        _["help_1"].format(SUPPORT_CHAT),
        reply_markup=keyboard
    )

    hybrid_help_color(
        CallbackQuery.message.chat.id,
        CallbackQuery.message.id,
        keyboard.inline_keyboard
    )


# =========================
# M+ CALLBACK
# =========================

@app.on_callback_query(filters.regex('mplus') & ~BANNED_USERS)
async def mb_plugin_button(client, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    cb = callback_data.split(None, 1)[1]
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="mbot_cb")]]
    )

    if cb == "Okieeeeee":
        await CallbackQuery.edit_message_text(
            "`something errors`",
            reply_markup=keyboard
        )
    else:
        await CallbackQuery.edit_message_text(
            getattr(Helper, cb),
            reply_markup=keyboard
        )

    hybrid_help_color(
        CallbackQuery.message.chat.id,
        CallbackQuery.message.id,
        keyboard.inline_keyboard
                )

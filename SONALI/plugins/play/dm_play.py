# ============================================
# DM PERSONAL PLAY PLUGIN (SONALI COMPATIBLE)
# ============================================

from pyrogram import filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.handlers import CallbackQueryHandler, MessageHandler
from pyrogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from SONALI import app
from SONALI.core.call import RAUSHAN
from SONALI.utils.stream.stream import stream
from SONALI import YouTube

# ============================================
# ASSISTANT DETAILS (CHANGE IF NEEDED)
# ============================================

ASSISTANT_USERNAME = "@Komalmusicbots"
ASSISTANT_USER_ID = 7908141416

# chat_id -> user query
_DM_PENDING_PLAY: dict[int, str] = {}


# ============================================
# INTERNAL: ENSURE ASSISTANT DM ACCESS
# ============================================

async def _ensure_assistant_access(chat_id: int, user_username: str | None = None):
    last_err = None

    async def _try(target) -> bool:
        nonlocal last_err
        try:
            await RAUSHAN.user_app.resolve_peer(target)
            await RAUSHAN.user_app.get_chat(target)
            return True
        except Exception as e:
            last_err = e
            return False

    # Try by ID
    if await _try(chat_id):
        return

    # Try by username
    if user_username:
        uname = user_username if user_username.startswith("@") else "@" + user_username
        if await _try(uname):
            return

    # Force dialog creation
    try:
        await RAUSHAN.user_app.send_message(
            chat_id,
            "Hi 👋 Personal music playback enable ho gaya.\nAb bot me /play try karo 🎵",
        )
        await RAUSHAN.user_app.get_chat(chat_id)
        return
    except Exception as e:
        last_err = e

    raise RuntimeError(
        f"Assistant DM access failed. Open {ASSISTANT_USERNAME} and press /start.\nReason: {last_err}"
    )


# ============================================
# INTERNAL: PLAY IMPLEMENTATION (REUSES STREAM)
# ============================================

async def _dm_play_track(
    message: Message,
    query: str,
):
    user = message.from_user
    chat_id = message.chat.id

    await _ensure_assistant_access(
        chat_id,
        user_username=getattr(user, "username", None),
    )

    details, _ = await YouTube.track(query)

    await stream(
        _={},
        mystic=message,
        user_id=user.id,
        details=details,
        chat_id=chat_id,
        user_name=user.first_name,
        chatid=chat_id,
        streamtype="youtube",
        forceplay=True,
    )


# ============================================
# CALLBACK: ALLOW / CANCEL BUTTON
# ============================================

async def on_dm_permission_button(_, query: CallbackQuery):
    data = (query.data or "").strip()
    chat_id = query.message.chat.id if query.message else None

    if not chat_id:
        return await query.answer("Error", show_alert=True)

    # CANCEL
    if data == "dm:cancel_call":
        _DM_PENDING_PLAY.pop(chat_id, None)
        try:
            await query.message.edit_text(
                "<b>❌ CANCELLED</b>\n\nUse /play again whenever you want.",
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass
        return await query.answer("Cancelled")

    # ALLOW
    if data == "dm:allow_call":
        query_text = _DM_PENDING_PLAY.pop(chat_id, None)
        if not query_text:
            return await query.answer("No pending request", show_alert=True)

        await query.answer("Connecting…")

        try:
            await query.message.edit_text(
                f"<b>🔗 CONNECTING</b>\n\n"
                f"🎵 <b>{query_text[:80]}</b>\n\n"
                f"Call from <b>{ASSISTANT_USERNAME}</b>",
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass

        await _dm_play_track(query.message, query_text)
        return

    await query.answer("Unknown", show_alert=True)


# ============================================
# COMMAND: /play (DM ONLY)
# ============================================

async def dm_play_command(_, message: Message):
    if message.chat.type != ChatType.PRIVATE:
        return

    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        return await message.reply_text(
            "<b>HOW TO PLAY</b>\n\n"
            "Use /play with song name or YouTube link.\n\n"
            "<b>Examples</b>\n"
            "• /play pasoori\n"
            "• /play https://youtu.be/dQw4w9WgXcQ",
            parse_mode=ParseMode.HTML,
        )

    query = parts[1].strip()
    _DM_PENDING_PLAY[message.chat.id] = query

    kb = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Allow Call", callback_data="dm:allow_call"),
                InlineKeyboardButton("❌ Cancel", callback_data="dm:cancel_call"),
            ]
        ]
    )

    await message.reply_text(
        f"<b>📞 PERSONAL CALL REQUEST</b>\n\n"
        f"🎵 <b>{query[:80]}</b>\n\n"
        f"You will receive a call from <b>{ASSISTANT_USERNAME}</b>.\n\n"
        "Tap <b>Allow Call</b> to continue.",
        reply_markup=kb,
        parse_mode=ParseMode.HTML,
    )


# ============================================
# REGISTER HANDLERS
# ============================================

app.add_handler(
    CallbackQueryHandler(
        on_dm_permission_button,
        filters.regex(r"^dm:(allow_call|cancel_call)$"),
    )
)

app.add_handler(
    MessageHandler(
        dm_play_command,
        filters.command("play") & filters.private,
    )
)

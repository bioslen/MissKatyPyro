import traceback
from logging import getLogger

from pyrogram import Client, filters
from pyrogram.errors import (ApiIdInvalid, PasswordHashInvalid,
                             PhoneCodeExpired, PhoneCodeInvalid,
                             PhoneNumberInvalid, SessionPasswordNeeded)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from telethon import TelegramClient
from telethon.errors import (ApiIdInvalidError, PasswordHashInvalidError,
                             PhoneCodeExpiredError, PhoneCodeInvalidError,
                             PhoneNumberInvalidError,
                             SessionPasswordNeededError)
from telethon.sessions import StringSession

from misskaty import app
from misskaty.vars import API_HASH, API_ID, COMMAND_HANDLER

LOGGER = getLogger(__name__)

__MODULE__ = "Session Generator"
__HELP__ = """
/genstring - Generate string session using this bot. Only support Pyrogram v2 and Telethon.
"""


ask_ques = "**» Please choose the library for which you want generate string :**\n\nNote: I'm not collecting any personal info from this feature, you can deploy own bot if you want."
buttons_ques = [
    [
        InlineKeyboardButton("Pyrogram", callback_data="pyrogram"),
        InlineKeyboardButton("Telethon", callback_data="telethon"),
    ],
    [
        InlineKeyboardButton("Pyrogram Bot", callback_data="pyrogram_bot"),
        InlineKeyboardButton("Telethon Bot", callback_data="telethon_bot"),
    ],
]

gen_button = [
    [
        InlineKeyboardButton(text="🙄 Generate Session 🙄", callback_data="genstring")
    ]
]

async def is_batal(msg):
    if msg.text == "/cancel":
        await msg.reply("**» Cancelled the ongoing string session generation process !**", quote=True, reply_markup=InlineKeyboardMarkup(gen_button))
        return True
    elif msg.text == "/skip":
        return False
    elif msg.text.startswith("/"):  # Bot Commands
        await msg.reply("**» Cancelled the ongoing string session generation process !**", quote=True)
        return True
    else:
        return False

@Client.on_callback_query(filters.regex(pattern=r"^(generate|pyrogram|pyrogram_bot|telethon_bot|telethon)$"))
async def callbackgenstring(bot, callback_query):
    query = callback_query.matches[0].group(1)
    if query == "genstring":
        await callback_query.answer()
        await callback_query.message.reply(ask_ques, reply_markup=InlineKeyboardMarkup(buttons_ques))
    elif query.startswith("pyrogram") or query.startswith("telethon"):
        try:
            if query == "pyrogram":
                await callback_query.answer()
                await generate_session(bot, callback_query.message)
            elif query == "pyrogram_bot":
                await callback_query.answer("» ᴛʜᴇ sᴇssɪᴏɴ ɢᴇɴᴇʀᴀᴛᴇᴅ ᴡɪʟʟ ʙᴇ ᴏғ ᴩʏʀᴏɢʀᴀᴍ ᴠ2.", show_alert=True)
                await generate_session(bot, callback_query.message, is_bot=True)
            elif query == "telethon_bot":
                await callback_query.answer()
                await generate_session(bot, callback_query.message, telethon=True, is_bot=True)
            elif query == "telethon":
                await callback_query.answer()
                await generate_session(bot, callback_query.message, telethon=True)
        except Exception as e:
            LOGGER.error(traceback.format_exc())
            ERROR_MESSAGE = "Something went wrong. \n\n**ERROR** : {} " \
                "\n\n**Please forward this message to my Owner**, if this message " \
                "doesn't contain any sensitive data " \
                "because this error is **not logged by bot.** !"
            await callback_query.message.reply(ERROR_MESSAGE.format(str(e)))

@app.on_message(filters.private & ~filters.forwarded & filters.command("genstring", COMMAND_HANDLER]))
async def genstringg(_, msg):
    await msg.reply(ask_ques, reply_markup=InlineKeyboardMarkup(buttons_ques))

async def generate_session(bot, msg, telethon=False, is_bot: bool = False):
    if telethon:
        ty = "Telethon"
    else:
        ty = "Pyrogram"
    if is_bot:
        ty += " Bot"
    await msg.reply(f"» Trying to start **{ty}** session generator...")
    user_id = msg.chat.id
    api_id_msg = await bot.ask(user_id, "Please send your **API_ID** to proceed.\n\nClick on /skip for using bot's api.", filters=filters.text)
    if await is_batal(api_id_msg):
        return
    if api_id_msg.text == "/skip":
        api_id = API_ID
        api_hash = API_HASH
    else:
        try:
            api_id = int(api_id_msg.text)
        except ValueError:
            await api_id_msg.reply("**API_ID** must be integer, start generating your session again.", quote=True, reply_markup=InlineKeyboardMarkup(gen_button))
            return
        api_hash_msg = await bot.ask(user_id, "» Now please send your **API_HASH** to continue.", filters=filters.text)
        if await is_batal(api_hash_msg):
            return
        api_hash = api_hash_msg.text
    if not is_bot:
        t = "» Please send your **PHONE_NUMBER** with country code for which you want generate session. \nᴇxᴀᴍᴩʟᴇ : `+6286356837789`'"
    else:
        t = "Please send your **BOT_TOKEN** to continue.\nExample : `5432198765:abcdanonymousterabaaplol`'"
    phone_number_msg = await bot.ask(user_id, t, filters=filters.text)
    if await is_batal()(phone_number_msg):
        return
    phone_number = phone_number_msg.text
    if not is_bot:
        await msg.reply("» Trying to send OTP at the given number...")
    else:
        await msg.reply("» Trying to login using Bot Token...")
    if telethon and is_bot:
        client = TelegramClient(StringSession(), api_id, api_hash)
    elif telethon:
        client = TelegramClient(StringSession(), api_id, api_hash)
    elif is_bot:
        client = Client(name="bot", api_id=api_id, api_hash=api_hash, bot_token=phone_number, in_memory=True)
    else:
        client = Client(name="user", api_id=api_id, api_hash=api_hash, in_memory=True)
    await client.connect()
    try:
        code = None
        if not is_bot:
            if telethon:
                code = await client.send_code_request(phone_number)
            else:
                code = await client.send_code(phone_number)
    except (ApiIdInvalid, ApiIdInvalidError):
        await msg.reply("» Your **API_ID** and **API_HASH** combination doesn't match. \n\nPlease start generating your session again.", reply_markup=InlineKeyboardMarkup(gen_button))
        return
    except (PhoneNumberInvalid, PhoneNumberInvalidError):
        await msg.reply("» The **PHONE_NUMBER** you've doesn't belong to any account in Telegram.\n\nPlease start generating your session again.", reply_markup=InlineKeyboardMarkup(gen_button))
        return
    try:
        phone_code_msg = None
        if not is_bot:
            phone_code_msg = await bot.ask(user_id, "» Please send the **OTP** That you've received from Telegram on your account.\nIf OTP is `12345`, **please send it as** `1 2 3 4 5`.", filters=filters.text, timeout=600)
            if await is_batal(phone_code_msg):
                return
    except TimeoutError:
        await msg.reply("» Time limit reached of 10 minutes.\n\nPlease start generating your session again.", reply_markup=InlineKeyboardMarkup(gen_button))
        return
    if not is_bot:
        phone_code = phone_code_msg.text.replace(" ", "")
        try:
            if telethon:
                await client.sign_in(phone_number, phone_code, password=None)
            else:
                await client.sign_in(phone_number, code.phone_code_hash, phone_code)
        except (PhoneCodeInvalid, PhoneCodeInvalidError):
            await msg.reply("» The OTP you've sent is **wrong.**\n\nPlease start generating your session again.", reply_markup=InlineKeyboardMarkup(gen_button))
            return
        except (PhoneCodeExpired, PhoneCodeExpiredError):
            await msg.reply("» The OTP you've sent is **expired.**\n\nPlease start generating your session again.", reply_markup=InlineKeyboardMarkup(gen_button))
            return
        except (SessionPasswordNeeded, SessionPasswordNeededError):
            try:
                two_step_msg = await bot.ask(user_id, "» Please enter your **Two Step Verification** password to continue.", filters=filters.text, timeout=300)
            except TimeoutError:
                await msg.reply("» Time limit reached of 5 minutes.\n\nPlease start generating your session again.", reply_markup=InlineKeyboardMarkup(gen_button))
                return
            try:
                password = two_step_msg.text
                if telethon:
                    await client.sign_in(password=password)
                else:
                    await client.check_password(password=password)
                if await is_batal()(api_id_msg):
                    return
            except (PasswordHashInvalid, PasswordHashInvalidError):
                await two_step_msg.reply("» The password you've sent is wrong.\n\nPlease start generating session again.", quote=True, reply_markup=InlineKeyboardMarkup(gen_button))
                return
    else:
        if telethon:
            await client.start(bot_token=phone_number)
        else:
            await client.sign_in_bot(phone_number)
    if telethon:
        string_session = client.session.save()
    else:
        string_session = await client.export_session_string()
    text = f"**This is your {ty} String Session** \n\n`{string_session}` \n\n**Generated By :** @{client.me.username}\n🍒 **Note :** Don't share it to anyone  And don't forget to support this owner bot if you like🥺"
    try:
        if not is_bot:
            await client.send_message("me", text)
        else:
            await bot.send_message(msg.chat.id, text)
    except KeyError:
        pass
    await client.disconnect()
    await bot.send_message(msg.chat.id, "» Successfullt generated your {} String Session.\n\nPlease check saved messages to get it ! \n\n**A String Generator bot by ** @IAmCuteCodes".format("Telethon" if telethon else "Pyrogram"))
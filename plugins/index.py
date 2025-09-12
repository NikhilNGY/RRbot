import logging import asyncio from pyrogram import Client, filters, enums from pyrogram.errors import FloodWait from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified from info import ADMINS from info import INDEX_REQ_CHANNEL as LOG_CHANNEL from database.ia_filterdb import save_file from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton from utils import temp import re

logger = logging.getLogger(name) logger.setLevel(logging.INFO) lock = asyncio.Lock()

@Client.on_callback_query(filters.regex(r'^index')) async def index_files(bot, query): if query.data.startswith('index_cancel'): temp.CANCEL = True return await query.answer("Cancelling Indexing") _, raju, chat, lst_msg_id, from_user = query.data.split("#") if raju == 'reject': await query.message.delete() await bot.send_message(int(from_user), f'Your Submission for indexing {chat} has been declined by our moderators.', reply_to_message_id=int(lst_msg_id)) return

if lock.locked():
    return await query.answer('Wait until previous process complete.', show_alert=True)
msg = query.message

await query.answer('Processing...⏳', show_alert=True)
if int(from_user) not in ADMINS:
    await bot.send_message(int(from_user),
                           f'Your Submission for indexing {chat} has been accepted by our moderators and will be added soon.',
                           reply_to_message_id=int(lst_msg_id))
await msg.edit(
    "Starting Indexing",
    reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
    )
)
try:
    chat = int(chat)
except:
    chat = chat
await index_files_to_db(int(lst_msg_id), chat, msg, bot)

@Client.on_message((filters.forwarded | (filters.regex("(https://)?(t.me/|telegram.me/|telegram.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")) & filters.text ) & filters.private & filters.incoming) async def send_for_index(bot, message): try: if message.text: regex = re.compile("(https://)?(t.me/|telegram.me/|telegram.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$") match = regex.match(message.text) if not match: return await message.reply('❌ Invalid link') chat_id = match.group(4) last_msg_id = int(match.group(5)) if chat_id.isnumeric(): chat_id = int("-100" + chat_id)

elif message.forward_from_chat:
        if message.forward_from_chat.type == enums.ChatType.CHANNEL:
            last_msg_id = message.forward_from_message_id
            chat_id = message.forward_from_chat.username or message.forward_from_chat.id
        else:
            return await message.reply("❌ Only channel forwards are allowed.")

    else:
        return await message.reply("❌ Please provide a valid message link or forward from a channel.")

    try:
        await bot.get_chat(chat_id)
    except (ChannelInvalid, ChatAdminRequired):
        return await message.reply('⚠️ Private channel/group. Make me an admin to index.')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('❌ Invalid username in link.')
    except Exception as e:
        logger.exception(e)
        return await message.reply(f'❌ Unexpected Error: {e}')

    try:
        target_message = await bot.get_messages(chat_id, last_msg_id)
    except Exception:
        return await message.reply('⚠️ Failed to fetch the message. Are you sure I am an admin?')

    if target_message.empty:
        return await message.reply('❌ The target message is empty or inaccessible.')

    if message.from_user.id in ADMINS:
        buttons = [
            [InlineKeyboardButton('Yes', callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')],
            [InlineKeyboardButton('close', callback_data='close_data')],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        return await message.reply(
            f'✅ Do you want to index this Channel/Group?

Chat ID/ Username: <code>{chat_id}</code> Last Msg ID: <code>{last_msg_id}</code>', reply_markup=reply_markup )

if isinstance(chat_id, int):
        try:
            link = (await bot.create_chat_invite_link(chat_id)).invite_link
        except ChatAdminRequired:
            return await message.reply('⚠️ I need admin rights to create invite links.')
    else:
        link = f"@{message.forward_from_chat.username}"

    buttons = [
        [InlineKeyboardButton('Accept Index', callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}')],
        [InlineKeyboardButton('Reject Index', callback_data=f'index#reject#{chat_id}#{message.id}#{message.from_user.id}')],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    await bot.send_message(
        LOG_CHANNEL,
        f'#IndexRequest\n\n👤 By: {message.from_user.mention} (<code>{message.from_user.id}</code>)\n🆔 Chat ID/Username: <code>{chat_id}</code>\n📝 Last Msg ID: <code>{last_msg_id}</code>\n🔗 Invite Link: {link}',
        reply_markup=reply_markup
    )
    await message.reply('✅ Thank you for the contribution. Our moderators will verify the files soon.')

except Exception as e:
    logger.exception(e)
    await message.reply(f'❌ Unexpected failure: {e}')

async def index_files_to_db(lst_msg_id, chat, msg, bot): total_files = 0 duplicate = 0 errors = 0 deleted = 0 no_media = 0 unsupported = 0 async with lock: try: current = temp.CURRENT temp.CANCEL = False async for message in bot.iter_messages(chat, lst_msg_id, temp.CURRENT): if temp.CANCEL: await msg.edit(f"Successfully Cancelled!!\n\nSaved <code>{total_files}</code> files to dataBase!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - {unsupported} )\nErrors Occurred: <code>{errors}</code>") break current += 1 if current % 20 == 0: can = [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]] reply = InlineKeyboardMarkup(can) await msg.edit_text( text=f"Total messages fetched: <code>{current}</code>\nTotal messages saved: <code>{total_files}</code>\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - {unsupported} )\nErrors Occurred: <code>{errors}</code>", reply_markup=reply) if message.empty: deleted += 1 continue elif not message.media: no_media += 1 continue elif message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]: unsupported += 1 continue media = getattr(message, message.media.value, None) if not media: unsupported += 1 continue media.file_type = message.media.value media.caption = message.caption aynav, vnay = await save_file(media) if aynav: total_files += 1 elif vnay == 0: duplicate += 1 elif vnay == 2: errors += 1 except Exception as e: logger.exception(e) await msg.edit(f'Error: {e}') else: await msg.edit(f'Successfully saved <code>{total_files}</code> to dataBase!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - {unsupported} )\nErrors Occurred: <code>{errors}</code>')


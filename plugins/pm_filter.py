# Kanged From @TroJanZheX
import asyncio
import re
import ast
import math
import random
import pytz
from datetime import datetime, timedelta, date, time
lock = asyncio.Lock()

from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, make_inactive
from info import ADMINS, AUTH_CHANNEL, AUTH_USERS, SUPPORT_CHAT_ID, CUSTOM_FILE_CAPTION, MSG_ALRT, PICS, AUTH_GROUPS, P_TTI_SHOW_OFF, GRP_LNK, CHNL_LNK, NOR_IMG, LOG_CHANNEL, MAX_B_TN, IMDB, SINGLE_BUTTON, IMDB_TEMPLATE, NO_RESULTS_MSG, TUTORIAL, REQST_CHANNEL, IS_TUTORIAL, LANGUAGES, SEASONS, SUPPORT_CHAT, PREMIUM_USER
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, get_shortlink, get_tutorial, send_all, get_cap
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results, get_bad_files
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
from database.gfilters_mdb import (
    find_gfilter,
    get_gfilters,
    del_allg
)
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Global Variables
BUTTON = {}
BUTTONS = {}
FRESH = {}
BUTTONS0 = {}
BUTTONS1 = {}
BUTTONS2 = {}

@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    if message.chat.id != SUPPORT_CHAT_ID:
        manual = await manual_filters(client, message)
        if manual == False:
            settings = await get_settings(message.chat.id)
            try:
                if settings['auto_ffilter']:
                    await auto_filter(client, message)
            except KeyError:
                grpid = await active_connection(str(message.from_user.id))
                await save_group_settings(grpid, 'auto_ffilter', True)
                settings = await get_settings(message.chat.id)
                if settings['auto_ffilter']:
                    await auto_filter(client, message) 
    else:
        # Better logic to avoid repeated lines of code in auto_filter function
        search = message.text
        temp_files, temp_offset, total_results = await get_search_results(chat_id=message.chat.id, query=search.lower(), offset=0, filter=True)
        if total_results == 0:
            return
        else:
            return await message.reply_text(f"<b>Há´‡Ê {message.from_user.mention}, {str(total_results)} Ê€á´‡sá´œÊŸá´›s á´€Ê€á´‡ Ò“á´á´œÉ´á´… ÉªÉ´ á´Ê á´…á´€á´›á´€Ê™á´€sá´‡ Ò“á´Ê€ Êá´á´œÊ€ Ç«á´œá´‡Ê€Ê {search}. \n\nTÊœÉªs Éªs á´€ sá´œá´˜á´˜á´Ê€á´› É¢Ê€á´á´œá´˜ sá´ á´›Êœá´€á´› Êá´á´œ á´„á´€É´'á´› É¢á´‡á´› Ò“ÉªÊŸá´‡s Ò“Ê€á´á´ Êœá´‡Ê€á´‡...\n\nJá´ÉªÉ´ á´€É´á´… Sá´‡á´€Ê€á´„Êœ Há´‡Ê€á´‡ - @KR_PICTURE</b>")

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    
    if content.startswith("/") or content.startswith("#"): 
        return  # ignore commands and hashtags
    if user_id in ADMINS: 
        return # ignore admins
        
    await message.reply_text(
         text=f"<b>Êœá´‡Ê {user} ðŸ˜ ,\n\nÊá´á´œ á´„á´€É´'á´› É¢á´‡á´› á´á´á´ Éªá´‡s êœ°Ê€á´á´ Êœá´‡Ê€á´‡. Ê€á´‡Ç«á´œá´‡sá´› Éªá´› ÉªÉ´ á´á´œÊ€ <a href=https://telegram.me/KR_PICTURE>á´á´á´ Éªá´‡ É¢Ê€á´á´œá´˜</a> á´Ê€ á´„ÊŸÉªá´„á´‹ Ê€á´‡Ç«á´œá´‡sá´› Êœá´‡Ê€á´‡ Ê™á´œá´›á´›á´É´ Ê™á´‡ÊŸá´á´¡ ðŸ‘‡</b>",   
         reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ðŸ“ Ê€á´‡Ç«á´œá´‡sá´› Êœá´‡Ê€á´‡ ", url=GRP_LNK)]])
    )
    
    await bot.send_message(
        chat_id=LOG_CHANNEL,
        text=f"<b>#ððŒ_ðŒð’ð†\n\nNá´€á´á´‡ : {user}\n\nID : {user_id}\n\nMá´‡ssá´€É¢á´‡ : {content}</b>"
    )

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    
    try:
        offset = int(offset)
    except:
        offset = 0
        
    if BUTTONS.get(key) != None:
        search = BUTTONS.get(key)
    else:
        search = FRESH.get(key)
        
    if not search:
        await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
        return

    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=offset, filter=True)
    
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
        
    temp.GETALL[key] = files
    temp.SHORT[query.from_user.id] = query.message.chat.id
    settings = await get_settings(query.message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    
    if settings['button']:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'), file.file_name.split()))}", 
                    callback_data=f'{pre}#{file.file_id}'
                ),
            ]
            for file in files
        ]

        btn.insert(0, 
            [
                InlineKeyboardButton("â€¢ Bá´€á´„á´‹á´œá´˜ CÊœá´€É´É´á´‡ÊŸ â€¢", url=f"https://t.me/KR_Picture")
            ]
        )
    else:
        btn = []
        btn.insert(0, 
            [
                InlineKeyboardButton("â€¢ Bá´€á´„á´‹á´œá´˜ CÊœá´€É´É´á´‡ÊŸ â€¢", url=f"https://t.me/KR_Picture")
            ]
        )
        
    try:
        if settings['max_btn']:
            if 0 < offset <= 8:
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - 8
                
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("âŒ« ðð€ð‚ðŠ", callback_data=f"next_{req}_{key}_{off_set}"), 
                     InlineKeyboardButton(f"{math.ceil(int(offset)/8)+1} / {math.ceil(total/8)}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([
                    InlineKeyboardButton("ðð€ð†ð„", callback_data="pages"), 
                    InlineKeyboardButton(f"{math.ceil(int(offset)/8)+1} / {math.ceil(total/8)}", callback_data="pages"), 
                    InlineKeyboardButton("ðð„ð—ð“ âžª", callback_data=f"next_{req}_{key}_{n_offset}")
                ])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("âŒ« ðð€ð‚ðŠ", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/8)+1} / {math.ceil(total/8)}", callback_data="pages"),
                        InlineKeyboardButton("ðð„ð—ð“ âžª", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
        else:
            if 0 < offset <= int(MAX_B_TN):
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - int(MAX_B_TN)
                
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("âŒ« ðð€ð‚ðŠ", callback_data=f"next_{req}_{key}_{off_set}"), 
                     InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([
                    InlineKeyboardButton("ðð€ð†ð„", callback_data="pages"), 
                    InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"), 
                    InlineKeyboardButton("ðð„ð—ð“ âžª", callback_data=f"next_{req}_{key}_{n_offset}")
                ])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("âŒ« ðð€ð‚ðŠ", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"),
                        InlineKeyboardButton("ðð„ð—ð“ âžª", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
    except KeyError:
        await save_group_settings(query.message.chat.id, 'max_btn', True)
        if 0 < offset <= 8:
            off_set = 0
        elif offset == 0:
            off_set = None
        else:
            off_set = offset - 8
            
        if n_offset == 0:
            btn.append(
                [InlineKeyboardButton("âŒ« ðð€ð‚ðŠ", callback_data=f"next_{req}_{key}_{off_set}"), 
                 InlineKeyboardButton(f"{math.ceil(int(offset)/8)+1} / {math.ceil(total/8)}", callback_data="pages")]
            )
        elif off_set is None:
            btn.append([
                InlineKeyboardButton("ðð€ð†ð„", callback_data="pages"), 
                InlineKeyboardButton(f"{math.ceil(int(offset)/8)+1} / {math.ceil(total/8)}", callback_data="pages"), 
                InlineKeyboardButton("ðð„ð—ð“ âžª", callback_data=f"next_{req}_{key}_{n_offset}")
            ])
        else:
            btn.append(
                [
                    InlineKeyboardButton("âŒ« ðð€ð‚ðŠ", callback_data=f"next_{req}_{key}_{off_set}"),
                    InlineKeyboardButton(f"{math.ceil(int(offset)/8)+1} / {math.ceil(total/8)}", callback_data="pages"),
                    InlineKeyboardButton("ðð„ð—ð“ âžª", callback_data=f"next_{req}_{key}_{n_offset}")
                ],
            )
            
    if not settings["button"]:
        cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
        remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
        cap = await get_cap(settings, remaining_seconds, files, query, total, search)
        try:
            await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        except MessageNotModified:
            pass
    else:
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
    await query.answer()
 
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    try:
        link = await client.create_chat_invite_link(int(REQST_CHANNEL))
    except:
        pass
        
    if query.data == "close_data":
        await query.message.delete()
        
    elif query.data == "gfiltersdeleteallconfirm":
        await del_allg(query.message, 'gfilters')
        await query.answer("Done !")
        return
        
    elif query.data == "gfiltersdeleteallcancel": 
        await query.message.reply_to_message.delete()
        await query.message.delete()
        await query.answer("Process Cancelled !")
        return
        
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Má´€á´‹á´‡ sá´œÊ€á´‡ I'á´ á´˜Ê€á´‡sá´‡É´á´› ÉªÉ´ Êá´á´œÊ€ É¢Ê€á´á´œá´˜!!", quote=True)
                    return await query.answer(MSG_ALRT)
            else:
                await query.message.edit_text(
                    "I'á´ É´á´á´› á´„á´É´É´á´‡á´„á´›á´‡á´… á´›á´ á´€É´Ê É¢Ê€á´á´œá´˜s!\nCÊœá´‡á´„á´‹ /connections á´Ê€ á´„á´É´É´á´‡á´„á´› á´›á´ á´€É´Ê É¢Ê€á´á´œá´˜s",
                    quote=True
                )
                return await query.answer(MSG_ALRT)

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title
        else:
            return await query.answer(MSG_ALRT)

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("Yá´á´œ É´á´‡á´‡á´… á´›á´ Ê™á´‡ GÊ€á´á´œá´˜ Oá´¡É´á´‡Ê€ á´Ê€ á´€É´ Aá´œá´›Êœ Usá´‡Ê€ á´›á´ á´…á´ á´›Êœá´€á´›!", show_alert=True)
            
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("TÊœá´€á´›'s É´á´á´› Ò“á´Ê€ Êá´á´œ!!", show_alert=True)
                
    elif "groupcb" in query.data:
        await query.answer()
        group_id = query.data.split(":")[1]
        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"GÊ€á´á´œá´˜ Ná´€á´á´‡ : **{title}**\nGÊ€á´á´œá´˜ ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer(MSG_ALRT)
        
    elif "connectcb" in query.data:
        await query.answer()
        group_id = query.data.split(":")[1]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id
        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Cá´É´É´á´‡á´„á´›á´‡á´… á´›á´ **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Sá´á´á´‡ á´‡Ê€Ê€á´Ê€ á´á´„á´„á´œÊ€Ê€á´‡á´…!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer(MSG_ALRT)
        
    elif "disconnect" in query.data:
        await query.answer()
        group_id = query.data.split(":")[1]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id
        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"DÉªsá´„á´É´É´á´‡á´„á´›á´‡á´… Ò“Ê€á´á´ **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Sá´á´á´‡ á´‡Ê€Ê€á´Ê€ á´á´„á´„á´œÊ€Ê€á´‡á´…!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
        
    elif "deletecb" in query.data:
        await query.answer()
        user_id = query.from_user.id
        group_id = query.data.split(":")[1]
        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Sá´œá´„á´„á´‡ssÒ“á´œÊŸÊŸÊ á´…á´‡ÊŸá´‡á´›á´‡á´… á´„á´É´É´á´‡á´„á´›Éªá´É´ !"
            )
        else:
            await query.message.edit_text(
                f"Sá´á´á´‡ á´‡Ê€Ê€á´Ê€ á´á´„á´„á´œÊ€Ê€á´‡á´…!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
        
    elif query.data == "backcb":
        await query.answer()
        userid = query.from_user.id
        groupids = await all_connections(str(userid))
        
        if groupids is None:
            await query.message.edit_text(
                "TÊœá´‡Ê€á´‡ á´€Ê€á´‡ É´á´ á´€á´„á´›Éªá´ á´‡ á´„á´É´É´á´‡á´„á´›Éªá´É´s!! Cá´É´É´á´‡á´„á´› á´›á´ sá´á´á´‡ É¢Ê€á´á´œá´˜s Ò“ÉªÊ€sá´›.",
            )
            return await query.answer(MSG_ALRT)
            
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
                
        if buttons:
            await query.message.edit_text(
                "Yá´á´œÊ€ á´„á´É´É´á´‡á´„á´›á´‡á´… É¢Ê€á´á´œá´˜ á´…á´‡á´›á´€ÉªÊŸs ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            
    elif "gfilteralert" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_gfilter('gfilters', keyword)
        
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
            
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
        
    # File handling section
    if query.data.startswith("file"):
        clicked = query.from_user.id
        try:
            typed = query.message.reply_to_message.from_user.id
        except:
            typed = query.from_user.id
            
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        
        if not files_:
            return await query.answer('Ná´ sá´œá´„Êœ Ò“ÉªÊŸá´‡ á´‡xÉªsá´›.')
            
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(
                    file_name='' if title is None else title,
                    file_size='' if size is None else size,
                    file_caption='' if f_caption is None else f_caption
                )
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
            
        if f_caption is None:
            f_caption = f"{files.file_name}"

        try:
            if settings['is_shortlink'] and clicked not in PREMIUM_USER:
                if clicked == typed:
                    temp.SHORT[clicked] = query.message.chat.id
                    await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=short_{file_id}")
                    return
                else:
                    await query.answer(f"Há´‡Ê {query.from_user.first_name}, TÊœÉªs Is Ná´á´› Yá´á´œÊ€ Má´á´ Éªá´‡ Rá´‡Ç«á´œá´‡sá´›. Rá´‡Ç«á´œá´‡sá´› Yá´á´œÊ€'s !", show_alert=True)
            else:
                if clicked == typed:
                    await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start={ident}_{file_id}")
                    return
                else:
                    await query.answer(f"Há´‡Ê {query.from_user.first_name}, TÊœÉªs Is Ná´á´› Yá´á´œÊ€ Má´á´ Éªá´‡ Rá´‡Ç«á´œá´‡sá´›. Rá´‡Ç«á´œá´‡sá´› Yá´á´œÊ€'s !", show_alert=True)
        except UserIsBlocked:
            await query.answer('UÉ´Ê™ÊŸá´á´„á´‹ á´›Êœá´‡ Ê™á´á´› á´á´€ÊœÉ´ !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start={ident}_{file_id}")
            
    elif query.data.startswith("sendfiles"):
        clicked = query.from_user.id
        ident, key = query.data.split("#")
        settings = await get_settings(query.message.chat.id)
        
        try:
            if settings['is_shortlink'] and clicked not in PREMIUM_USER:
                await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles1_{key}")
                return
            else:
                await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=allfiles_{key}")
                return
        except UserIsBlocked:
            await query.answer('UÉ´Ê™ÊŸá´á´„á´‹ á´›Êœá´‡ Ê™á´á´› á´á´€ÊœÉ´ !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles3_{key}")
        except Exception as e:
            logger.exception(e)
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles4_{key}")
    
    elif query.data.startswith("del"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        
        if not files_:
            return await query.answer('Ná´ sá´œá´„Êœ Ò“ÉªÊŸá´‡ á´‡xÉªsá´›.')
            
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(
                    file_name='' if title is None else title,
                    file_size='' if size is None else size,
                    file_caption='' if f_caption is None else f_caption
                )
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
            
        if f_caption is None:
            f_caption = f"{files.file_name}"
            
        await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=file_{file_id}")
    
    elif query.data.startswith("checksub"):
        ident, mc = query.data.split("#")
        btn = await is_subscribed(client, query)
        
        if btn:
            await query.answer(f"Hello {query.from_user.first_name},\nPlease join our Sponsored channels and try again.", show_alert=True)
            btn.append(
                [InlineKeyboardButton("ðŸ” Try Again ðŸ”", callback_data=f"checksub#{mc}")]
            )
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
            return
            
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start={mc}")
        await query.message.delete()
    
    elif query.data == "pages":
        await query.answer()
    
    elif query.data.startswith("send_fsall"):
        temp_var, ident, key, offset = query.data.split("#")
        search = BUTTON0.get(key)
        
        if not search:
            await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
            return
            
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        
        search = BUTTONS1.get(key)
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        
        search = BUTTONS2.get(key)
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        
        await query.answer(f"Hey {query.from_user.first_name}, All files on this page has been sent successfully to your PM !", show_alert=True)
        
    elif query.data.startswith("send_fall"):
        temp_var, ident, key, offset = query.data.split("#")
        
        if BUTTONS.get(key) != None:
            search = BUTTONS.get(key)
        else:
            search = FRESH.get(key)
            
        if not search:
            await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
            return
            
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        await query.answer(f"Hey {query.from_user.first_name}, All files on this page has been sent successfully to your PM !", show_alert=True)
        
    elif query.data.startswith("killfilesdq"):
        ident, keyword = query.data.split("#")
        files, total = await get_bad_files(keyword)
        await query.message.edit_text("<b>File deletion process will start in 5 seconds !</b>")
        await asyncio.sleep(5)
        deleted = 0
        
        async with lock:
            try:
                for file in files:
                    file_ids = file.file_id
                    file_name = file.file_name
                    result = await Media.collection.delete_one({
                        '_id': file_ids,
                    })
                    if result.deleted_count:
                        logger.info(f'File Found for your query {keyword}! Successfully deleted {file_name} from database.')
                    deleted += 1
                    if deleted % 20 == 0:
                        await query.message.edit_text(f"<b>Process started for deleting files from DB. Successfully deleted {str(deleted)} files from DB for your query {keyword} !\n\nPlease wait...</b>")
            except Exception as e:
                logger.exception(e)
                await query.message.edit_text(f'Error: {e}')
            else:
                await query.message.edit_text(f"<b>Process Completed for file deletion !\n\nSuccessfully deleted {str(deleted)} files from database for your query {keyword}.</b>")
    
    elif query.data.startswith("opnsetgrp"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(userid) not in ADMINS
        ):
            await query.answer("Yá´á´œ Dá´É´'á´› Há´€á´ á´‡ TÊœá´‡ RÉªÉ¢Êœá´›s Tá´ Dá´ TÊœÉªs !", show_alert=True)
            return
            
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        
        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Rá´‡sá´œÊŸá´› Pá´€É¢á´‡',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Bá´œá´›á´›á´É´' if settings["button"] else 'Tá´‡xá´›',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('FÉªÊŸá´‡ Sá´‡É´á´… Má´á´…á´‡', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Má´€É´á´œá´€ÊŸ Sá´›á´€Ê€á´›' if settings["botpm"] else 'Aá´œá´›á´ Sá´‡É´á´…',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('PÊ€á´á´›á´‡á´„á´› Cá´É´á´›á´‡É´á´›',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('âœ” OÉ´' if settings["file_secure"] else 'âœ˜ OÒ“Ò“',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Iá´á´…Ê™', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('âœ” OÉ´' if settings["imdb"] else 'âœ˜ OÒ“Ò“',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Wá´‡ÊŸá´„á´á´á´‡ MsÉ¢', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('âœ” OÉ´' if settings["welcome"] else 'âœ˜ OÒ“Ò“',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aá´œá´›á´-Dá´‡ÊŸá´‡á´›á´‡',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('5 MÉªÉ´s' if settings["auto_delete"] else 'âœ˜ OÒ“Ò“',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aá´œá´›á´-FÉªÊŸá´›á´‡Ê€',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('âœ” OÉ´' if settings["auto_ffilter"] else 'âœ˜ OÒ“Ò“',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Má´€x Bá´œá´›á´›á´É´s',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('8' if settings["max_btn"] else f'{MAX_B_TN}',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('SÊœá´Ê€á´›LÉªÉ´á´‹',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                    InlineKeyboardButton('âœ” OÉ´' if settings["is_shortlink"] else 'âœ˜ OÒ“Ò“',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_text(
                text=f"<b>CÊœá´€É´É¢á´‡ Yá´á´œÊ€ Sá´‡á´›á´›ÉªÉ´É¢s Fá´Ê€ {title} As Yá´á´œÊ€ WÉªsÊœ âš™</b>",
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML
            )
            await query.message.edit_reply_markup(reply_markup)
        
    elif query.data.startswith("opnsetpm"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(userid) not in ADMINS
        ):
            await query.answer("Yá´á´œ Dá´É´'á´› Há´€á´ á´‡ TÊœá´‡ RÉªÉ¢Êœá´›s Tá´ Dá´ TÊœÉªs !", show_alert=True)
            return
            
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        btn2 = [[
                 InlineKeyboardButton("CÊœá´‡á´„á´‹ PM", url=f"telegram.me/{temp.U_NAME}")
               ]]
        reply_markup = InlineKeyboardMarkup(btn2)
        await query.message.edit_text(f"<b>Yá´á´œÊ€ sá´‡á´›á´›ÉªÉ´É¢s á´á´‡É´á´œ Ò“á´Ê€ {title} Êœá´€s Ê™á´‡á´‡É´ sá´‡É´á´› á´›á´ Êá´á´œÊ€ PM</b>")
        await query.message.edit_reply_markup(reply_markup)
        
        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Rá´‡sá´œÊŸá´› Pá´€É¢á´‡',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Bá´œá´›á´›á´É´' if settings["button"] else 'Tá´‡xá´›',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('FÉªÊŸá´‡ Sá´‡É´á´… Má´á´…á´‡', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Má´€É´á´œá´€ÊŸ Sá´›á´€Ê€á´›' if settings["botpm"] else 'Aá´œá´›á´ Sá´‡É´á´…',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('PÊ€á´á´›á´‡á´„á´› Cá´É´á´›á´‡É´á´›',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('âœ” OÉ´' if settings["file_secure"] else 'âœ˜ OÒ“Ò“',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Iá´á´…Ê™', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('âœ” OÉ´' if settings["imdb"] else 'âœ˜ OÒ“Ò“',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Wá´‡ÊŸá´„á´á´á´‡ MsÉ¢', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('âœ” OÉ´' if settings["welcome"] else 'âœ˜ OÒ“Ò“',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aá´œá´›á´-Dá´‡ÊŸá´‡á´›á´‡',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('5 MÉªÉ´s' if settings["auto_delete"] else 'âœ˜ OÒ“Ò“',
                                         callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Aá´œá´›á´-FÉªÊŸá´›á´‡Ê€',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('âœ” OÉ´' if settings["auto_ffilter"] else 'âœ˜ OÒ“Ò“',
                                         callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Má´€x Bá´œá´›á´›á´É´s',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('8' if settings["max_btn"] else f'{MAX_B_TN}',
                                         callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('SÊœá´Ê€á´›LÉªÉ´á´‹',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                    InlineKeyboardButton('âœ” OÉ´' if settings["is_shortlink"] else 'âœ˜ OÒ“Ò“',
                                         callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await client.send_message(
                chat_id=userid,
                text=f"<b>CÊœá´€É´É¢á´‡ Yá´á´œÊ€ Sá´‡á´›á´›ÉªÉ´É¢s Fá´Ê€ {title} As Yá´á´œÊ€ WÉªsÊœ âš™</b>",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=query.message.id
            )

    elif query.data.startswith("show_option"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("UÉ´á´€á´ á´€ÉªÊŸá´€Ê™ÊŸá´‡", callback_data=f"unavailable#{from_user}"),
                InlineKeyboardButton("Uá´˜ÊŸá´á´€á´…á´‡á´…", callback_data=f"uploaded#{from_user}")
             ],[
                InlineKeyboardButton("AÊŸÊ€á´‡á´€á´…Ê Aá´ á´€ÉªÊŸá´€Ê™ÊŸá´‡", callback_data=f"already_available#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton("VÉªá´‡á´¡ Sá´›á´€á´›á´œs", url=f"{query.message.link}")
               ]]
               
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Há´‡Ê€á´‡ á´€Ê€á´‡ á´›Êœá´‡ á´á´˜á´›Éªá´É´s !")
        else:
            await query.answer("Yá´á´œ á´…á´É´'á´› Êœá´€á´ á´‡ sá´œÒ“Ò“Éªá´„Éªá´€É´á´› Ê€ÉªÉ¢Êœá´›s á´›á´ á´…á´ á´›ÊœÉªs !", show_alert=True)
        
    elif query.data.startswith("unavailable"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("âš ï¸ UÉ´á´€á´ á´€ÉªÊŸá´€Ê™ÊŸá´‡ âš ï¸", callback_data=f"unalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton('Já´ÉªÉ´ CÊœá´€É´É´á´‡ÊŸ', url=link.invite_link),
                 InlineKeyboardButton("VÉªá´‡á´¡ Sá´›á´€á´›á´œs", url=f"{query.message.link}")
               ]]
               
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sá´‡á´› á´›á´ UÉ´á´€á´ á´€ÉªÊŸá´€Ê™ÊŸá´‡ !")
            
            try:
                await client.send_message(
                    chat_id=int(from_user), 
                    text=f"<b>Há´‡Ê {user.mention}, Sá´Ê€Ê€Ê Yá´á´œÊ€ Ê€á´‡Ç«á´œá´‡sá´› Éªs á´œÉ´á´€á´ á´€ÉªÊŸá´€Ê™ÊŸá´‡. Sá´ á´á´œÊ€ á´á´á´…á´‡Ê€á´€á´›á´Ê€s á´„á´€É´'á´› á´œá´˜ÊŸá´á´€á´… Éªá´›.</b>", 
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
            except UserIsBlocked:
                await client.send_message(
                    chat_id=int(SUPPORT_CHAT_ID), 
                    text=f"<b>Há´‡Ê {user.mention}, Sá´Ê€Ê€Ê Yá´á´œÊ€ Ê€á´‡Ç«á´œá´‡sá´› Éªs á´œÉ´á´€á´ á´€ÉªÊŸá´€Ê™ÊŸá´‡. Sá´ á´á´œÊ€ á´á´á´…á´‡Ê€á´€á´›á´Ê€s á´„á´€É´'á´› á´œá´˜ÊŸá´á´€á´… Éªá´›.\n\nNá´á´›á´‡: TÊœÉªs á´á´‡ssá´€É¢á´‡ Éªs sá´‡É´á´› á´›á´ á´›ÊœÉªs É¢Ê€á´á´œá´˜ Ê™á´‡á´„á´€á´œsá´‡ Êá´á´œ'á´ á´‡ Ê™ÊŸá´á´„á´‹á´‡á´… á´›Êœá´‡ Ê™á´á´›. Tá´ sá´‡É´á´… á´›ÊœÉªs á´á´‡ssá´€É¢á´‡ á´›á´ Êá´á´œÊ€ PM, Má´œsá´› á´œÉ´Ê™ÊŸá´á´„á´‹ á´›Êœá´‡ Ê™á´á´›.</b>", 
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
        else:
            await query.answer("Yá´á´œ á´…á´É´'á´› Êœá´€á´ á´‡ sá´œÒ“Ò“Éªá´„Éªá´€É´á´› Ê€ÉªÉ¢Êœá´›s á´›á´ á´…á´ á´›ÊœÉªs !", show_alert=True)

    elif query.data.startswith("uploaded"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("âœ… Uá´˜ÊŸá´á´€á´…á´‡á´… âœ…", callback_data=f"upalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton('Já´ÉªÉ´ CÊœá´€É´É´á´‡ÊŸ', url=link.invite_link),
                 InlineKeyboardButton("VÉªá´‡á´¡ Sá´›á´€á´›á´œs", url=f"{query.message.link}")
               ],[
                 InlineKeyboardButton("Rá´‡Ç«á´œá´‡sá´› GÊ€á´á´œá´˜ LÉªÉ´á´‹", url=GRP_LNK)
               ]]
               
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sá´‡á´› á´›á´ Uá´˜ÊŸá´á´€á´…á´‡á´… !")
            
            try:
                await client.send_message(
                    chat_id=int(from_user), 
                    text=f"<b>Há´‡Ê {user.mention}, Yá´á´œÊ€ Ê€á´‡Ç«á´œá´‡sá´› Êœá´€s Ê™á´‡á´‡É´ á´œá´˜ÊŸá´á´€á´…á´‡á´… Ê™Ê á´á´œÊ€ á´á´á´…á´‡Ê€á´€á´›á´Ê€s. KÉªÉ´á´…ÊŸÊ sá´‡á´€Ê€á´„Êœ ÉªÉ´ á´á´œÊ€ GÊ€á´á´œá´˜.</b>", 
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
            except UserIsBlocked:
                await client.send_message(
                    chat_id=int(SUPPORT_CHAT_ID), 
                    text=f"<b>Há´‡Ê {user.mention}, Yá´á´œÊ€ Ê€á´‡Ç«á´œá´‡sá´› Êœá´€s Ê™á´‡á´‡É´ á´œá´˜ÊŸá´á´€á´…á´‡á´… Ê™Ê á´á´œÊ€ á´á´á´…á´‡Ê€á´€á´›á´Ê€s. KÉªÉ´á´…ÊŸÊ sá´‡á´€Ê€á´„Êœ ÉªÉ´ á´á´œÊ€ GÊ€á´á´œá´˜.\n\nNá´á´›á´‡: TÊœÉªs á´á´‡ssá´€É¢á´‡ Éªs sá´‡É´á´› á´›á´ á´›ÊœÉªs É¢Ê€á´á´œá´˜ Ê™á´‡á´„á´€á´œsá´‡ Êá´á´œ'á´ á´‡ Ê™ÊŸá´á´„á´‹á´‡á´… á´›Êœá´‡ Ê™á´á´›. Tá´ sá´‡É´á´… á´›ÊœÉªs á´á´‡ssá´€É¢á´‡ á´›á´ Êá´á´œÊ€ PM, Má´œsá´› á´œÉ´Ê™ÊŸá´á´„á´‹ á´›Êœá´‡ Ê™á´á´›.</b>", 
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
        else:
            await query.answer("Yá´á´œ á´…á´É´'á´› Êœá´€á´ á´‡ sá´œÒ“Ò“Éªá´„Éªá´€É´á´› Ê€ÉªÉ¢Êœá´›s á´›á´ á´…á´ á´›ÊœÉªs !", show_alert=True)

    elif query.data.startswith("already_available"):
        ident, from_user = query.data.split("#")
        btn = [[
                InlineKeyboardButton("â™»ï¸ AÊŸÊ€á´‡á´€á´…Ê Aá´ á´€ÉªÊŸá´€Ê™ÊŸá´‡ â™»ï¸", callback_data=f"alalert#{from_user}")
              ]]
        btn2 = [[
                 InlineKeyboardButton('Já´ÉªÉ´ CÊœá´€É´É´á´‡ÊŸ', url=link.invite_link),
                 InlineKeyboardButton("VÉªá´‡á´¡ Sá´›á´€á´›á´œs", url=f"{query.message.link}")
               ],[
                 InlineKeyboardButton("Rá´‡Ç«á´œá´‡sá´› GÊ€á´á´œá´˜ LÉªÉ´á´‹", url=GRP_LNK)
               ]]
               
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Sá´‡á´› á´›á´ AÊŸÊ€á´‡á´€á´…Ê Aá´ á´€ÉªÊŸá´€Ê™ÊŸá´‡ !")
            
            try:
                await client.send_message(
                    chat_id=int(from_user), 
                    text=f"<b>Há´‡Ê {user.mention}, Yá´á´œÊ€ Ê€á´‡Ç«á´œá´‡sá´› Éªs á´€ÊŸÊ€á´‡á´€á´…Ê á´€á´ á´€ÉªÊŸá´€Ê™ÊŸá´‡ ÉªÉ´ á´á´œÊ€ É¢Ê€á´á´œá´˜. KÉªÉ´á´…ÊŸÊ sá´‡á´€Ê€á´„Êœ á´›Êœá´‡Ê€á´‡.</b>", 
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
            except UserIsBlocked:
                await client.send_message(
                    chat_id=int(SUPPORT_CHAT_ID), 
                    text=f"<b>Há´‡Ê {user.mention}, Yá´á´œÊ€ Ê€á´‡Ç«á´œá´‡sá´› Éªs á´€ÊŸÊ€á´‡á´€á´…Ê á´€á´ á´€ÉªÊŸá´€Ê™ÊŸá´‡ ÉªÉ´ á´á´œÊ€ É¢Ê€á´á´œá´˜. KÉªÉ´á´…ÊŸÊ sá´‡á´€Ê€á´„Êœ á´›Êœá´‡Ê€á´‡.\n\nNá´á´›á´‡: TÊœÉªs á´á´‡ssá´€É¢á´‡ Éªs sá´‡É´á´› á´›á´ á´›ÊœÉªs É¢Ê€á´á´œá´˜ Ê™á´‡á´„á´€á´œsá´‡ Êá´á´œ'á´ á´‡ Ê™ÊŸá´á´„á´‹á´‡á´… á´›Êœá´‡ Ê™á´á´›. Tá´ sá´‡É´á´… á´›ÊœÉªs á´á´‡ssá´€É¢á´‡ á´›á´ Êá´á´œÊ€ PM, Má´œsá´› á´œÉ´Ê™ÊŸá´á´„á´‹ á´›Êœá´‡ Ê™á´á´›.</b>", 
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
        else:
            await query.answer("Yá´á´œ á´…á´É´'á´› Êœá´€á´ á´‡ sá´œÒ“Ò“Éªá´„Éªá´€É´á´› Ê€ÉªÉ¢Êœá´›s á´›á´ á´…á´ á´›ÊœÉªs !", show_alert=True)

    # Additional callback handlers for alerts
    elif query.data.startswith("unalert") or query.data.startswith("upalert") or query.data.startswith("alalert"):
        await query.answer("âš ï¸ TÊœÉªs Éªs á´Šá´œsá´› á´€É´ ÉªÉ´Ò“á´Ê€á´á´€á´›Éªá´ á´‡ á´á´‡ssá´€É¢á´‡ !", show_alert=True)

# Additional helper functions that might be needed
async def manual_filters(client, message):
    """Handle manual filters"""
    # This function should be implemented based on your filter logic
    # Return True if manual filter was found and processed, False otherwise
    return False

async def auto_filter(client, message):
    """Handle auto filter functionality"""
    # This function should be implemented based on your auto filter logic
    # This is where the main search and display logic would go
    pass

# You can add any additional functions that are referenced but not included in the original code

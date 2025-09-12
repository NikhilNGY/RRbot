from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from pyrogram.errors import ChatAdminRequired
import asyncio

# Import configurations and utilities
from info import ADMINS, LOG_CHANNEL, SUPPORT_CHAT, MELCOW_NEW_USERS, MELCOW_VID, CHNL_LNK, GRP_LNK
from database.users_chats_db import db
from database.ia_filterdb import Media
from utils import get_size, temp, get_settings
from Script import script

"""-----------------------------------------https://t.me/KR_PICTURE --------------------------------------"""

# ========================================
# NEW CHAT MEMBERS HANDLER
# ========================================

@Client.on_message(filters.new_chat_members & filters.group)
async def save_group(bot, message):
    """Handle new chat members and bot addition to groups"""
    
    # Get list of new member IDs
    new_member_ids = [user.id for user in message.new_chat_members]
    
    # Check if bot was added to the group
    if temp.ME in new_member_ids:
        await handle_bot_added_to_group(bot, message)
    else:
        await handle_new_user_joined(bot, message)


async def handle_bot_added_to_group(bot, message):
    """Handle when bot is added to a new group"""
    
    # Add chat to database if not exists
    if not await db.get_chat(message.chat.id):
        total_members = await bot.get_chat_members_count(message.chat.id)
        added_by = message.from_user.mention if message.from_user else "Anonymous"
        
        # Log the new group addition
        await bot.send_message(
            LOG_CHANNEL, 
            script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total_members, added_by)
        )
        await db.add_chat(message.chat.id, message.chat.title)
    
    # Check if chat is banned
    if message.chat.id in temp.BANNED_CHATS:
        await handle_banned_chat(bot, message)
        return
    
    # Send welcome message for bot
    await send_bot_welcome_message(message)


async def handle_banned_chat(bot, message):
    """Handle banned chat scenario"""
    
    buttons = [[
        InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    warning_message = await message.reply(
        text='<b>CHAT NOT ALLOWED ðŸž\n\nMy admins has restricted me from working here ! '
             'If you want to know more about it contact support..</b>',
        reply_markup=reply_markup,
    )
    
    # Try to pin the warning message
    try:
        await warning_message.pin()
    except:
        pass
    
    # Leave the banned chat
    await bot.leave_chat(message.chat.id)


async def send_bot_welcome_message(message):
    """Send welcome message when bot is added"""
    
    buttons = [[
        InlineKeyboardButton('Sá´œá´˜á´˜á´Ê€á´› GÊ€á´á´œá´˜', url=GRP_LNK),
        InlineKeyboardButton('Uá´˜á´…á´€á´›á´‡s CÊœá´€É´É´á´‡ÊŸ', url=CHNL_LNK)
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await message.reply_text(
        text=f"<b>Thankyou For Adding Me In {message.chat.title} â£ï¸\n\n"
             f"If you have any questions & doubts about using me contact support.</b>",
        reply_markup=reply_markup
    )


async def handle_new_user_joined(bot, message):
    """Handle when new users join the group"""
    
    settings = await get_settings(message.chat.id)
    
    if settings["welcome"]:
        for user in message.new_chat_members:
            await send_user_welcome_video(message, user)
            
        # Auto-delete welcome message if enabled
        if settings["auto_delete"]:
            await asyncio.sleep(6000)  # Wait 100 minutes
            try:
                await temp.MELCOW['welcome'].delete()
            except:
                pass


async def send_user_welcome_video(message, user):
    """Send welcome video for new user"""
    
    # Delete previous welcome message if exists
    if temp.MELCOW.get('welcome') is not None:
        try:
            await temp.MELCOW['welcome'].delete()
        except:
            pass
    
    # Send new welcome video
    buttons = [[
        InlineKeyboardButton('Sá´œá´˜á´˜á´Ê€á´› GÊ€á´á´œá´˜', url=GRP_LNK),
        InlineKeyboardButton('Uá´˜á´…á´€á´›á´‡s CÊœá´€É´É´á´‡ÊŸ', url=CHNL_LNK)
    ]]
    
    temp.MELCOW['welcome'] = await message.reply_video(
        video=MELCOW_VID,
        caption=script.MELCOW_ENG.format(user.mention, message.chat.title),
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )


# ========================================
# ADMIN COMMANDS
# ========================================

@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_chat_command(bot, message):
    """Admin command to make bot leave a specific chat"""
    
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    
    chat_id = message.command[1]
    
    # Convert to int if possible
    try:
        chat_id = int(chat_id)
    except:
        pass
    
    try:
        # Send goodbye message
        buttons = [[
            InlineKeyboardButton('Support Group', url=GRP_LNK),
            InlineKeyboardButton('Owner', url="https://t.me/NIKHIL5757H")
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await bot.send_message(
            chat_id=chat_id,
            text='<b>Hello Friends, \nMy admin has told me to leave from group, so i go! '
                 'If you wanna add me again contact my Support Group or My Owner</b>',
            reply_markup=reply_markup,
        )
        
        # Leave the chat
        await bot.leave_chat(chat_id)
        await message.reply(f"Successfully left the chat `{chat_id}`")
        
    except Exception as e:
        await message.reply(f'Error - {e}')


@Client.on_message(filters.command('disable') & filters.user(ADMINS))
async def disable_chat_command(bot, message):
    """Admin command to disable a chat"""
    
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    
    # Parse command arguments
    command_parts = message.text.split(None)
    if len(command_parts) > 2:
        chat_id = command_parts[1]
        reason = message.text.split(None, 2)[2]
    else:
        chat_id = message.command[1]
        reason = "No reason provided"
    
    # Validate chat ID
    try:
        chat_id = int(chat_id)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    
    # Check if chat exists in database
    chat_data = await db.get_chat(chat_id)
    if not chat_data:
        return await message.reply("Chat Not Found In DB")
    
    # Check if already disabled
    if chat_data['is_disabled']:
        return await message.reply(
            f"This chat is already disabled:\nReason: <code>{chat_data['reason']}</code>"
        )
    
    # Disable the chat
    await db.disable_chat(chat_id, reason)
    temp.BANNED_CHATS.append(chat_id)
    await message.reply('Chat Successfully Disabled')
    
    # Send notification and leave chat
    try:
        buttons = [[
            InlineKeyboardButton('Support', url=GRP_LNK)
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await bot.send_message(
            chat_id=chat_id,
            text=f'<b>Hello Friends, \nMy admin has told me to leave from group so i go! '
                 f'If you wanna add me again contact my support group.</b> \n'
                 f'Reason: <code>{reason}</code>',
            reply_markup=reply_markup
        )
        await bot.leave_chat(chat_id)
        
    except Exception as e:
        await message.reply(f"Error - {e}")


@Client.on_message(filters.command('enable') & filters.user(ADMINS))
async def enable_chat_command(bot, message):
    """Admin command to re-enable a disabled chat"""
    
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    
    chat_id = message.command[1]
    
    # Validate chat ID
    try:
        chat_id = int(chat_id)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    
    # Check chat status
    chat_data = await db.get_chat(chat_id)
    if not chat_data:
        return await message.reply("Chat Not Found In DB!")
    
    if not chat_data.get('is_disabled'):
        return await message.reply('This chat is not yet disabled.')
    
    # Re-enable the chat
    await db.re_enable_chat(chat_id)
    temp.BANNED_CHATS.remove(chat_id)
    await message.reply("Chat Successfully re-enabled")


@Client.on_message(filters.command('stats') & filters.incoming)
async def get_stats_command(bot, message):
    """Get bot statistics"""
    
    status_message = await message.reply('Fetching stats..')
    
    # Gather statistics
    total_users = await db.total_users_count()
    total_chats = await db.total_chat_count()
    total_files = await Media.count_documents()
    db_size = await db.get_db_size()
    free_space = 536870912 - db_size  # 512MB - used space
    
    # Format sizes
    formatted_db_size = get_size(db_size)
    formatted_free_space = get_size(free_space)
    
    # Send formatted statistics
    await status_message.edit(
        script.STATUS_TXT.format(
            total_files, total_users, total_chats, 
            formatted_db_size, formatted_free_space
        )
    )


@Client.on_message(filters.command('invite') & filters.user(ADMINS))
async def generate_invite_link(bot, message):
    """Admin command to generate invite link for a chat"""
    
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    
    chat_id = message.command[1]
    
    # Validate chat ID
    try:
        chat_id = int(chat_id)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    
    try:
        # Generate invite link
        invite_link = await bot.create_chat_invite_link(chat_id)
        await message.reply(f'Here is your Invite Link: {invite_link.invite_link}')
        
    except ChatAdminRequired:
        return await message.reply(
            "Invite Link Generation Failed, I am not having sufficient rights"
        )
    except Exception as e:
        return await message.reply(f'Error: {e}')


# ========================================
# USER MANAGEMENT COMMANDS
# ========================================

@Client.on_message(filters.command('ban') & filters.user(ADMINS))
async def ban_user_command(bot, message):
    """Admin command to ban a user"""
    
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')
    
    # Parse command arguments
    command_parts = message.text.split(None)
    if len(command_parts) > 2:
        user_identifier = command_parts[1]
        reason = message.text.split(None, 2)[2]
    else:
        user_identifier = message.command[1]
        reason = "No reason provided"
    
    # Convert to int if possible
    try:
        user_identifier = int(user_identifier)
    except:
        pass
    
    try:
        # Get user information
        user = await bot.get_users(user_identifier)
        
        # Check if user is already banned
        ban_status = await db.get_ban_status(user.id)
        if ban_status['is_banned']:
            return await message.reply(
                f"{user.mention} is already banned\nReason: {ban_status['ban_reason']}"
            )
        
        # Ban the user
        await db.ban_user(user.id, reason)
        temp.BANNED_USERS.append(user.id)
        await message.reply(f"Successfully banned {user.mention}")
        
    except PeerIdInvalid:
        return await message.reply(
            "This is an invalid user, make sure I have met them before."
        )
    except IndexError:
        return await message.reply(
            "This might be a channel, make sure it's a user."
        )
    except Exception as e:
        return await message.reply(f'Error - {e}')


@Client.on_message(filters.command('unban') & filters.user(ADMINS))
async def unban_user_command(bot, message):
    """Admin command to unban a user"""
    
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')
    
    # Parse command arguments
    command_parts = message.text.split(None)
    if len(command_parts) > 2:
        user_identifier = command_parts[1] 
        reason = message.text.split(None, 2)[2]
    else:
        user_identifier = message.command[1]
        reason = "No reason provided"
    
    # Convert to int if possible
    try:
        user_identifier = int(user_identifier)
    except:
        pass
    
    try:
        # Get user information
        user = await bot.get_users(user_identifier)
        
        # Check ban status
        ban_status = await db.get_ban_status(user.id)
        if not ban_status['is_banned']:
            return await message.reply(f"{user.mention} is not yet banned.")
        
        # Unban the user
        await db.remove_ban(user.id)
        temp.BANNED_USERS.remove(user.id)
        await message.reply(f"Successfully unbanned {user.mention}")
        
    except PeerIdInvalid:
        return await message.reply(
            "This is an invalid user, make sure I have met them before."
        )
    except IndexError:
        return await message.reply(
            "This might be a channel, make sure it's a user."
        )
    except Exception as e:
        return await message.reply(f'Error - {e}')


# ========================================
# LIST COMMANDS
# ========================================

@Client.on_message(filters.command('users') & filters.user(ADMINS))
async def list_users_command(bot, message):
    """Admin command to list all users"""
    
    status_message = await message.reply('Getting List Of Users')
    
    # Get all users from database
    users = await db.get_all_users()
    output_text = "Users Saved In DB Are:\n\n"
    
    # Build user list
    async for user in users:
        output_text += f"<a href=tg://user?id={user['id']}>{user['name']}</a>"
        if user['ban_status']['is_banned']:
            output_text += ' ( Banned User )'
        output_text += '\n'
    
    # Send the list (handle long messages)
    try:
        await status_message.edit_text(output_text)
    except MessageTooLong:
        # Create file if message is too long
        with open('users.txt', 'w+', encoding='utf-8') as file:
            file.write(output_text)
        await message.reply_document('users.txt', caption="List Of Users")


@Client.on_message(filters.command('chats') & filters.user(ADMINS))
async def list_chats_command(bot, message):
    """Admin command to list all chats"""
    
    status_message = await message.reply('Getting List Of Chats')
    
    # Get all chats from database
    chats = await db.get_all_chats()
    output_text = "Chats Saved In DB Are:\n\n"
    
    # Build chat list
    async for chat in chats:
        output_text += f"**Title:** `{chat['title']}`\n**ID:** `{chat['id']}`"
        if chat['chat_status']['is_disabled']:
            output_text += ' ( Disabled Chat )'
        output_text += '\n\n'
    
    # Send the list (handle long messages)
    try:
        await status_message.edit_text(output_text)
    except MessageTooLong:
        # Create file if message is too long
        with open('chats.txt', 'w+', encoding='utf-8') as file:
            file.write(output_text)
        await message.reply_document('chats.txt', caption="List Of Chats")


# ========================================
# UTILITY FUNCTIONS
# ========================================

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"


async def log_admin_action(action, admin_id, target, reason=None):
    """Log admin actions for audit purposes"""
    log_message = f"Admin Action: {action}\n"
    log_message += f"Admin ID: {admin_id}\n"
    log_message += f"Target: {target}\n"
    if reason:
        log_message += f"Reason: {reason}\n"
    
    # This could be expanded to log to a specific channel or database
    print(log_message)  # For now, just print to console


# ========================================
# ERROR HANDLERS
# ========================================

async def handle_command_error(message, error):
    """Generic error handler for commands"""
    error_message = f"An error occurred: {str(error)}"
    await message.reply(error_message)
    
    # Log the error for debugging
    print(f"Command Error: {error}")


# ========================================
# END OF FILE
# ========================================
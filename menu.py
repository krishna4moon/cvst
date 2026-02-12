from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from pyrogram.errors import FloodWait, ChatAdminRequired
from db import db
from vars import *
import os
import time
import asyncio
from datetime import datetime

# Image URLs from original code
photologo = 'https://i.ibb.co/v6Vr7HCt/1000003297.png'
photoyt = 'https://i.ibb.co/v6Vr7HCt/1000003297.png'
photocp = 'https://i.ibb.co/v6Vr7HCt/1000003297.png'
photozip = 'https://i.ibb.co/v6Vr7HCt/1000003297.png'

async def get_main_menu_keyboard(user_id, is_authorized, is_admin):
    """Create main menu keyboard based on user status"""
    if not is_authorized:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 Get Premium", callback_data="premium_plans")],
            [InlineKeyboardButton("📞 Contact", url="https://t.me/ITsGOLU_OWNER_BOT"),
             InlineKeyboardButton("❓ Help", callback_data="help")],
            [InlineKeyboardButton("🆔 Get ID", callback_data="get_id")]
        ])
    
    if is_admin:
        buttons = [
            [InlineKeyboardButton("📥 DRM Download", callback_data="drm_menu"),
             InlineKeyboardButton("⚙️ Settings", callback_data="settings_menu")],
            [InlineKeyboardButton("🛠️ Tools", callback_data="tools_menu"),
             InlineKeyboardButton("👑 Admin Panel", callback_data="admin_menu")],
            [InlineKeyboardButton("📊 Stats", callback_data="stats"),
             InlineKeyboardButton("📋 Plans", callback_data="premium_plans")],
            [InlineKeyboardButton("📂 Topics", callback_data="topics_menu"),
             InlineKeyboardButton("🆔 My ID", callback_data="get_id")],
            [InlineKeyboardButton("📞 Contact", url="https://t.me/ITsGOLU_OWNER_BOT")]
        ]
    else:
        buttons = [
            [InlineKeyboardButton("📥 DRM Download", callback_data="drm_menu"),
             InlineKeyboardButton("⚙️ Settings", callback_data="settings_menu")],
            [InlineKeyboardButton("🛠️ Tools", callback_data="tools_menu"),
             InlineKeyboardButton("📋 My Plan", callback_data="my_plan")],
            [InlineKeyboardButton("💎 Premium Plans", callback_data="premium_plans"),
             InlineKeyboardButton("📂 Topics", callback_data="topics_menu")],
            [InlineKeyboardButton("🆔 My ID", callback_data="get_id"),
             InlineKeyboardButton("📞 Contact", url="https://t.me/ITsGOLU_OWNER_BOT")]
        ]
    return InlineKeyboardMarkup(buttons)

async def get_settings_keyboard(user_id):
    """Create settings menu keyboard"""
    prefs = db.get_user_preferences(user_id)
    font_color = prefs.get('font_color', 'white')
    font_style = prefs.get('font_style', 'default')
    video_thumb = "✅ Custom" if prefs.get('video_thumb') != "/d" else "❌ Default"
    pdf_thumb = "✅ Custom" if prefs.get('pdf_thumb') != "/d" else "❌ Default"
    auto_topic = "✅ ON" if prefs.get('auto_topic') else "❌ OFF"
    topic_mode = prefs.get('topic_mode', 'none')
    topic_mode_display = {
        'auto': '✅ Auto',
        'manual': '📝 Manual',
        'none': '❌ None',
        'per_batch': '📦 Per Batch',
        'per_video': '🎬 Per Video'
    }.get(topic_mode, f'📌 {topic_mode}')
    add_credit = "✅ ON" if prefs.get('add_credit') else "❌ OFF"
    pdf_watermark = "✅ ON" if prefs.get('pdf_watermark') != "/d" else "❌ OFF"
    video_watermark = "✅ ON" if prefs.get('video_watermark') != "/d" else "❌ OFF"
    quality = prefs.get('video_quality', '480')
    pdf_hyperlinks = "✅ ON" if prefs.get('pdf_hyperlinks') else "❌ OFF"
    token_status = "✅ Set" if prefs.get('token') != "/d" else "❌ Not Set"
    
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🎨 Font Color ({font_color})", callback_data="set_font_color")],
        [InlineKeyboardButton(f"📝 Font Style ({font_style})", callback_data="set_font_style")],
        [InlineKeyboardButton(f"📁 File Name Format", callback_data="set_file_name")],
        [InlineKeyboardButton(f"🖼️ Video Thumb ({video_thumb})", callback_data="set_video_thumb")],
        [InlineKeyboardButton(f"📄 PDF Thumb ({pdf_thumb})", callback_data="set_pdf_thumb")],
        [InlineKeyboardButton(f"📌 Topic Mode ({topic_mode_display})", callback_data="set_topic_mode")],
        [InlineKeyboardButton(f"©️ Add Credit ({add_credit})", callback_data="toggle_add_credit")],
        [InlineKeyboardButton(f"💧 PDF Watermark ({pdf_watermark})", callback_data="set_pdf_watermark")],
        [InlineKeyboardButton(f"🎬 Video Watermark ({video_watermark})", callback_data="set_video_watermark")],
        [InlineKeyboardButton(f"⚡ Video Quality ({quality}p)", callback_data="set_video_quality")],
        [InlineKeyboardButton(f"🔗 PDF Hyperlinks ({pdf_hyperlinks})", callback_data="toggle_pdf_hyperlinks")],
        [InlineKeyboardButton(f"🔑 Set Token ({token_status})", callback_data="set_token")],
        [InlineKeyboardButton(f"📢 Default Channel", callback_data="set_default_channel")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ])

async def get_topic_mode_keyboard():
    """Create topic mode selection keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ No Topic (None)", callback_data="topic_mode_none")],
        [InlineKeyboardButton("🤖 Auto Create Topic", callback_data="topic_mode_auto")],
        [InlineKeyboardButton("📝 Manual Command (/topic)", callback_data="topic_mode_manual")],
        [InlineKeyboardButton("📦 One Topic Per Batch", callback_data="topic_mode_per_batch")],
        [InlineKeyboardButton("🎬 Separate Topic Per Video", callback_data="topic_mode_per_video")],
        [InlineKeyboardButton("🔙 Back to Settings", callback_data="settings_menu")]
    ])

async def get_topics_menu_keyboard(user_id, channel_id=None):
    """Create topics management keyboard"""
    buttons = [
        [InlineKeyboardButton("📌 Set Topic Mode", callback_data="set_topic_mode")],
        [InlineKeyboardButton("➕ Create New Topic", callback_data="create_topic")],
        [InlineKeyboardButton("📋 List All Topics", callback_data="list_topics")],
        [InlineKeyboardButton("🗑️ Delete Topic", callback_data="delete_topic")],
        [InlineKeyboardButton("📤 Upload to Topic", callback_data="upload_to_topic")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(buttons)

async def get_tools_keyboard():
    """Create tools menu keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Text → .txt", callback_data="tool_text_to_txt"),
         InlineKeyboardButton("✏️ Edit .txt", callback_data="tool_edit_txt")],
        [InlineKeyboardButton("✂️ Split .txt", callback_data="tool_split_txt"),
         InlineKeyboardButton("🔄 Replace Word", callback_data="tool_replace_word")],
        [InlineKeyboardButton("🌐 HTML Formatter", callback_data="tool_html_formatter"),
         InlineKeyboardButton("🔍 Keyword Filter", callback_data="tool_keyword_filter")],
        [InlineKeyboardButton("🧹 Title Clean", callback_data="tool_title_clean"),
         InlineKeyboardButton("📜 PW (.sh → .txt)", callback_data="tool_pw_converter")],
        [InlineKeyboardButton("▶️ YouTube Extract", callback_data="tool_youtube_extract")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ])

async def get_drm_keyboard():
    """Create DRM download menu keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 Single Video", callback_data="drm_single"),
         InlineKeyboardButton("📋 Batch Process", callback_data="drm_batch")],
        [InlineKeyboardButton("📑 PDF Download", callback_data="drm_pdf"),
         InlineKeyboardButton("🖼️ Image Download", callback_data="drm_image")],
        [InlineKeyboardButton("🎵 Audio Download", callback_data="drm_audio")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ])

async def get_admin_keyboard():
    """Create admin panel keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add User", callback_data="admin_add_user"),
         InlineKeyboardButton("➖ Remove User", callback_data="admin_remove_user")],
        [InlineKeyboardButton("📋 List Users", callback_data="admin_list_users"),
         InlineKeyboardButton("📊 Bot Stats", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
         InlineKeyboardButton("🧹 Clean Files", callback_data="admin_clean")],
        [InlineKeyboardButton("📜 View Logs", callback_data="admin_logs"),
         InlineKeyboardButton("⚙️ System Config", callback_data="admin_config")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ])

async def get_plans_keyboard():
    """Create premium plans keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 7 Days - ₹400", callback_data="buy_plan_7")],
        [InlineKeyboardButton("💰 15 Days - ₹600", callback_data="buy_plan_15")],
        [InlineKeyboardButton("💰 30 Days - ₹1000", callback_data="buy_plan_30")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
    ])

async def get_font_color_keyboard():
    """Create font color selection keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚪ White", callback_data="font_color_white"),
         InlineKeyboardButton("🔵 Blue", callback_data="font_color_blue")],
        [InlineKeyboardButton("🟢 Green", callback_data="font_color_green"),
         InlineKeyboardButton("🔴 Red", callback_data="font_color_red")],
        [InlineKeyboardButton("🟡 Yellow", callback_data="font_color_yellow"),
         InlineKeyboardButton("🟣 Purple", callback_data="font_color_purple")],
        [InlineKeyboardButton("🔙 Back to Settings", callback_data="settings_menu")]
    ])

async def get_font_style_keyboard():
    """Create font style selection keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📄 Default", callback_data="font_style_default")],
        [InlineKeyboardButton("🖋️ Bold", callback_data="font_style_bold")],
        [InlineKeyboardButton("✍️ Italic", callback_data="font_style_italic")],
        [InlineKeyboardButton("💻 Monospace", callback_data="font_style_monospace")],
        [InlineKeyboardButton("🔙 Back to Settings", callback_data="settings_menu")]
    ])

async def get_video_quality_keyboard():
    """Create video quality selection keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("144p", callback_data="quality_144"),
         InlineKeyboardButton("240p", callback_data="quality_240"),
         InlineKeyboardButton("360p", callback_data="quality_360")],
        [InlineKeyboardButton("480p", callback_data="quality_480"),
         InlineKeyboardButton("720p", callback_data="quality_720"),
         InlineKeyboardButton("1080p", callback_data="quality_1080")],
        [InlineKeyboardButton("🔙 Back to Settings", callback_data="settings_menu")]
    ])

async def show_main_menu(client, message, user_id, edit=False):
    """Display main menu to user"""
    is_authorized = db.is_user_authorized(user_id, client.me.username)
    is_admin = db.is_admin(user_id)
    
    if is_authorized:
        welcome_text = (
            f"**WELCOME TO OUR TEAM ADVANCED UPLOADER**\n"
            f"Join Our Team\n\n"
            f"ID: `{user_id}`\n\n"
            f"**Welcome Back!**"
        )
    else:
        welcome_text = (
            f"**WELCOME TO OUR TEAM ADVANCED UPLOADER**\n"
            f"Join Our Team\n\n"
            f"ID: `{user_id}`\n\n"
            f"⚠️ Premium required for full access.\n"
            f"🔒 Use /id to get your Chat ID & share with owner if needed."
        )
    
    keyboard = await get_main_menu_keyboard(user_id, is_authorized, is_admin)
    
    if edit:
        try:
            await message.edit_media(
                media=InputMediaPhoto(media=photologo, caption=welcome_text),
                reply_markup=keyboard
            )
        except:
            await message.edit_caption(
                caption=welcome_text,
                reply_markup=keyboard
            )
    else:
        await message.reply_photo(
            photo=photologo,
            caption=welcome_text,
            reply_markup=keyboard
        )

async def create_channel_topic(client, channel_id, topic_name):
    """Create a topic/thread in a channel"""
    try:
        # For supergroups with topics enabled
        message = await client.send_message(
            chat_id=channel_id,
            text=f"📌 **Topic:** {topic_name}\n━━━━━━━━━━━━━━━"
        )
        
        # Store topic information in database
        db.create_channel_topic(channel_id, topic_name, message.id)
        
        return message.id
    except ChatAdminRequired:
        return None
    except Exception as e:
        print(f"Error creating topic: {e}")
        return None

async def upload_to_topic(client, channel_id, topic_id, file_path, caption, thumb=None, duration=None):
    """Upload content to a specific topic/thread"""
    try:
        sent_message = await client.send_video(
            chat_id=channel_id,
            video=file_path,
            caption=caption,
            supports_streaming=True,
            thumb=thumb,
            duration=duration,
            reply_to_message_id=topic_id
        )
        return sent_message
    except Exception as e:
        print(f"Error uploading to topic: {e}")
        return None

def register_menu_handlers(bot: Client):
    """Register all menu callback handlers"""
    
    @bot.on_callback_query()
    async def handle_callback(client: Client, callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        data = callback_query.data
        
        # ============= MAIN MENU NAVIGATION =============
        
        if data == "back_to_main":
            await show_main_menu(client, callback_query.message, user_id, edit=True)
            await callback_query.answer()
        
        elif data == "premium_plans":
            await callback_query.message.edit_media(
                media=InputMediaPhoto(media=photologo, caption="**💎 Premium Plans**\n\nUnlock full speed, automation & priority support now!"),
                reply_markup=await get_plans_keyboard()
            )
            await callback_query.answer()
        
        elif data.startswith("buy_plan_"):
            days = data.split("_")[2]
            price = PLAN_PRICES.get(days, 0)
            await callback_query.message.edit_caption(
                caption=f"**💎 Purchase Premium**\n\n"
                       f"📅 Plan: {days} Days\n"
                       f"💰 Price: ₹{price}\n\n"
                       f"📞 Contact admin to complete payment:\n"
                       f"@ITsGOLU_OWNER_BOT\n\n"
                       f"Please send payment screenshot with your User ID: `{user_id}`",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📞 Contact Admin", url="https://t.me/ITsGOLU_OWNER_BOT")],
                    [InlineKeyboardButton("🔙 Back", callback_data="premium_plans")]
                ])
            )
            await callback_query.answer()
        
        elif data == "get_id":
            await callback_query.answer(f"Your Chat ID: {user_id}", show_alert=True)
        
        elif data == "help":
            help_text = (
                "**❓ Help & Support**\n\n"
                "**Available Commands:**\n"
                "• /start - Start the bot\n"
                "• /drm - Download DRM content\n"
                "• /plan - View your plan\n"
                "• /t2t - Text to TXT converter\n"
                "• /t2h - HTML generator\n"
                "• /topic - Create manual topic\n"
                "• /topics - List all topics\n"
                "• /id - Get chat ID\n\n"
                "**Need more help?** Contact @ITsGOLU_OWNER_BOT"
            )
            await callback_query.message.edit_caption(
                caption=help_text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
                ])
            )
            await callback_query.answer()
        
        # ============= SETTINGS MENU =============
        
        elif data == "settings_menu":
            if not db.is_user_authorized(user_id, client.me.username) and not db.is_admin(user_id):
                await callback_query.answer("⚠️ Premium required for settings!", show_alert=True)
                return
            prefs = db.get_user_preferences(user_id)
            settings_text = (
                f"**⚙️ Premium Settings Panel**\n\n"
                f"Customize your experience & unlock full potential!\n"
                f"- Fonts · Thumbnails · Watermarks\n"
                f"- Topics · Quality · Tokens\n"
                f"- Supercharge your uploads with pro tools\n\n"
                f"**Current Settings:**\n"
                f"🎨 Font Color: `{prefs.get('font_color', 'white')}`\n"
                f"📝 Font Style: `{prefs.get('font_style', 'default')}`\n"
                f"⚡ Video Quality: `{prefs.get('video_quality', '480')}p`\n"
                f"📌 Topic Mode: `{prefs.get('topic_mode', 'none')}`\n"
                f"©️ Credit: `{prefs.get('add_credit', True)}`"
            )
            await callback_query.message.edit_media(
                media=InputMediaPhoto(media=photologo, caption=settings_text),
                reply_markup=await get_settings_keyboard(user_id)
            )
            await callback_query.answer()
        
        elif data == "set_font_color":
            await callback_query.message.edit_caption(
                caption="**🎨 Select Font Color**\n\nChoose your preferred text color:",
                reply_markup=await get_font_color_keyboard()
            )
            await callback_query.answer()
        
        elif data.startswith("font_color_"):
            color = data.replace("font_color_", "")
            db.update_user_preference(user_id, "font_color", color)
            await callback_query.answer(f"✅ Font color set to {color}", show_alert=True)
            await callback_query.message.edit_caption(
                caption="**⚙️ Premium Settings Panel**\n\nSettings updated successfully!",
                reply_markup=await get_settings_keyboard(user_id)
            )
        
        elif data == "set_font_style":
            await callback_query.message.edit_caption(
                caption="**📝 Select Font Style**\n\nChoose your preferred font style:",
                reply_markup=await get_font_style_keyboard()
            )
            await callback_query.answer()
        
        elif data.startswith("font_style_"):
            style = data.replace("font_style_", "")
            db.update_user_preference(user_id, "font_style", style)
            await callback_query.answer(f"✅ Font style set to {style}", show_alert=True)
            await callback_query.message.edit_caption(
                caption="**⚙️ Premium Settings Panel**\n\nSettings updated successfully!",
                reply_markup=await get_settings_keyboard(user_id)
            )
        
        elif data == "set_video_quality":
            await callback_query.message.edit_caption(
                caption="**⚡ Select Video Quality**\n\nChoose default download quality:",
                reply_markup=await get_video_quality_keyboard()
            )
            await callback_query.answer()
        
        elif data.startswith("quality_"):
            quality = data.replace("quality_", "")
            db.update_user_preference(user_id, "video_quality", quality)
            await callback_query.answer(f"✅ Video quality set to {quality}p", show_alert=True)
            await callback_query.message.edit_caption(
                caption="**⚙️ Premium Settings Panel**\n\nSettings updated successfully!",
                reply_markup=await get_settings_keyboard(user_id)
            )
        
        elif data == "toggle_add_credit":
            prefs = db.get_user_preferences(user_id)
            current = prefs.get('add_credit', True)
            db.update_user_preference(user_id, "add_credit", not current)
            await callback_query.answer(f"✅ Add Credit {'Enabled' if not current else 'Disabled'}", show_alert=True)
            await callback_query.message.edit_caption(
                caption="**⚙️ Premium Settings Panel**\n\nSettings updated successfully!",
                reply_markup=await get_settings_keyboard(user_id)
            )
        
        elif data == "toggle_pdf_hyperlinks":
            prefs = db.get_user_preferences(user_id)
            current = prefs.get('pdf_hyperlinks', True)
            db.update_user_preference(user_id, "pdf_hyperlinks", not current)
            await callback_query.answer(f"✅ PDF Hyperlinks {'Enabled' if not current else 'Disabled'}", show_alert=True)
            await callback_query.message.edit_caption(
                caption="**⚙️ Premium Settings Panel**\n\nSettings updated successfully!",
                reply_markup=await get_settings_keyboard(user_id)
            )
        
        elif data == "set_file_name":
            await callback_query.answer("📁 Send the new file name format\nUse {name} as placeholder", show_alert=True)
            await callback_query.message.reply_text(
                "**📁 Set File Name Format**\n\n"
                "Send the format you want to use for file names.\n"
                "Use `{name}` as placeholder for original name.\n\n"
                "Example: `{name} - ITsGOLU`"
            )
            db.update_user_preference(user_id, "awaiting_file_name_format", True)
        
        elif data == "set_video_thumb":
            await callback_query.answer("🖼️ Send a photo to set as video thumbnail", show_alert=True)
            await callback_query.message.reply_text(
                "**🖼️ Set Video Thumbnail**\n\n"
                "Send me a photo to use as default video thumbnail.\n"
                "Or send /d to use default thumbnail.\n"
                "Or send /skip to skip."
            )
            db.update_user_preference(user_id, "awaiting_video_thumb", True)
        
        elif data == "set_pdf_thumb":
            await callback_query.answer("📄 Send a photo to set as PDF thumbnail", show_alert=True)
            await callback_query.message.reply_text(
                "**📄 Set PDF Thumbnail**\n\n"
                "Send me a photo to use as default PDF thumbnail.\n"
                "Or send /d to use default thumbnail.\n"
                "Or send /skip to skip."
            )
            db.update_user_preference(user_id, "awaiting_pdf_thumb", True)
        
        elif data == "set_pdf_watermark":
            await callback_query.answer("💧 Send text for PDF watermark", show_alert=True)
            await callback_query.message.reply_text(
                "**💧 Set PDF Watermark**\n\n"
                "Send the text you want to use as PDF watermark.\n"
                "Or send /d to disable."
            )
            db.update_user_preference(user_id, "awaiting_pdf_watermark", True)
        
        elif data == "set_video_watermark":
            await callback_query.answer("🎬 Send text for video watermark", show_alert=True)
            await callback_query.message.reply_text(
                "**🎬 Set Video Watermark**\n\n"
                "Send the text you want to use as video watermark.\n"
                "Or send /d to disable."
            )
            db.update_user_preference(user_id, "awaiting_video_watermark", True)
        
        elif data == "set_token":
            await callback_query.answer("🔑 Send your PW token", show_alert=True)
            await callback_query.message.reply_text(
                "**🔑 Set Token**\n\n"
                "Send your PW token for accessing DRM content.\n"
                "Or send /d to use default."
            )
            db.update_user_preference(user_id, "awaiting_token", True)
        
        elif data == "set_default_channel":
            await callback_query.answer("📢 Send the channel ID where you want to upload", show_alert=True)
            await callback_query.message.reply_text(
                "**📢 Set Default Channel**\n\n"
                "Send the channel ID where you want to upload files by default.\n\n"
                "Example: `-100123456789`\n"
                "Or send /d to clear."
            )
            db.update_user_preference(user_id, "awaiting_default_channel", True)
        
        # ============= TOPIC MANAGEMENT =============
        
        elif data == "set_topic_mode":
            await callback_query.message.edit_caption(
                caption="**📌 Select Topic/Thread Mode**\n\n"
                       "Choose how you want to organize your uploads:\n\n"
                       "❌ **No Topic** - Upload without topics\n"
                       "🤖 **Auto Create** - Automatically create topics per batch\n"
                       "📝 **Manual** - Use /topic command to create\n"
                       "📦 **Per Batch** - One topic for entire batch\n"
                       "🎬 **Per Video** - Separate topic for each video",
                reply_markup=await get_topic_mode_keyboard()
            )
            await callback_query.answer()
        
        elif data.startswith("topic_mode_"):
            mode = data.replace("topic_mode_", "")
            db.set_topic_mode(user_id, mode)
            await callback_query.answer(f"✅ Topic mode set to: {mode}", show_alert=True)
            await callback_query.message.edit_caption(
                caption="**⚙️ Premium Settings Panel**\n\nTopic settings updated successfully!",
                reply_markup=await get_settings_keyboard(user_id)
            )
        
        elif data == "topics_menu":
            prefs = db.get_user_preferences(user_id)
            default_channel = prefs.get('default_channel')
            topic_mode = prefs.get('topic_mode', 'none')
            
            text = f"**📂 Topics Management**\n\n"
            text += f"Current Topic Mode: `{topic_mode}`\n"
            text += f"Default Channel: `{default_channel if default_channel else 'Not Set'}`\n\n"
            text += "Manage your channel topics and threads here."
            
            await callback_query.message.edit_media(
                media=InputMediaPhoto(media=photologo, caption=text),
                reply_markup=await get_topics_menu_keyboard(user_id, default_channel)
            )
            await callback_query.answer()
        
        elif data == "create_topic":
            await callback_query.answer("📌 Send the name for new topic", show_alert=True)
            await callback_query.message.reply_text(
                "**📌 Create New Topic**\n\n"
                "Send the name for the new topic/thread.\n\n"
                "Example: `Batch 1 - Geography`"
            )
            db.update_user_preference(user_id, "awaiting_topic_name", True)
        
        elif data == "list_topics":
            prefs = db.get_user_preferences(user_id)
            channel_id = prefs.get('default_channel')
            
            if not channel_id:
                await callback_query.answer("⚠️ No default channel set!", show_alert=True)
                return
            
            topics = db.get_all_channel_topics(int(channel_id))
            
            if not topics:
                text = f"**📋 Topics in Channel**\n\nNo topics found in channel `{channel_id}`.\n\nCreate one using the 'Create New Topic' button."
            else:
                text = f"**📋 Topics in Channel `{channel_id}`**\n\n"
                for i, topic in enumerate(topics, 1):
                    text += f"{i}. 📌 {topic.get('topic_name')}\n"
                    text += f"   ID: `{topic.get('topic_id')}`\n\n"
            
            await callback_query.message.edit_caption(
                caption=text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Create New", callback_data="create_topic")],
                    [InlineKeyboardButton("🔙 Back", callback_data="topics_menu")]
                ])
            )
            await callback_query.answer()
        
        elif data == "delete_topic":
            await callback_query.answer("🗑️ Send the topic name to delete", show_alert=True)
            await callback_query.message.reply_text(
                "**🗑️ Delete Topic**\n\n"
                "Send the name of the topic you want to delete.\n\n"
                "Example: `Batch 1 - Geography`"
            )
            db.update_user_preference(user_id, "awaiting_topic_delete", True)
        
        elif data == "upload_to_topic":
            await callback_query.answer("📤 Send the topic name to upload to", show_alert=True)
            await callback_query.message.reply_text(
                "**📤 Upload to Topic**\n\n"
                "Send the name of the topic you want to upload to.\n\n"
                "Your next upload will be sent to this topic."
            )
            db.update_user_preference(user_id, "awaiting_topic_upload", True)
        
        # ============= TOOLS MENU =============
        
        elif data == "tools_menu":
            await callback_query.message.edit_media(
                media=InputMediaPhoto(media=photologo, 
                    caption="**🛠️ Premium Command Panel**\n\nSmart tools to manage & process your uploads\nConvert · Edit · Split · Clean · Extract with ease"),
                reply_markup=await get_tools_keyboard()
            )
            await callback_query.answer()
        
        elif data == "tool_text_to_txt":
            await callback_query.answer("📝 Use /t2t command", show_alert=True)
        
        elif data == "tool_edit_txt":
            await callback_query.answer("✏️ Edit .txt feature coming soon", show_alert=True)
        
        elif data == "tool_split_txt":
            await callback_query.answer("✂️ Split .txt feature coming soon", show_alert=True)
        
        elif data == "tool_replace_word":
            await callback_query.answer("🔄 Replace Word feature coming soon", show_alert=True)
        
        elif data == "tool_html_formatter":
            await callback_query.answer("🌐 Use /t2h command", show_alert=True)
        
        elif data == "tool_keyword_filter":
            await callback_query.answer("🔍 Keyword Filter feature coming soon", show_alert=True)
        
        elif data == "tool_title_clean":
            await callback_query.answer("🧹 Title Clean feature coming soon", show_alert=True)
        
        elif data == "tool_pw_converter":
            await callback_query.answer("📜 PW Converter feature coming soon", show_alert=True)
        
        elif data == "tool_youtube_extract":
            await callback_query.answer("▶️ YouTube Extract feature coming soon", show_alert=True)
        
        # ============= DRM MENU =============
        
        elif data == "drm_menu":
            await callback_query.message.edit_media(
                media=InputMediaPhoto(media=photologo, 
                    caption="**📥 DRM Download Menu**\n\nChoose download type:"),
                reply_markup=await get_drm_keyboard()
            )
            await callback_query.answer()
        
        elif data == "drm_single":
            await callback_query.answer("🎬 Send me a direct video link", show_alert=True)
            await callback_query.message.reply_text(
                "**🎬 Single Video Download**\n\n"
                "Send me the direct link to the video you want to download.\n\n"
                "Supported platforms:\n"
                "• YouTube\n"
                "• Classplus\n"
                "• PW Live\n"
                "• Testbook\n"
                "• And more..."
            )
        
        elif data == "drm_batch":
            await callback_query.answer("📋 Use /drm command with text file", show_alert=True)
        
        elif data == "drm_pdf":
            await callback_query.answer("📑 Send me the PDF link", show_alert=True)
        
        elif data == "drm_image":
            await callback_query.answer("🖼️ Send me the image link", show_alert=True)
        
        elif data == "drm_audio":
            await callback_query.answer("🎵 Send me the audio link", show_alert=True)
        
        # ============= MY PLAN =============
        
        elif data == "my_plan":
            expiry_info = db.get_user_expiry_info(user_id, client.me.username)
            if expiry_info and expiry_info['is_active']:
                text = (
                    f"**📱 Your Premium Plan**\n\n"
                    f"👤 Name: {expiry_info['name']}\n"
                    f"🆔 ID: `{expiry_info['user_id']}`\n"
                    f"📅 Expires: {expiry_info['expiry_date']}\n"
                    f"⏳ Days Left: {expiry_info['days_left']}\n"
                    f"✅ Status: Active"
                )
            else:
                text = "**❌ No Active Plan**\n\nYou don't have an active subscription. Please purchase a premium plan to use the bot."
            
            await callback_query.message.edit_caption(
                caption=text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💎 Buy Premium", callback_data="premium_plans")],
                    [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
                ])
            )
            await callback_query.answer()
        
        # ============= STATS =============
        
        elif data == "stats" or data == "admin_stats":
            if not db.is_admin(user_id):
                await callback_query.answer("⛔ Access Denied!", show_alert=True)
                return
            
            users = db.list_users(client.me.username)
            active_users = 0
            for user in users:
                expiry = user.get('expiry_date')
                if expiry:
                    if isinstance(expiry, str):
                        try:
                            expiry = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")
                        except:
                            expiry = None
                    if expiry and expiry > datetime.now():
                        active_users += 1
            
            prefs_count = db.user_preferences.count_documents({})
            topics_count = db.topics.count_documents({})
            
            stats_text = (
                f"**📊 Bot Statistics**\n\n"
                f"👥 Total Users: {len(users)}\n"
                f"✅ Active Users: {active_users}\n"
                f"❌ Expired Users: {len(users) - active_users}\n"
                f"⚙️ User Preferences: {prefs_count}\n"
                f"📂 Total Topics: {topics_count}\n"
                f"👑 Admins: {len(ADMINS) + 1}\n"
                f"🤖 Bot: @{client.me.username}\n"
                f"🕐 Time: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
            )
            
            await callback_query.message.edit_caption(
                caption=stats_text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Refresh", callback_data="stats"),
                     InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]
                ])
            )
            await callback_query.answer()
        
        # ============= ADMIN PANEL =============
        
        elif data == "admin_menu":
            if not db.is_admin(user_id):
                await callback_query.answer("⛔ Access Denied! Admin only.", show_alert=True)
                return
            
            await callback_query.message.edit_media(
                media=InputMediaPhoto(media=photologo, 
                    caption="**👑 Admin Control Panel**\n\nManage users, view statistics, and configure the bot."),
                reply_markup=await get_admin_keyboard()
            )
            await callback_query.answer()
        
        elif data == "admin_add_user":
            if not db.is_admin(user_id):
                await callback_query.answer("⛔ Access Denied!", show_alert=True)
                return
            
            await callback_query.answer("➕ Use /add user_id days", show_alert=True)
        
        elif data == "admin_remove_user":
            if not db.is_admin(user_id):
                await callback_query.answer("⛔ Access Denied!", show_alert=True)
                return
            
            await callback_query.answer("➖ Use /remove user_id", show_alert=True)
        
        elif data == "admin_list_users":
            if not db.is_admin(user_id):
                await callback_query.answer("⛔ Access Denied!", show_alert=True)
                return
            
            await callback_query.answer("📋 Use /users command", show_alert=True)
        
        elif data == "admin_broadcast":
            if not db.is_admin(user_id):
                await callback_query.answer("⛔ Access Denied!", show_alert=True)
                return
            
            await callback_query.answer("📢 Broadcast feature coming soon", show_alert=True)
        
        elif data == "admin_clean":
            if not db.is_admin(user_id):
                await callback_query.answer("⛔ Access Denied!", show_alert=True)
                return
            
            await callback_query.message.edit_caption(
                caption="**🧹 Cleanup Utility**\n\nWhat would you like to clean?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📁 Downloads Folder", callback_data="clean_downloads")],
                    [InlineKeyboardButton("🎬 Media Files", callback_data="clean_media")],
                    [InlineKeyboardButton("👥 Expired Users", callback_data="clean_expired")],
                    [InlineKeyboardButton("🗑️ All", callback_data="clean_all")],
                    [InlineKeyboardButton("🔙 Back", callback_data="admin_menu")]
                ])
            )
            await callback_query.answer()
        
        elif data == "admin_logs":
            if not db.is_admin(user_id):
                await callback_query.answer("⛔ Access Denied!", show_alert=True)
                return
            
            try:
                with open("logs.txt", "rb") as f:
                    await callback_query.message.reply_document(f, caption="📜 Bot Logs")
                await callback_query.answer("✅ Logs sent!", show_alert=False)
            except:
                await callback_query.answer("❌ No logs found!", show_alert=True)
        
        elif data == "admin_config":
            if not db.is_admin(user_id):
                await callback_query.answer("⛔ Access Denied!", show_alert=True)
                return
            
            await callback_query.answer("⚙️ System Config coming soon", show_alert=True)
        
        # ============= CLEAN COMMANDS =============
        
        elif data.startswith("clean_"):
            if not db.is_admin(user_id):
                await callback_query.answer("⛔ Access Denied!", show_alert=True)
                return
            
            clean_type = data.replace("clean_", "")
            await callback_query.answer(f"🧹 Cleaning {clean_type}...", show_alert=False)
            await callback_query.message.reply_text(f"🔄 Cleanup started for: {clean_type}")
        
        # ============= DEFAULT =============
        
        else:
            await callback_query.answer(f"⚠️ Feature under development", show_alert=True)
    
    return bot

import os
from os import environ

# API Configuration
API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

CREDIT = os.environ.get("CREDIT", "𝐈𝐓'𝐬𝐆𝐎𝐋𝐔")

# MongoDB Configuration
DATABASE_NAME = os.environ.get("DATABASE_NAME", "CpprivateApi")
DATABASE_URL = os.environ.get("DATABASE_URL", "mongodb+srv://itsgoluAPI:jrMHSipToKUEnmcp@cpprivateapi.ghhp3oz.mongodb.net/?appName=CpprivateApi")
MONGO_URL = DATABASE_URL

# Owner and Admin Configuration
OWNER_ID = int(os.environ.get("OWNER_ID", ""))
ADMINS = [int(x) for x in os.environ.get("ADMINS", "").split()]

# Channel Configuration
PREMIUM_CHANNEL = ""

# Thumbnail Configuration
THUMBNAILS = list(map(str, os.environ.get("THUMBNAILS", "").split()))

# Web Server Configuration
WEB_SERVER = os.environ.get("WEB_SERVER", "False").lower() == "true"
WEBHOOK = True
PORT = int(os.environ.get("PORT", 8000))

# Message Formats
AUTH_MESSAGES = {
    "subscription_active": """<b>🎉 Subscription Activated!</b>

<blockquote>Your subscription has been activated and will expire on {expiry_date}.
You can now use the bot!</blockquote>\n\n Type /start to start uploading """,

    "subscription_expired": """<b>⚠️ Your Subscription Has Ended</b>

<blockquote>Your access to the bot has been revoked as your subscription period has expired.
Please contact the admin to renew your subscription.</blockquote>""",

    "user_added": """<b>✅ User Added Successfully!</b>

<blockquote>👤 Name: {name}
🆔 User ID: {user_id}
📅 Expiry: {expiry_date}</blockquote>""",

    "user_removed": """<b>✅ User Removed Successfully!</b>

<blockquote>User ID {user_id} has been removed from authorized users.</blockquote>""",

    "access_denied": """<b>⚠️ Access Denied!</b>

<blockquote>You are not authorized to use this bot.
Please contact the admin to get access.</blockquote>""",

    "not_admin": "⚠️ You are not authorized to use this command!",
    
    "invalid_format": """❌ <b>Invalid Format!</b>

<blockquote>Use format: {format}</blockquote>"""
}

# ============= NEW ADDITIONS - PRESERVING ALL ABOVE =============
# Premium Plans Configuration
PLAN_PRICES = {
    "7": 400,
    "15": 600,
    "30": 1000
}

# Font Styles Configuration
FONT_STYLES = {
    "default": "Default",
    "bold": "Bold",
    "italic": "Italic",
    "monospace": "Monospace"
}

# Font Colors Configuration
FONT_COLORS = {
    "white": "#FFFFFF",
    "blue": "#007bff",
    "green": "#28a745",
    "red": "#dc3545",
    "yellow": "#ffc107",
    "purple": "#6f42c1"
}

# Topic/Thread Configuration
TOPIC_MODES = {
    "auto": "Auto Create Topic",
    "manual": "Manual Command (/topic)",
    "none": "No Topic",
    "per_batch": "Topic Per Batch",
    "per_video": "Topic Per Video"
}

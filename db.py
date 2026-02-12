import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Union
from pymongo import MongoClient, errors
from pymongo.database import Database as MongoDatabase
from pymongo.collection import Collection
from vars import *
import colorama
from colorama import Fore, Style
import time
import certifi
from typing_extensions import Literal

colorama.init()

class Database:
    def __init__(self, max_retries: int = 3, retry_delay: float = 2.0):
        self._print_startup_message()
        self.client: Optional[MongoClient] = None
        self.db: Optional[MongoDatabase] = None
        self.users: Optional[Collection] = None
        self.settings: Optional[Collection] = None
        # ============= NEW ADDITION =============
        self.user_preferences: Optional[Collection] = None
        self.bot_settings: Optional[Collection] = None
        self.topics: Optional[Collection] = None
        # ========================================
        
        self._connect_with_retry(max_retries, retry_delay)
        
    def _connect_with_retry(self, max_retries: int, retry_delay: float):
        for attempt in range(1, max_retries + 1):
            try:
                print(f"{Fore.YELLOW}⌛ Attempt {attempt}/{max_retries}: Connecting to MongoDB...{Style.RESET_ALL}")
                
                self.client = MongoClient(
                    MONGO_URL,
                    serverSelectionTimeoutMS=20000,
                    connectTimeoutMS=20000,
                    socketTimeoutMS=30000,
                    tlsCAFile=certifi.where(),
                    retryWrites=True,
                    retryReads=True
                )
                
                self.client.server_info()
                
                self.db = self.client.get_database('ITsGOLU_db')
                self.users = self.db['users']
                self.settings = self.db['user_settings']
                # ============= NEW ADDITION =============
                self.user_preferences = self.db['user_preferences']
                self.bot_settings = self.db['bot_settings']
                self.topics = self.db['channel_topics']
                # ========================================
                
                print(f"{Fore.GREEN}✓ MongoDB Connected Successfully!{Style.RESET_ALL}")
                self._initialize_database()
                return
                
            except errors.ServerSelectionTimeoutError as e:
                print(f"{Fore.RED}✕ Connection attempt {attempt} failed: {str(e)}{Style.RESET_ALL}")
                if attempt < max_retries:
                    time.sleep(retry_delay)
                else:
                    raise ConnectionError(f"Failed to connect to MongoDB after {max_retries} attempts") from e
            except Exception as e:
                print(f"{Fore.RED}✕ Unexpected error during connection: {str(e)}{Style.RESET_ALL}")
                raise

    def _print_startup_message(self):
        print(f"\n{Fore.CYAN}{'='*50}")
        print(f"{Fore.CYAN}🚀 ITsGOLU_UPLOADER Bot - Database Initialization")
        print(f"{'='*50}{Style.RESET_ALL}\n")

    def _initialize_database(self):
        print(f"{Fore.YELLOW}⌛ Setting up database...{Style.RESET_ALL}")
        
        try:
            self._create_indexes()
            print(f"{Fore.GREEN}✓ Database indexes created!{Style.RESET_ALL}")
            
            self._migrate_existing_users()
            
            print(f"{Fore.GREEN}✓ Database initialization complete!{Style.RESET_ALL}\n")
        except Exception as e:
            print(f"{Fore.RED}⚠ Database initialization error: {str(e)}{Style.RESET_ALL}")
            raise

    def _create_indexes(self):
        index_results = []
        
        try:
            self.users.create_index(
                [("bot_username", 1), ("user_id", 1)], 
                unique=True,
                name="user_identity"
            )
            index_results.append("users compound index")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Could not create users compound index: {str(e)}{Style.RESET_ALL}")

        try:
            self.settings.create_index(
                [("user_id", 1)],
                unique=True,
                name="user_settings"
            )
            index_results.append("settings index")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Could not create settings index: {str(e)}{Style.RESET_ALL}")

        # ============= NEW ADDITIONS =============
        try:
            self.user_preferences.create_index(
                [("user_id", 1)],
                unique=True,
                name="user_preferences"
            )
            index_results.append("preferences index")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Could not create preferences index: {str(e)}{Style.RESET_ALL}")
            
        try:
            self.topics.create_index(
                [("channel_id", 1), ("topic_name", 1)],
                unique=True,
                name="channel_topics"
            )
            index_results.append("topics index")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Could not create topics index: {str(e)}{Style.RESET_ALL}")
        # ========================================

        try:
            self.users.create_index(
                "expiry_date",
                name="user_expiry",
                expireAfterSeconds=0
            )
            index_results.append("expiry TTL index")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠ Could not create expiry index: {str(e)}{Style.RESET_ALL}")
            
        return index_results

    def _migrate_existing_users(self):
        try:
            update_result = self.users.update_many(
                {"bot_username": {"$exists": False}},
                {"$set": {"bot_username": "ITsGOLU_UPLOADER"}}
            )
            
            if update_result.modified_count > 0:
                print(f"{Fore.YELLOW}⚠ Migrated {update_result.modified_count} users to new schema{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}⚠ Could not migrate users: {str(e)}{Style.RESET_ALL}")

    def get_user(self, user_id: int, bot_username: str = "ITsGOLU_UPLOADER") -> Optional[dict]:
        try:
            return self.users.find_one({
                "user_id": user_id,
                "bot_username": bot_username
            })
        except Exception as e:
            print(f"{Fore.RED}Error getting user {user_id}: {str(e)}{Style.RESET_ALL}")
            return None

    def is_user_authorized(self, user_id: int, bot_username: str = "ITsGOLU_UPLOADER") -> bool:
        try:
            if user_id == OWNER_ID or user_id in ADMINS:
                return True
                
            user = self.get_user(user_id, bot_username)
            if not user:
                return False
                
            expiry = user.get('expiry_date')
            if not expiry:
                return False
                
            if isinstance(expiry, str):
                expiry = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")
                
            return expiry > datetime.now()
            
        except Exception as e:
            print(f"{Fore.RED}Authorization error for {user_id}: {str(e)}{Style.RESET_ALL}")
            return False

    def add_user(self, user_id: int, name: str, days: int, 
                bot_username: str = "ITsGOLU_UPLOADER") -> tuple[bool, Optional[datetime]]:
        try:
            expiry_date = datetime.now() + timedelta(days=days)
            update_result = self.users.update_one(
                {"user_id": user_id, "bot_username": bot_username},
                {"$set": {
                    "name": name,
                    "expiry_date": expiry_date,
                    "added_date": datetime.now(),
                    "last_updated": datetime.now()
                }},
                upsert=True
            )
            
            if update_result.upserted_id or update_result.modified_count > 0:
                return True, expiry_date
            return False, None
            
        except Exception as e:
            print(f"{Fore.RED}Add user error for {user_id}: {str(e)}{Style.RESET_ALL}")
            return False, None

    def remove_user(self, user_id: int, bot_username: str = "ITsGOLU_UPLOADER") -> bool:
        try:
            result = self.users.delete_one({
                "user_id": user_id,
                "bot_username": bot_username
            })
            return result.deleted_count > 0
        except Exception as e:
            print(f"{Fore.RED}Remove user error for {user_id}: {str(e)}{Style.RESET_ALL}")
            return False

    def list_users(self, bot_username: str = "ITsGOLU_UPLOADER") -> List[dict]:
        try:
            return list(self.users.find(
                {"bot_username": bot_username},
                {"_id": 0, "name": 1, "user_id": 1, "expiry_date": 1}
            ))
        except Exception as e:
            print(f"{Fore.RED}List users error: {str(e)}{Style.RESET_ALL}")
            return []

    def is_admin(self, user_id: int) -> bool:
        try:
            is_admin = user_id == OWNER_ID or user_id in ADMINS
            if is_admin:
                print(f"{Fore.GREEN}✓ Admin/Owner {user_id} verified{Style.RESET_ALL}")
            return is_admin
        except Exception as e:
            print(f"{Fore.RED}Admin check error: {str(e)}{Style.RESET_ALL}")
            return False
            
    def get_log_channel(self, bot_username: str):
        try:
            settings = self.bot_settings.find_one({"bot_username": bot_username})
            if settings and 'log_channel' in settings:
                return settings['log_channel']
            return None
        except Exception as e:
            print(f"Error getting log channel: {str(e)}")
            return None

    def set_log_channel(self, bot_username: str, channel_id: int):
        try:
            self.bot_settings.update_one(
                {"bot_username": bot_username},
                {"$set": {"log_channel": channel_id}},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error setting log channel: {str(e)}")
            return False
            
    def list_bot_usernames(self) -> List[str]:
        try:
            usernames = self.users.distinct("bot_username")
            return usernames if usernames else ["ITsGOLU_UPLOADER"]
        except Exception as e:
            print(f"{Fore.RED}List bot usernames error: {str(e)}{Style.RESET_ALL}")
            return ["ITsGOLU_UPLOADER"]

    async def cleanup_expired_users(self, bot) -> int:
        try:
            current_time = datetime.now()
            expired_users = self.users.find({
                "expiry_date": {"$lt": current_time},
                "user_id": {"$nin": [OWNER_ID] + ADMINS}
            })

            removed_count = 0
            for user in expired_users:
                try:
                    await bot.send_message(
                        user["user_id"],
                        f"**⚠️ Your subscription has expired!**\n\n"
                        f"• Name: {user['name']}\n"
                        f"• Expired on: {user['expiry_date'].strftime('%d-%m-%Y')}\n\n"
                        f"Contact admin to renew your subscription."
                    )
                    
                    self.users.delete_one({"_id": user["_id"]})
                    removed_count += 1

                    log_msg = (
                        f"**🚫 Removed Expired User**\n\n"
                        f"• Name: {user['name']}\n"
                        f"• ID: {user['user_id']}\n"
                        f"• Expired on: {user['expiry_date'].strftime('%d-%m-%Y')}"
                    )
                    for admin in ADMINS + [OWNER_ID]:
                        try:
                            await bot.send_message(admin, log_msg)
                        except:
                            continue

                except Exception as e:
                    print(f"{Fore.YELLOW}Error processing user {user['user_id']}: {str(e)}{Style.RESET_ALL}")
                    continue

            return removed_count

        except Exception as e:
            print(f"{Fore.RED}Cleanup error: {str(e)}{Style.RESET_ALL}")
            return 0

    def get_user_expiry_info(self, user_id: int, bot_username: str = "ITsGOLU_UPLOADER") -> Optional[dict]:
        try:
            user = self.get_user(user_id, bot_username)
            if not user:
                return None

            expiry = user.get('expiry_date')
            if not expiry:
                return None

            if isinstance(expiry, str):
                expiry = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")

            days_left = (expiry - datetime.now()).days

            return {
                "name": user.get('name', 'Unknown'),
                "user_id": user_id,
                "expiry_date": expiry.strftime("%d-%m-%Y"),
                "days_left": days_left,
                "added_date": user.get('added_date', 'Unknown'),
                "is_active": days_left > 0
            }

        except Exception as e:
            print(f"{Fore.RED}Get expiry info error for {user_id}: {str(e)}{Style.RESET_ALL}")
            return None

    # ============= NEW METHODS - ADDED WITHOUT REMOVING ANYTHING =============
    
    def get_user_preferences(self, user_id: int) -> dict:
        """Get user preferences with defaults"""
        try:
            prefs = self.user_preferences.find_one({"user_id": user_id})
            if not prefs:
                default_prefs = {
                    "user_id": user_id,
                    "font_color": "white",
                    "font_style": "default",
                    "file_name_format": "{name}",
                    "video_thumb": "/d",
                    "pdf_thumb": "/d",
                    "auto_topic": False,
                    "topic_mode": "none",
                    "add_credit": True,
                    "pdf_watermark": "/d",
                    "video_watermark": "/d",
                    "video_quality": "480",
                    "pdf_hyperlinks": True,
                    "token": "/d",
                    "default_channel": None
                }
                self.user_preferences.insert_one(default_prefs)
                return default_prefs
            return prefs
        except Exception as e:
            print(f"{Fore.RED}Get user preferences error: {str(e)}{Style.RESET_ALL}")
            return {}

    def update_user_preference(self, user_id: int, key: str, value):
        """Update specific user preference"""
        try:
            self.user_preferences.update_one(
                {"user_id": user_id},
                {"$set": {key: value}},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"{Fore.RED}Update user preference error: {str(e)}{Style.RESET_ALL}")
            return False

    def get_topic_mode(self, user_id: int) -> str:
        """Get user's topic/thread mode"""
        prefs = self.get_user_preferences(user_id)
        return prefs.get('topic_mode', 'none')

    def set_topic_mode(self, user_id: int, mode: str):
        """Set user's topic/thread mode"""
        return self.update_user_preference(user_id, "topic_mode", mode)

    def create_channel_topic(self, channel_id: int, topic_name: str, topic_id: int = None):
        """Store channel topic/thread information"""
        try:
            topic_data = {
                "channel_id": channel_id,
                "topic_name": topic_name,
                "topic_id": topic_id,
                "created_at": datetime.now()
            }
            self.topics.update_one(
                {"channel_id": channel_id, "topic_name": topic_name},
                {"$set": topic_data},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"{Fore.RED}Create channel topic error: {str(e)}{Style.RESET_ALL}")
            return False

    def get_channel_topic(self, channel_id: int, topic_name: str):
        """Get channel topic/thread information"""
        try:
            return self.topics.find_one({
                "channel_id": channel_id,
                "topic_name": topic_name
            })
        except Exception as e:
            print(f"{Fore.RED}Get channel topic error: {str(e)}{Style.RESET_ALL}")
            return None

    def get_all_channel_topics(self, channel_id: int) -> List[dict]:
        """Get all topics for a channel"""
        try:
            return list(self.topics.find(
                {"channel_id": channel_id},
                {"_id": 0}
            ))
        except Exception as e:
            print(f"{Fore.RED}Get all channel topics error: {str(e)}{Style.RESET_ALL}")
            return []

    def delete_channel_topic(self, channel_id: int, topic_name: str):
        """Delete a channel topic"""
        try:
            result = self.topics.delete_one({
                "channel_id": channel_id,
                "topic_name": topic_name
            })
            return result.deleted_count > 0
        except Exception as e:
            print(f"{Fore.RED}Delete channel topic error: {str(e)}{Style.RESET_ALL}")
            return False

    # ============= END NEW METHODS =============

    def close(self):
        if self.client:
            self.client.close()
            print(f"{Fore.YELLOW}✓ MongoDB connection closed{Style.RESET_ALL}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

print(f"\n{Fore.CYAN}{'='*50}")
print(f"🤖 Initializing ITsGOLU_UPLOADER Bot Database")
print(f"{'='*50}{Style.RESET_ALL}\n")

try:
    db = Database(max_retries=3, retry_delay=2)
except Exception as e:
    print(f"{Fore.RED}✕ Fatal Error: DB initialization failed!{Style.RESET_ALL}")
    raise

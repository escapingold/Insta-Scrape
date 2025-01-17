import logging
import json
import base64
import instaloader,os,time
from secrets import token_hex
from uuid import uuid4 
from binascii import hexlify
import requests
from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup,Bot
from telegram.ext import Application, CommandHandler, ContextTypes,CallbackContext
from telegram.error import BadRequest,TelegramError
from telegram.constants import ParseMode
import re,asyncio
from random import randint
import pyfiglet
from termcolor import colored
from config import *
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
"""
    "1. /start - Start the bot \n"
    "2. /id :get chat id. 🌍\n"
    "3. /insta <username> - Get detailed Instagram profile information. 📱\n"
    "4. /info - Get detailed information about your user profile. 📸\n"
    "5. /feedback :Send Your feed back to admin🌍\n"

"""
CHANNEL_LINK = CHANNEL_LINK
IMAGE_URL = IMAGE_URL
ADMIN_ID=ADMIN_ID
NOTIFY_CHANNEL = NOTIFY_CHANNEL
telegram_username=telegram_username
owner=f"https://t.me/{telegram_username}"

USER_IDS_FILE = "user_ids.json"

def load_user_ids():
    try:
        with open(USER_IDS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
def save_user_id(user_id):
    try:
        try:
            with open(USER_IDS_FILE, "r") as f:
                user_ids = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            user_ids = []

        if user_id not in user_ids:
            user_ids.append(user_id)
            with open(USER_IDS_FILE, "w") as f:
                json.dump(user_ids, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving user ID: {e}")

async def send_channel_notification(bot: Bot, user_id: int, username: str) -> None:
    message = (
        f"<b>📢 New user started the {BOT_USERNAME} !</b>\n\n"
        f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
        f"👤 <b>Username:</b> @{username}\n\n"
    )
    
    notify_channels =NOTIFY_CHANNEL
    
    try:
        print(f"New user joined {BOT_USERNAME}: {user_id}")
        for channel in notify_channels:
            await bot.send_message(channel, message, parse_mode="HTML")
            print(f"Notification sent to {channel}")
    except Exception as e:
        logger.error(f"Error sending notification to channels: {e}")



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome image and message when /start is used"""
    user = update.effective_user
    username = user.username or "Unknown"
    user_id = user.id

    save_user_id(user_id)

    bot = context.bot
    await send_channel_notification(bot, user_id, username)

    welcome_message = (f"<b>Welcome to {BOT_USERNAME}!</b>\n\n"
                       f"Use <b>/insta - </b> to get the insta id🌍.\n\n"
                       f"Use <b>/help - </b> to know about BOT.\n"
                       f"Here are your details:\n\n"
                       f"👤 <b>Username:</b> <b>@{username}</b>\n"
                       f"🔑 <b>User ID:</b> <code>{user_id}</code>\n\n"
                       f"✨ Let's start exploring IP addresses! 🌐")

    keyboard = [
        [InlineKeyboardButton("Join our Channel 📢", url=CHANNEL_LINK)],  # Separate button for channel
        [
            InlineKeyboardButton("Owner🔑", url=owner),
            xd
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(photo=IMAGE_URL, caption=welcome_message, parse_mode="html", reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Provides information about available commands"""
    help_message = (
        f"*📢Welcome to the {BOT_USERNAME} !*\n\n"
        "*Here are the available commands:*\n\n"
        "1. /start - Start the bot \n"
        "2. /id :get chat id. 🌍\n"
        "3. /insta <username> - Get detailed Instagram profile information. 📱\n"
        "4. /info - Get detailed information about your user profile. 📸\n"
        "5. /feedback :Send Your feed back to admin🌍\n"
        "*If you have any questions, feel free to reach out! 😊*\n\n"

    )

    keyboard = [
        [InlineKeyboardButton("Join our Channel 📢", url=CHANNEL_LINK)],
        [InlineKeyboardButton("Developer🔑", url=owner),xd]
        
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_photo(
        photo="https://drive.google.com/uc?export=view&id=13cDsTYQftsdp_ZHyOBWA_hsyk63TtFRl", 
        caption=help_message,  
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="MarkDown"
    )
encoded_url = "aHR0cHM6Ly90Lm1lL3B5X2h1YnM="
async def feedback_command(update: Update, context: CallbackContext):
    # Get the feedback message sent by the user after the /feedback command
    feedback_message = ' '.join(context.args)  # All text after /feedback is the message

    # If no feedback message is provided
    if not feedback_message:
        await update.message.reply_text("❗ Please provide your feedback after the /feedback command. Example: /feedback Your message here.")
        return

    # Get user details
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "No username"  # If no username, show 'No username'
    
    # Create the feedback message format with emojis
    formatted_feedback = (
        f"💬 <b>Feedback Received for {BOT_USERNAME} from User:</b> 💬\n\n"
        f"👤 <b>Username:</b> @{username}\n"
        f"🆔 <b>User ID:</b> {user_id}\n"
        f"📝 <b>Feedback:</b> {feedback_message}\n\n"
    )

    # Define your list of notify channels
    notify_channels = NOTIFY_CHANNEL

    try:
        # Loop through the list of channels and send the feedback to each
        for channel in notify_channels:
            await context.bot.send_message(channel, formatted_feedback, parse_mode="HTML")
        
        # Send a confirmation reply to the user
        await update.message.reply_text("✅ Thank you for your feedback! It has been sent to the admin. 📨")
    
    except Exception as e:
        # Handle any errors that occur
        await update.message.reply_text("⚠️ Sorry, there was an error sending your feedback. Please try again later. 😔")
        print(f"Error sending feedback: {e}")
url_hash = "2c6ee24b09816a6f14f95d1698b24cfc4c40168b84f24071e7d4baf53957719b" 
async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Allows the admin to send a broadcast message to all users."""
    if update.effective_user.id not in ADMIN_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    args = context.args
    if len(args) < 1:
        await update.message.reply_text("Usage: /broad <message>\nPlease provide a message to broadcast.")
        return

    message = ' '.join(args)

    # Formatting the broadcast message from the admin
    formatted_message = f"📢 <b>Broadcast from Admin:</b>\n\n{message}"

    if os.path.exists(USER_IDS_FILE):
        with open(USER_IDS_FILE, 'r') as file:
            user_ids = json.load(file)
    else:
        user_ids = []

    successful = 0
    failed = 0
    skipped = 0
    failed_user_ids = []

    for user_id in user_ids:
        try:
            await context.bot.send_message(chat_id=user_id, text=formatted_message,parse_mode="HTML")
            successful += 1
        except BadRequest as e:
            if 'blocked' in str(e).lower():
                skipped += 1
                failed_user_ids.append(user_id)
            else:
                failed += 1
            print(f"Error sending message to user {user_id}: {e}")
        except TelegramError as e:
            failed += 1
            print(f"Error sending message to user {user_id}: {e}")
        except Exception as e:
            failed += 1
            print(f"Unexpected error with user {user_id}: {e}")

    summary_message = (
        f"📢 **Broadcast completed!**\n\n"
        f"👥 **Total users:** {len(user_ids)}\n"
        f"✅ **Message sent successfully to:** {successful} users\n"
        f"❌ **Failed to send to:** {failed} users\n"
        f"⛔ **Skipped (blocked users):** {skipped} users\n\n"
        f"⚠️ **Failed user IDs (Blocked/Invalid):** {', '.join(map(str, failed_user_ids)) if failed_user_ids else 'None'}"
    )

    await update.message.reply_text(summary_message, parse_mode="MARKDOWN")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fetches and displays user info with their profile picture (if available)"""
    user = update.effective_user
    user_id = user.id
    username = user.username or "Unknown"
    first_name = user.first_name or "No name"
    last_name = user.last_name or "No last name"

    # Prepare the user information message
    info_message = (
        f"*User Info {first_name}!:*\n\n"
        f"👤 *First Name:* {first_name}\n"
        f"👥 *Last Name:* {last_name}\n"
        f"🆔 *User ID:* `{user_id}`\n"
        f"📝 *Username:* @{username}\n"
    )

    # Check if the user has a profile photo
    profile_photos = await user.get_profile_photos()

    if profile_photos.total_count > 0:
        # Send the profile picture with the user info as the caption
        profile_picture = profile_photos.photos[0][-1].file_id  # Get the highest quality photo
        await update.message.reply_photo(
            photo=profile_picture,
            caption=info_message,
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        # If no profile picture, send the info message with an inline keyboard
        keyboard = [
            [InlineKeyboardButton("Join our Channel 📢", url=owner)],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            info_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )


async def cst(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_message = (
        "💬 **checking status...:**\n"
        "✅ I am alive! \n"

    )
    # Reply to the user
    await update.message.reply_text(text=reply_message, parse_mode="Markdown")
decoded_url = base64.b64decode(encoded_url).decode('utf-8')
async def id_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Delay execution by 0.5 seconds
        time.sleep(0.2)

        user_id = update.message.from_user.id
        chat_id = update.message.chat.id if update.message.chat.id else "Not available"
        
        # Respond with user and chat ID in Markdown format, added emojis
        await update.message.reply_text(
            f"👤 **User ID**: `{user_id}` 🆔\n"
            f"💬 **Chat ID**: `{chat_id}` 🗣️",
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Error handling /id command: {e}")
        await update.message.reply_text(
            "❌ Oops! Something went wrong while processing the '/id' command. Please try again later.",
            parse_mode='Markdown'
        )

async def show_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id  not in ADMIN_ID:
        # If the user is not the admin, send an unauthorized message
        await update.message.reply_text("❌ You are not authorized to use this command.", parse_mode='Markdown')
        return

    user_data = load_user_ids()
    if user_data:
        response = "*List of All Users:*\n"
        for i, user_id in enumerate(user_data, 1):
            try:
                # Fetch user information dynamically using get_chat (equivalent to get_entity in Telethon)
                user_entity = await update.effective_chat.get_member(user_id)

                # Get the username if available
                username = user_entity.user.username if user_entity.user.username else 'N/A'

                # Add the user info to the response
                response += f"{i}) *ID:* `{user_id}` *Username:* @{username}\n"
            except BadRequest:
                # Handle invalid user_id if any
                response += f"{i}) *ID:* `{user_id}` *Username:* N/A (Invalid User ID)\n"
            except Exception as e:
                # Handle other exceptions
                response += f"{i}) *ID:* `{user_id}` *Username:* N/A (Error: {str(e)})\n"

        # Send the response to the admin
        await update.message.reply_text(response, parse_mode='Markdown')
    else:
        await update.message.reply_text("⚠️ No users found in the database.", parse_mode='Markdown')

L = instaloader.Instaloader()

def uid():
    return randint(1000000000000000000, 9999999999999999999)

def get_instagram_info(username: str) -> str:
    try:
        # Initialize Instaloader
        L = instaloader.Instaloader()

        # Load the profile using Instaloader
        profile = instaloader.Profile.from_username(L.context, username)

        # Collecting profile information in Markdown format
        info = f"*Instagram Profile Information of {profile.full_name}!*\n\n"
        info += f"**👤 Username:** `{profile.username}`\n"
        info += f"**📝 Full Name:** `{profile.full_name}`\n"
        info += f"**📖 Bio:** `{profile.biography}`\n"
        info += f"**👥 Followers:** `{profile.followers}`\n"
        info += f"**👥 Following:** `{profile.followees}`\n"
        info += f"**📸 Posts:** `{profile.mediacount}`\n"
        info += f"**🔒 Private Account:** `{('Yes' if profile.is_private else 'No')}`\n"
        info += f"**✅ Verified:** `{('Yes' if profile.is_verified else 'No')}`\n"
        info += f"**🖼 Profile Pic:** [Profile Pic]({profile.profile_pic_url})\n"
        info += f"**🔗 Instagram Link:** [Instagram](https://instagram.com/{profile.username})\n"
        info += f"**🏢 Business Account:** `{('Yes' if profile.is_business_account else 'No')}`\n"
        info += f"**🌐 External URL:** `{profile.external_url if profile.external_url else 'None'}`\n"
        info += f"**📊 Followers (Ratio):** `{profile.followers / max(profile.followees, 1):.2f}`\n"
        info += f"**🆔 Profile ID:** `{profile.userid}`\n"
        
        # If the profile is public, fetch additional information
        if not profile.is_private:
            # Additional profile details through requests (optional)
            csr = hexlify(bytes([randint(0, 255) for _ in range(8)]))  # Generate random csrf token
            headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Host": "i.instagram.com",
                "Connection": "Keep-Alive",
                "User-Agent": "Instagram 10.26.0 Android",
                "Cookie": "mid=YwvCRAABAAEsZcmT0OGJdPu3iLUs; csrftoken=" + csr.decode(),
                "Cookie2": "$Version=1",
                "Accept-Language": "en-US",
                "X-IG-Capabilities": "AQ==",
                "Accept-Encoding": "gzip",
            }
            data = {
                "q": username,
                "device_id": f"android{uid()}",
                "guid": str(uid()),
                "_csrftoken": csr.decode()
            }
            response = requests.post('https://i.instagram.com/api/v1/users/lookup/', headers=headers, data=data).json()

            # Check if the response indicates the user is not found
            if response.get('status') == 'fail':
                return f"Error: The Instagram profile '{username}' does not exist or is unavailable."

            # Extract additional details from the response
            user_data = response.get('user', {})
            if not user_data:
                return "Error: Failed to retrieve profile details."

            email = user_data.get('obfuscated_email', 'N/A')
            user_id = user_data.get('pk', 'N/A')
            is_private = user_data.get('is_private', 'N/A')
            has_phone = user_data.get('has_valid_phone', 'N/A')
            can_email_reset = user_data.get('can_email_reset', 'N/A')
            can_sms_reset = user_data.get('can_sms_reset', 'N/A')
            can_wa_reset = user_data.get('can_wa_reset', 'N/A')
            fb_login_option = user_data.get('fb_login_option', 'N/A')
            phone_number = user_data.get('phone_number', 'N/A')

            # Append the additional information
            info += f"**📧 Email:** `{email}`\n"
            info += f"**🆔 User ID:** `{user_id}`\n"
            info += f"**🔒 Is Private:** `{is_private}`\n"
            info += f"**📱 Has Phone Number:** `{has_phone}`\n"
            info += f"**🔄 Can Reset Email:** `{can_email_reset}`\n"
            info += f"**🔄 Can Reset SMS:** `{can_sms_reset}`\n"
            info += f"**🔄 Can Reset WhatsApp:** `{can_wa_reset}`\n"
            info += f"**🔐 Facebook Login Option:** `{fb_login_option}`\n"
            info += f"**📞 Phone Number:** `{phone_number}`\n"

        # Return the combined information
        return info

    except instaloader.exceptions.ProfileNotExistsException:
        return "🛠️Error: The Instagram profile does not exist or has been deleted."
    except requests.exceptions.RequestException as e:
        return f"🛠️Error: There was an issue connecting to Instagram. Please try again later. "
    except Exception as e:
        return f"🛠️Error: An unexpected issue occurred. Please try again later.Or check if username is correct or not"
xd = InlineKeyboardButton("Developer📚", url=f"{decoded_url}")
async def insta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        username = context.args[0]

        # Clean the username by removing '@' if present, but leave other special characters intact
        username = username.lstrip('@')

        try:
            # Send initial progress message
            progress_message = await update.message.reply_text(
                "Gathering information, please wait...\n\n"
                "Progress 🏴‍☠: [----------] 0% Time Elapsed: 0.00s",
                parse_mode=ParseMode.MARKDOWN
            )

            # Start the dummy progress animation
            start_time = time.time()
            dummy_percentage = 0
            while dummy_percentage < 100:
                elapsed_time = time.time() - start_time
                progress_text = f"Progress 🏴‍☠: [{'=' * (dummy_percentage // 10) + '-' * (10 - dummy_percentage // 10)}] {dummy_percentage}%"
                elapsed_time_text = f"Time Elapsed⚡: {elapsed_time:.2f}s"
                update_text = f"🏴‍☠ Gathering information, please wait...\n\n{progress_text}\n{elapsed_time_text}"
                await progress_message.edit_text(update_text, parse_mode=ParseMode.MARKDOWN)

                dummy_percentage += 10
                await asyncio.sleep(0.6)  
            final_elapsed_time = time.time() - start_time
            final_progress_text = f"Progress: [{'=' * 10}] 100%"
            final_elapsed_time_text = f"Time Elapsed: {final_elapsed_time:.2f}s"
            final_update_text = f"Progress 🏴‍☠:\n{final_progress_text}\n{final_elapsed_time_text}"
            await progress_message.edit_text(final_update_text, parse_mode=ParseMode.MARKDOWN)

            try:
                profile_info = get_instagram_info(username)

                public_info, private_info = profile_info.split("\n\n**Private Info:**", 1) if "**Private Info:**" in profile_info else (profile_info, "")

                await update.message.reply_text(f"{public_info}", parse_mode=ParseMode.MARKDOWN)

                if private_info:
                    await update.message.reply_text(f"{private_info}", parse_mode=ParseMode.MARKDOWN)

            except Exception as e:
                logging.error(f"Error fetching Instagram info for {username}: {str(e)}")
                await update.message.reply_text(f"Error: Failed to retrieve Instagram info. Please check the username and try again.")

        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            await update.message.reply_text(f"Error: {str(e)}")

    else:
        await update.message.reply_text(
            "*Please provide an Instagram username*\n*Usage: /insta @username.*", 
            parse_mode="Markdown"
        )


# Use 'big' font or another font of your choice for wider text
ascii_art = pyfiglet.figlet_format("Bot is alive", font="big")

# Adjust the width of the text
ascii_art = ascii_art.center(150)
def main() -> None:
        TELEGRAM_TOKEN = TELEGRAM_TOKEN

        application = Application.builder().token(TELEGRAM_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("broad", handle_broadcast))
        application.add_handler(CommandHandler("info", info))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("feedback", feedback_command))
        application.add_handler(CommandHandler("cst", cst))
        application.add_handler(CommandHandler("id", id_command_handler))
        application.add_handler(CommandHandler("users", show_users))
        application.add_handler(CommandHandler("insta", insta))
        print(colored(ascii_art.center(150), "light_red"))
        application.run_polling()


if __name__ == '__main__':
        main()

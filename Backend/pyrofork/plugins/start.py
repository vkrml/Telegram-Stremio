from pyrogram import filters, Client, enums
from Backend.helper.custom_filter import CustomFilters
from pyrogram.types import Message
from Backend.config import Telegram

@Client.on_message(filters.command('start') & filters.private & CustomFilters.owner, group=10)
async def send_start_message(client: Client, message: Message):
    try:
        website_url = Telegram.BASE_URL

        await message.reply_text(
            '<b>Welcome to Links4U Archive Bot!</b>\n\n'
            'This bot manages the backend for the digital library.\n'
            'To access the content, visit the web archive:\n\n'
            f'👉 <b>{website_url}</b>',
            quote=True,
            parse_mode=enums.ParseMode.HTML
        )

    except Exception as e:
        await message.reply_text(f"⚠️ Error: {e}")

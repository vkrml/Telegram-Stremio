from pyrogram import filters, Client, enums
from Backend.helper.custom_filter import CustomFilters
from pyrogram.types import Message
from Backend.config import Telegram

@Client.on_message(filters.command('start') & filters.private & CustomFilters.owner)
async def send_start_message(client: Client, message: Message):
    base_url = Telegram.BASE_URL
    
    await message.reply_text(
        f"🚀 <b>Your Media Portal is Online!</b>\n\n"
        f"🔗 <b>Website:</b> {base_url}\n"
        f"🔑 <b>Admin Panel:</b> {base_url}/admin\n\n"
        "Forward movies or series to your authorized channels to update the catalog automatically.",
        quote=True,
        parse_mode=enums.ParseMode.HTML
    )

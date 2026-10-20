import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@ShunchakiMusiqaUz"


def obuna_tugmalari():
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "📢 Kanalga obuna bo‘lish",
            url="https://t.me/ShunchakiMusiqaUz"
        )],
        [InlineKeyboardButton(
            "✅ Obuna bo‘ldim",
            callback_data="check_subscription"
        )],
    ])


async def obunani_tekshir(user_id, context):
    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL,
            user_id=user_id
        )
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        print("Obuna tekshirish xatosi:", e)
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Salom! Musiqa yuborishdan oldin kanalga obuna bo‘l!",
        reply_markup=obuna_tugmalari()
    )


async def tekshirish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if await obunani_tekshir(query.from_user.id, context):
        await query.edit_message_text(
            "✅ Obuna tasdiqlandi! Endi menga musiqa yubor."
        )
    else:
        await query.answer(
            "Avval kanalga obuna bo‘l!", show_alert=True
        )


async def music_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    message = update.message

    if not await obunani_tekshir(message.from_user.id, context):
        await message.reply_text(
            "Avval kanalga obuna bo‘l!",
            reply_markup=obuna_tugmalari()
        )
        return

    if message.audio:
        audio = message.audio
        title = audio.title or "Noma'lum qo'shiq"
        artist = audio.performer or "Noma'lum ijrochi"

        caption = (
            f"🎵 {title}\n"
            f"🎤 {artist}\n\n"
            f"📢 @ShunchakiMusiqaUz"
        )

        await context.bot.send_audio(
            chat_id=CHANNEL,
            audio=audio.file_id,
            caption=caption
        )

        await message.reply_text("✅ Musiqa kanalingga joylandi!")
    else:
        await message.reply_text("Iltimos, musiqa faylini yubor.")


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN sozlanmagan!")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        CallbackQueryHandler(tekshirish, pattern="^check_subscription$")
    )
    app.add_handler(
        MessageHandler(filters.AUDIO, music_handler)
    )
    app.run_polling()


if __name__ == "__main__":
    main()

import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.filters import CommandStart
from aiogram.enums import ChatMemberStatus


# =========================
# 🔐 НАСТРОЙКИ
# =========================

TOKEN = os.getenv("8528151092:AAEfpe4jOC1fEotFvx0m1Y6I3wJ8oIQhGR4")  # токен берётся из переменных окружения
CHANNEL_USERNAME = "@vlgIive"   # username канала
ADMIN_ID = 7612070974            # твой Telegram ID


if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Добавь его в переменные окружения.")


bot = Bot(token=TOKEN)
dp = Dispatcher()



# 🔹 Клавиатура подписки
def subscription_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📢 Подписаться",
                url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
            )
        ],
        [
            InlineKeyboardButton(
                text="✅ Проверить подписку",
                callback_data="check_sub"
            )
        ]
    ])
    return keyboard


# 🔹 Проверка подписки
async def check_subscription(user_id: int) -> bool:
    member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
    return member.status in [
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.CREATOR
    ]


# 🔹 /start
@dp.message(CommandStart())
async def start_handler(message: Message):
    text = (
        "👋 Добро пожаловать в предложку новостного канала *VLG LIVE*!\n\n"
        "📰 Здесь вы можете предложить новость, фото или видео.\n\n"
        "Чтобы отправить материал — подпишитесь на канал и подтвердите подписку."
    )
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=subscription_keyboard()
    )


# 🔹 Обработка кнопки проверки
@dp.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery):
    is_subscribed = await check_subscription(callback.from_user.id)

    if is_subscribed:
        await callback.message.edit_text(
            "✅ Подписка подтверждена!\n\n"
            "Теперь отправьте новость, фото или видео для публикации."
        )
    else:
        await callback.answer("❌ Вы ещё не подписались!", show_alert=True)


# 🔹 Обработка сообщений
@dp.message()
async def handle_message(message: Message):
    is_subscribed = await check_subscription(message.from_user.id)

    if not is_subscribed:
        await message.answer(
            "❌ Для отправки новости необходимо подписаться на канал.",
            reply_markup=subscription_keyboard()
        )
        return

    # Пересылаем админу
    await bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id
    )

    await message.answer("✅ Спасибо! Ваша новость отправлена на рассмотрение.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

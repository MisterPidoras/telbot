import asyncio
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.enums import ParseMode, ChatType
from aiogram.filters import Command, ChatMemberUpdatedFilter, JOIN_TRANSITION, CommandStart
from aiogram.types import ContentType, Message, ChatMemberUpdated
from aiogram.client.default import DefaultBotProperties

TOKEN = ""
ADMIN_IDS = [728594122, 7898080464] 
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
bot.my_admins_list = ADMIN_IDS

# Создаем роутеры
dp = Dispatcher()
user_group_router = Router()

# Фильтр для групповых чатов
class ChatTypeFilter:
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types

# Применяем фильтры к роутерам
user_group_router.message.filter(ChatTypeFilter(["group", "supergroup"]))
user_group_router.edited_message.filter(ChatTypeFilter(["group", "supergroup"]))

# Обработчик нового участника
@user_group_router.chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def new_member(event: ChatMemberUpdated, bot: Bot):
    user = event.new_chat_member.user
    chat = event.chat

    # Уведомление только админам (без приветствия в группе)
    for admin_id in bot.my_admins_list:
        try:
            username_text = f"@{user.username}" if user.username else "❌ Нет юзернейма"
            await bot.send_message(
                chat_id=admin_id,
                text=f"🔔 Новый участник в группе <b>{chat.title}</b>:\n"
                     f"👤 Имя: <a href='tg://user?id={user.id}'>{user.full_name}</a>\n"
                     f"🆔 ID: <code>{user.id}</code>\n"
                     f"📌 Юзернейм: {username_text}",
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Ошибка отправки уведомления админу {admin_id}: {e}")


async def main():
    dp.include_router(user_group_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())

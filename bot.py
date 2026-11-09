import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession

TOKEN = "9259216256:AAEqlZ0fvK_gzX5nzUnPg_xVjK6Fahcm-TU"

logging.basicConfig(level=logging.INFO)
session = AiohttpSession()
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()

# Хранилище истории диалогов для каждого пользователя
histories = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я умный бот на базе нейросети. Напиши мне что-нибудь, и я отвечу.\n/clear - очистить историю.")

@dp.message(Command("clear"))
async def cmd_clear(message: types.Message):
    histories[message.from_user.id] = []
    await message.answer("История диалога очищена!")

@dp.message()
async def chat_handler(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    # Показываем статус "печатает"
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # Достаем историю пользователя (или создаем новую)
    history = histories.get(user_id, [])
    history.append({"role": "user", "content": text})
    history = history[-5:] # Оставляем только последние 5 сообщений

    try:
        # Отправляем запрос к локальной Ollama
        response = requests.post("http://localhost:11434/api/chat", json={
            "model": "llama3.2",
            "messages": history,
            "stream": False
        })
        
        answer = response.json()["message"]["content"]
        history.append({"role": "assistant", "content": answer})
        histories[user_id] = history

        await message.answer(answer)
    except Exception as e:
        await message.answer(f"Ошибка: убедись, что Ollama запущена.\n{e}")

async def main():
    print("Умный бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
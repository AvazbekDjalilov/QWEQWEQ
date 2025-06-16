from telethon import TelegramClient, events
import re
import asyncio
from collections import defaultdict

# Ваши API_ID и API_HASH
api_id = 21315612
api_hash = '0cb203071f7c204af47bd8e3193cbd71'

# Источники и цель
source_channels = ['CodeAntipova', 'ecotopor']
target_channel = 'World_Nuws'

client = TelegramClient('session_name', api_id, api_hash)
album_groups = defaultdict(list)

def clean_text(text):
    # Удаляет ссылки (http, https, t.me и др.), @упоминания, юзернеймы
    text = re.sub(r'http\S+', '', text)                # Удалить все http/https ссылки
    text = re.sub(r't\.me/\S+', '', text)              # Удалить t.me ссылки
    text = re.sub(r'@\w+', '', text)                   # Удалить @username
    text = re.sub(r'\s+', ' ', text).strip()           # Удалить лишние пробелы
    return text

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    message = event.message
    grouped_id = message.grouped_id

    if grouped_id:
        album_groups[grouped_id].append(message)
        await asyncio.sleep(1.5)
        if len(album_groups[grouped_id]) > 1:
            messages = album_groups.pop(grouped_id)
            media_files = [m.media for m in messages if m.media]
            first_msg = messages[0]
            clean_caption = clean_text(first_msg.text or '')
            try:
                await client.send_file(target_channel, file=media_files, caption=clean_caption)
            except Exception as e:
                print(f"Ошибка при пересылке альбома: {e}")
    else:
        clean_caption = clean_text(message.text or '')
        try:
            if message.media:
                await client.send_file(target_channel, file=message.media, caption=clean_caption)
            else:
                if clean_caption:
                    await client.send_message(target_channel, clean_caption)
        except Exception as e:
            print(f"Ошибка при пересылке сообщения: {e}")

client.start()
print("✅ Бот запущен. Ожидаю сообщения...")
client.run_until_disconnected()

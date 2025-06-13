from telethon import TelegramClient, events
from telethon.tl.types import (
    MessageEntityBold, MessageEntityItalic, MessageEntityUnderline,
    MessageEntityStrike, MessageEntityCode, MessageEntityPre
)
import html
import asyncio
from collections import defaultdict

# Ваши API_ID и API_HASH
api_id = 21315612
api_hash = '0cb203071f7c204af47bd8e3193cbd71'

# Источники и цель
source_channels = ['CodeAntipova', 'ecotopor']
target_channel = 'nuwseco'

client = TelegramClient('session_name', api_id, api_hash)
album_groups = defaultdict(list)

def render_html(text, entities):
    if not entities:
        return html.escape(text)
    result = []
    last_offset = 0
    for entity in sorted(entities, key=lambda e: e.offset):
        if last_offset < entity.offset:
            result.append(html.escape(text[last_offset:entity.offset]))
        entity_text = text[entity.offset:entity.offset + entity.length]
        entity_html = html.escape(entity_text)
        if isinstance(entity, MessageEntityBold):
            entity_html = f"<b>{entity_html}</b>"
        elif isinstance(entity, MessageEntityItalic):
            entity_html = f"<i>{entity_html}</i>"
        elif isinstance(entity, MessageEntityUnderline):
            entity_html = f"<u>{entity_html}</u>"
        elif isinstance(entity, MessageEntityStrike):
            entity_html = f"<s>{entity_html}</s>"
        elif isinstance(entity, MessageEntityCode):
            entity_html = f"<code>{entity_html}</code>"
        elif isinstance(entity, MessageEntityPre):
            entity_html = f"<pre>{entity_html}</pre>"
        result.append(entity_html)
        last_offset = entity.offset + entity.length
    if last_offset < len(text):
        result.append(html.escape(text[last_offset:]))
    return ''.join(result)

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
            html_text = render_html(first_msg.text or '', first_msg.entities or [])
            try:
                await client.send_file(target_channel, file=media_files, caption=html_text, parse_mode='html')
            except Exception as e:
                print(f"Ошибка при пересылке альбома: {e}")
    else:
        text = message.text or ''
        html_text = render_html(text, message.entities or [])
        try:
            if message.media:
                await client.send_file(target_channel, file=message.media, caption=html_text, parse_mode='html')
            else:
                await client.send_message(target_channel, html_text, parse_mode='html')
        except Exception as e:
            print(f"Ошибка при пересылке сообщения: {e}")

client.start()
print("✅ Бот запущен. Ожидаю сообщения...")
client.run_until_disconnected()

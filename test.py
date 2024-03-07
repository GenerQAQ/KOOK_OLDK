# test.py
from khl import Message

async def world(msg: Message):
    await msg.reply('你好呀~')

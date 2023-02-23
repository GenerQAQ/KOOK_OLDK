from khl import Bot, Message
from khl.command import Command
from khl import HTTPRequester

from keep_alive import keep_alive
import os

from epic import epicCard

# init Bot
token = os.environ['KOOK_oldK']
bot = Bot(token)


# register command, send `/hello` in channel to invoke
@bot.command(name='hello')
async def world(msg: Message):
    await msg.reply('我是人气最旺探员-老K!')


# 嗦牛子代码
def snz(msg: Message) -> bool:
    return msg.content.find('嗦牛子') != -1


@bot.command(rules=[snz])
async def 嗦牛子(msg: Message, comment: str):
    await msg.reply(f'{comment}太小了! 根本看不到')


# 获取epic免费游戏 发送卡片
@bot.command()
async def epic(msg: Message):
    await msg.ctx.channel.send(epicCard())


# 捕获epic指令接口报错
@epic.on_exception(HTTPRequester.APIRequestFailed)
async def on_epic_exc(cmd: Command, exc: HTTPRequester.APIRequestFailed,
                      msg: Message):
    await msg.reply(f'err {exc} raised during handling {cmd.name}')


# everything done, go ahead now!
keep_alive()
bot.run()
# now invite the bot to a server, and send '/hello' in any channel
# (remember to grant the bot with read & send permissions)

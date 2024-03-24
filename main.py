import json
import os
import redis
from khl import Message,Bot,Cert,PublicMessage
from epic import update_epic_data,update_epic_card,send_channel


def open_file(path: str):
    """打开path对应的json文件"""
    # 获取当前脚本所在的目录路径
    current_dir = os.path.dirname(__file__)
    # 使用相对路径拼接文件路径
    file_path = os.path.join(current_dir, path)
    with open(file_path, 'r', encoding='utf-8') as f:
        tmp = json.load(f)
    return tmp


# 打开config.json
config = open_file('./config/config.json')

# redis
r = redis.Redis(host=config['redis_host'], port=config['redis_port'], password=config['redis_password'], db=0, decode_responses=True)

# 初始化机器人
bot = Bot(token=config['token'])  # 默认采用 websocket
"""main bot"""
if not config['using_ws']:  # webhook
    # 当配置文件中'using_ws'键值为false时，代表不使用websocket
    # 此时采用webhook方式初始化机器人
    print(f"[BOT] using webhook at port {config['webhook_port']}")
    bot = Bot(cert=Cert(token=config['token'],
                        verify_token=config['verify_token'],
                        encrypt_key=config['encrypt_token']),
                        port=config['webhook_port'])

# 启动前执行
@bot.on_startup
async def bot_start_task(bot: Bot):
    update_epic_data()
    update_epic_card()

# 机器人启动后执行
@bot.task.add_date(timezone='Asia/Shanghai')
async def add_date_task():
    await bot.client.update_listening_music('求毛的故事', '给你看看我的大宝贝！', 'cloudmusic')

# 添加定时发送消息的频道
@bot.task.add_cron(day_of_week=4, hour=20, minute=0, timezone="Asia/Shanghai")
async def auto_skin_notify_task():
    # 定时发送消息的频道列表
    update_epic_data()
    update_epic_card()
    # 获取所有的频道id
    channels = r.keys('*')

    print("-" * 10)
    print("[BOT] channels id list")
    for channel_id in channels:
        await send_channel(bot, channel_id)
        print(f"[BOT] send message to {channel_id} - {r.get(channel_id)}")
    print("-" * 10)

# 添加定时发送消息的频道
@bot.command(name='start_epic')
async def start_epic(msg:Message):
    """将用户发送的频道ID添加到定时发送消息的频道列表"""
    if isinstance(msg, PublicMessage):
        # 添加频道id至redis
        hax = r.setnx(msg.ctx.channel.id, msg.ctx.channel.name)
        if hax == False:
            await msg.reply("该频道已经添加过了, 每周五20:00点会提醒各位老登")
            return

        await msg.reply("添加成功，/stop_epic取消")
        await send_channel(bot, msg.ctx.channel.id)
    else:
        # 是私聊消息
        await msg.reply("别私信我，我懒得理你")

# 取消定时发送消息的频道
@bot.command(name='stop_epic')
async def stop_epic(msg:Message):
    """将用户发送的频道ID从定时发送消息的频道列表中移除"""
    if isinstance(msg, PublicMessage):
        # 公共频道消息
        de = r.delete(msg.ctx.channel.id)
        if de == 0:
            await msg.reply("该频道不在定时发送消息的频道列表中")
            return

        await msg.reply("取消成功，/start_epic重新添加")
    else:
        # 是私聊消息
        await msg.reply("别私信我，我懒得理你")

# 临时发送epic消息
@bot.command(name='epic')
async def epic(msg:Message):
    """将用户发送的频道ID从定时发送消息的频道列表中移除"""
    if isinstance(msg, PublicMessage):
        # 公共频道消息
        await send_channel(bot, msg.ctx.channel.id)
    else:
        # 是私聊消息
        await msg.reply("别私信我，我懒得理你")


# 启动机器人
if __name__ == '__main__':
    # 获取所有的频道id
    channels = r.keys()
    if 0 != len(channels):
        print("-" * 10)
        print("[BOT] channels id list")
        for channel in channels:
            print(channel)
        print("-" * 10)
    else:
        print("-" * 10)
        print("[BOT] no channels")
        print("-" * 10)

    print("[BOT] bot is running")
    bot.run()
    print("[BOT] bot is stoped")

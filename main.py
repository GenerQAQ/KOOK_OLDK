from khl import Bot, Message
from keep_alive import keep_alive
import os
import time
import json

import requests
from bs4 import BeautifulSoup

from datetime import datetime
from datetime import timedelta
# from datetime import timezone

from khl.card import CardMessage, Card, Module, Element, Types, Struct

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


def get_epic():
    url = 'https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=zh-Hant&country=CN&allowCountries=CN'
    get_url = requests.get(url=url)
    card = set_card(get_url.text)
    return card


def set_card(text):
    # 创建机器人卡片配置属性
    c1 = Card(theme=Types.Theme.SUCCESS, size=Types.Size.LG)
    c1.append(Module.Header('现在免费'))
    c1.append(Module.Divider())
    c2 = Card(theme=Types.Theme.INFO, size=Types.Size.LG)
    c2.append(Module.Header('即将推出'))
    c2.append(Module.Divider())
    cm = CardMessage()
    fmt_text = json.loads(text)
    jump_first = 'https://store.epicgames.com/zh-Hant/p/'
    # print(fmt_text['data']['Catalog']['searchStore']['elements'])
    for item in fmt_text['data']['Catalog']['searchStore']['elements']:
        # print(item['promotions'])
        if (item['promotions'] == None):
            continue
        # 促销优惠
        if (len(item['promotions']['promotionalOffers'])) and (item['price']['totalPrice']['discountPrice'] == 0):
            # promotionalOffers.append({
            #   "title": item['title'],
            #   "img": item['keyImages'][0]['url'],
            # })
            c1.append(Module.Header(':joystick:' + item['title']))
            info = item['description']
            start_time = item['promotions']['promotionalOffers'][0][
                'promotionalOffers'][0]['startDate']
            start_time = datetime.strptime(
                start_time, "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8)
            end_time = item['promotions']['promotionalOffers'][0][
                'promotionalOffers'][0]['endDate']
            end_time = datetime.strptime(
                end_time, "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8)
            game_type = item['offerType']
            c1.append(Module.Section(Element.Text(info, Types.Text.KMD)))
            c1.append(
                Module.Section(
                    Struct.Paragraph(1, f'开始时间：{start_time}',
                                     f'结束时间：{end_time}', f'游戏类型：{game_type}'),
                    # LINK type: user will open the link in browser when clicked
                    Element.Image(item['keyImages'][0]['url'], "", False,
                                  Types.Size.SM),
                    Types.SectionMode.RIGHT))
            c1.append(Module.Countdown(end_time, mode=Types.CountdownMode.DAY))
            # print(item['catalogNs']['mappings'][0]['pageSlug'])
            productSlug = item['productSlug'] if item[
                'productSlug'] != None else item['catalogNs']['mappings'][0][
                    'pageSlug']
            c1.append(
                Module.Section(
                    "",
                    Element.Button('前往领取', jump_first + productSlug,
                                   Types.Click.LINK)))
            c1.append(Module.Divider())
        # 即将到来的促销优惠
        if (len(item['promotions']['upcomingPromotionalOffers'])):
            c2.append(Module.Header(':joystick:' + item['title']))
            info = item['description']
            start_time = item['promotions']['upcomingPromotionalOffers'][0][
                'promotionalOffers'][0]['startDate']
            start_time = datetime.strptime(
                start_time, "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8)
            end_time = item['promotions']['upcomingPromotionalOffers'][0][
                'promotionalOffers'][0]['endDate']
            end_time = datetime.strptime(
                end_time, "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8)
            game_type = item['offerType']
            c2.append(Module.Section(Element.Text(info, Types.Text.KMD)))
            c2.append(
                Module.Section(
                    Struct.Paragraph(1, f'开始时间：{start_time}',
                                     f'结束时间：{end_time}', f'游戏类型：{game_type}'),
                    # LINK type: user will open the link in browser when clicked
                    Element.Image(item['keyImages'][0]['url'], "", False,
                                  Types.Size.SM),
                    Types.SectionMode.RIGHT))
            c2.append(Module.Divider())

    cm.append(c1)
    cm.append(c2)
    return cm


# 爬取喜加一页面&拼接机器人卡片
def get_free():
    # 设置获取URL
    url = 'https://steamstats.cn/xi'
    # 设置请求头部
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36 Edg/90.0.818.41'
    }
    # 调用requests获得页面内容
    r = requests.get(url, headers=headers)
    # 判断返回状态是不是200
    r.raise_for_status()
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, "html.parser")
    # 寻找特定标签
    tbody = soup.find('tbody')
    trs = tbody.find_all('tr')
    # 创建机器人卡片配置属性
    c1 = Card(theme=Types.Theme.INFO, size=Types.Size.LG)
    # 添加头部
    c1.append(Module.Header('今日囍加壹'))
    # 判重
    repeat = []
    # 遍历页面表格&整理内容
    for tr in trs:
        td = tr.find_all('td')
        # 判断有重复值 跳出本次遍历
        if (td[1].find('a')['title'].replace(' ', '') in repeat):
            continue
        repeat.append(td[1].find('a')['title'].replace(' ', ''))
        # 将字符串时间转为utc时间 => 给倒计时用
        end_time = td[4].string.replace('\n',
                                        '').replace('\r',
                                                    '').strip()  # 获取时间字符串
        fmt_time = time.strptime(end_time, "%Y-%m-%d %H:%M")  # 转格式化时间
        fmt_time = int(time.mktime(fmt_time))  # 转时间戳
        fmt_time = datetime.utcfromtimestamp(fmt_time) - timedelta(
            hours=8)  # 转utc时间 时区问题需要减去8小时倒计时才正常
        # 整理信息内容
        start_time = td[3].string.replace('\n', '').replace('\r', '').strip()
        end_time = td[4].string.replace('\n', '').replace('\r', '').strip()
        game_type = td[2].string.replace('\n', '').replace('\r', '').strip()
        long = td[5].string.replace('\n', '').replace('\r', '').strip()
        # 整理按钮 名称 & 跳转URL
        jump_name = td[6].find('span').string.replace('\n',
                                                      '').replace('\r',
                                                                  '').strip()
        jump_url = td[1].find('a')['href']
        # -------------------------------
        # 分割线
        c1.append(Module.Divider())
        # 游戏名称
        c1.append(
            Module.Section(
                Element.Text(f'**{td[1].find("a")["title"]}**',
                             Types.Text.KMD)))
        # 信息&按钮
        c1.append(
            Module.Section(
                Struct.Paragraph(2, f'开始:{start_time}', f'类型:{game_type}',
                                 f'结束:{end_time}', f'永久?{long}'),
                # LINK type: user will open the link in browser when clicked
                Element.Button(jump_name, jump_url, Types.Click.LINK)))
        # 倒计时模块
        c1.append(Module.Countdown(fmt_time, mode=Types.CountdownMode.DAY))
        # -------------------------------
    # 添加尾部
    c1.append(Module.Divider())
    # 封装卡片
    cm = CardMessage(c1)
    return cm


@bot.command()
async def 喜加一(msg: Message):
    # 获取当前时间
    # SHA_TZ = timezone(
    #     timedelta(hours=8),
    #     name='Asia/Shanghai',
    # )
    # 协调世界时
    # utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    # 北京时间
    # beijing_now = utc_now.astimezone(SHA_TZ).strftime("%H:%M")
    await msg.reply(get_free())


@bot.command()
async def epic(msg: Message):
    await msg.reply(get_epic())


# everything done, go ahead now!
get_epic()
keep_alive()
bot.run()
# now invite the bot to a server, and send '/hello' in any channel
# (remember to grant the bot with read & send permissions)

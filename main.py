from khl import Bot, Message
from keep_alive import keep_alive
import os
import json

import requests

from datetime import datetime
from datetime import timedelta

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
        # print(item['title'])
        # print('------------------------')
        if (item['promotions'] == None):
            continue
        # 促销优惠
        if (len(item['promotions']['promotionalOffers'])) and (
                item['price']['totalPrice']['discountPrice'] == 0):
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
            productSlug = item[
                'productSlug'] if item['productSlug'] != None else item[
                    'catalogNs']['mappings'][0]['pageSlug']
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


@bot.command()
async def epic(msg: Message):
    await msg.reply(get_epic())


# everything done, go ahead now!
keep_alive()
bot.run()
# now invite the bot to a server, and send '/hello' in any channel
# (remember to grant the bot with read & send permissions)

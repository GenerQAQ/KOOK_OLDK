# epic.py
import requests
import json
import os
from datetime import datetime, timedelta
from khl.card import CardMessage,Types,Card,Module,Element,Struct
from khl import Bot

global_epic_data = []

global_epic_card = CardMessage()

global_epic_jump_first = 'https://store.epicgames.com/zh-CN/p/'

def update_epic_data():
    """更新epic数据到全局变量"""
    global global_epic_data
    url = 'https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?locale=zh-CN&country=CN&allowCountries=CN'
    html = requests.get(url=url)
    resp = json.loads(html.text)
    
    items = resp['data']['Catalog']['searchStore']['elements']
    
    global_epic_data = []
    now_frees = {
        'title': '现在免费',
        'type': 'now',
        'theme': Types.Theme.SUCCESS,
        'size': Types.Size.LG,
        'games': []
    }
    coming_frees = {
        'title': '即将免费',
        'type': 'coming',
        'theme': Types.Theme.INFO,
        'size': Types.Size.LG,
        'games': []
    }

    for item in items:
        if (item['promotions'] == None):
            continue

        # 当前免费
        if (len(item['promotions']['promotionalOffers'])) and (item['price']['totalPrice']['discountPrice'] == 0):
            now_frees['games'].append({
                'name': item['title'],
                'img': item['keyImages'][0]['url'],
                'desc': item['description'],
                'start_time': datetime.strptime(item['promotions']['promotionalOffers'][0]['promotionalOffers'][0]['startDate'], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8),
                'end_time': datetime.strptime(item['promotions']['promotionalOffers'][0]['promotionalOffers'][0]['endDate'], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8),
                'type': item['offerType'],
                'link': global_epic_jump_first + item['catalogNs']['mappings'][0]['pageSlug']
            })
            continue

        # 即将推出
        if (len(item['promotions']['upcomingPromotionalOffers'])):
            coming_frees['games'].append({
                'name': item['title'],
                'img': item['keyImages'][0]['url'],
                'desc': item['description'],
                'start_time': datetime.strptime(item['promotions']['upcomingPromotionalOffers'][0]['promotionalOffers'][0]['startDate'], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8),
                'end_time': datetime.strptime(item['promotions']['upcomingPromotionalOffers'][0]['promotionalOffers'][0]['endDate'], "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8),
                'type': item['offerType'],
                'link': global_epic_jump_first + item['catalogNs']['mappings'][0]['pageSlug']
            })
            continue

    global_epic_data.append(now_frees)
    global_epic_data.append(coming_frees)
    print("epic data updated")

def update_epic_card():
    """更新epic卡片"""
    global global_epic_card
    global global_epic_data

    if 0 == len(global_epic_data):
        return

    global_epic_card = CardMessage()
    for item in global_epic_data:
        if 0 == len(item['games']):
            continue
        games = []
        for game in item['games']:
            games.append(Module.Divider())
            games.append(Module.Header(':joystick:' + game['name']))
            games.append(Module.Section(Element.Text(game['desc'], Types.Text.KMD)))
            games.append(Module.Section(
                Struct.Paragraph(1, f'开始时间：{game["start_time"]}', f'结束时间：{game["end_time"]}', f'游戏类型：{game["type"]}'),
                # LINK type: user will open the link in browser when clicked
                Element.Image(game['img'], "", False, Types.Size.SM),
                Types.SectionMode.RIGHT
            ))
            if item['type'] == 'now':
                games.append(Module.Countdown(game['end_time'], mode=Types.CountdownMode.DAY))
                games.append(Module.Section("", Element.Button('前往领取', game['link'], Types.Click.LINK)))
            if item['type'] == 'coming':
                games.append(Module.Countdown(game['start_time'], mode=Types.CountdownMode.DAY))
        global_epic_card.append(
            Card(
                Module.Header(item['title']),
                *games,
                theme=item['theme'],
                size=item['size'],
            )
        )
    print("epic card updated")

async def send_channel(bot: Bot, channel_id: str):
    """主动发送消息"""
    global global_epic_card
    ch = await bot.client.fetch_public_channel(channel_id)
    await ch.send(global_epic_card)
    print(f"epic card sent {channel_id}")

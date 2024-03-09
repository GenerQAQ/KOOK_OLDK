# epic.py
import requests
import json
from datetime import datetime, timedelta
from khl import Message

global_epic_data = []

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
        'games': []
    }
    coming_frees = {
        'title': '即将免费',
        'games': []
    }

    for item in items:
        if (item['promotions'] == None):
            continue

        # 当前免费
        if (len(item['promotions']['promotionalOffers'])) and (item['price']['totalPrice']['discountPrice'] == 0):
            now_frees['games'].append({
                'name': '🕹'+item['title'],
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
                'name': '🕹'+item['title'],
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

def update_epic_card():
    """更新epic卡片"""


def add_channel_id(channel_id: str):
    """添加频道ID至配置文件"""
    with open('./config/channels.json', 'r') as f:
        data = json.load(f)
    if channel_id not in data['channels']:
        data['channels'].append(channel_id)
    with open('./config/channels.json', 'w') as f:
        json.dump(data, f, indent=4)

def remove_channel_id(channel_id: str):
    """移除频道ID至配置文件"""
    with open('./config/channels.json', 'r') as f:
        data = json.load(f)
    if channel_id in data['channels']:
        data['channels'].remove(channel_id)
    with open('./config/channels.json', 'w') as f:
        json.dump(data, f, indent=4)
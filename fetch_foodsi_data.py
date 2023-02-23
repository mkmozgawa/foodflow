import requests
import json
import dateutil.parser
from datetime import datetime


'''
Shamelessly stolen and hammered into the shape I needed from https://github.com/kacpi2442/am_bot
'''


def parse_foodsi_api(api_result):
    new_api_result = list()
    for restaurant in api_result['data']:
        current_item = restaurant
        current_item['opened_at'] = dateutil.parser.parse(
            restaurant['package_day']['collection_day']['opened_at']).strftime('%H:%M')
        current_item['closed_at'] = dateutil.parser.parse(
            restaurant['package_day']['collection_day']['closed_at']).strftime('%H:%M')
        if restaurant['package_day']['meals_left'] is None:
            current_item['package_day']['meals_left'] = 0
        new_api_result.append(current_item)
    return new_api_result


def call_foodsi():
    items = list()
    food = list()
    page = 1
    total_pages = 1
    while page <= total_pages:
        req_json = {
            "page": page,
            "per_page": 15,
            "distance": {
                "lat": 52.407120,
                "lng": 16.921319,
                "range": 10 * 1000
            },
            "hide_unavailable": True,
            "food_type": [],
            "collection_time": {
                "from": "00:00:00",
                "to": "23:59:59"
            }
        }
        foodsi_api = requests.post('https://api.foodsi.pl/api/v2/restaurants',
                                   headers={'Content-type': 'application/json', 'system-version': 'android_3.0.0',
                                            'user-agent': 'okhttp/3.12.0'}, data=json.dumps(req_json))
        items += parse_foodsi_api(foodsi_api.json())
        print(foodsi_api.json())
        total_pages = foodsi_api.json()['total_pages']
        page += 1

    for item in items:
        food.append({
            'place_name': item['name'],
            'place_url': item['url'],
            'description': item['meal']['description'],
            'longitude': item['longitude'],
            'latitude': item['latitude'],
            'meals_amount': item['meals_amount'],
            'discount_price': item['meal']['price'],
            'original_price': item['meal']['original_price'],
            'collection_day': item['package_day']['collection_day']['week_day'],
            'open_time': item['opened_at'],
            'close_time': item['closed_at'],
            'package_type': item['package_type'],
            'package_id': item['package_id'],
            'parent_id': item['parent_id'],
            'source': 'foodsi',
            'created_at': str(datetime.now())

        })
    return food


if __name__ == '__main__':
    results = call_foodsi()
    filename = str(datetime.now()).replace(' ', '_') + '.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

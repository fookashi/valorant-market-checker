import json

import aiofiles
import asyncio

from client import ValorantAPIClient
from datetime import datetime


async def write_into_result(filename, chunk):
    async with aiofiles.open(f'results/results.txt', 'a+') as f:
        data = json.dumps(chunk)
        await f.write(f'{data}\n')


class MarketChecker:
    
    @staticmethod
    async def check_market_from_file():
        async with aiofiles.open(f'results/results.txt', 'w') as f:
            pass
        users_info = {}
        async with aiofiles.open('gsheet_info/accounts.txt', 'r') as f:
            while line := await f.readline():
                userdata = line.rstrip('\n').split(':')
                username = userdata[0]
                password = userdata[1]
                users_info[username] = password

        filename_date = datetime.now().strftime("%d-%m-%Y %H_%M")
        filename = f'results_{filename_date}'
        for username, password in users_info.items():
            await MarketChecker.check_market_and_write(username, password, filename)
            await asyncio.sleep(5)

    @staticmethod
    async def check_market_and_write(username,password,filename):
        k = 0
        while k <= 5:
            try:
                market_info = await MarketChecker.check_user_market(username, password)
                print(username)
                await write_into_result(filename, market_info)
                break
            except Exception as e:
                print(e)
                k += 1
                print('Error appeared, attempt #', k+1)
                await asyncio.sleep(5)
    
    @staticmethod
    async def check_user_market(username,password):

        acc_auth = ValorantAPIClient(username,password)
        await acc_auth.set_access_token()
        await acc_auth.set_entitlements_token()
        await acc_auth.set_puuid()

        default_store_items = list()
        default_store_prices = list()
        result = {'username': username}
        market = await acc_auth.get_market_offers()

        for item in market["SkinsPanelLayout"]["SingleItemStoreOffers"]:
            skin_id = item['Rewards'][0]['ItemID']
            skin_name = await acc_auth.get_skin_name_from_id(skin_id)
            default_store_items.append(skin_name)
            default_store_prices.extend(item['Cost'].values())
        result['default_store'] = list(zip(default_store_items,default_store_prices))

        try:
            nm_items = list()
            nm_prices = list()
            for item in market['BonusStore']['BonusStoreOffers']:
                nm_prices.extend(item['DiscountCosts'].values())
                skin_id = item['Offer']['Rewards'][0]['ItemID']
                skin_name = await acc_auth.get_skin_name_from_id(skin_id)
                nm_items.append(skin_name)
            result['nightmarket_store'] = list(zip(nm_items, nm_prices))
        except KeyError:
            pass
        return result


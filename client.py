import asyncio

from fake_useragent import UserAgent
import aiohttp

from utils import extract_tokens
from errors import APIError


class ValorantAPIClient:

    def __init__(self, username, password) -> None:
        self.puuid = None
        self.entitlements_token = None
        self.access_token = None
        self.token_id = None
        self.username = username
        self.password = password
        self.ua = UserAgent().random

    async def set_access_token(self):
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': self.ua,
            'Accept': 'application/json, text/plain, */*', }
        data = {
            "client_id": "play-valorant-web-prod",
            "nonce": "1",
            "redirect_uri": "https://playvalorant.com/opt_in",
            "response_type": "token id_token",
            'scope': 'account openid',
        }
        async with aiohttp.ClientSession() as session:
            async with session.post('https://auth.riotgames.com/api/v1/authorization',
                                    json=data, headers=headers):
                pass
            data = {"type": "auth",
                    "username": self.username,
                    "password": self.password,
                    "remember": False}

            async with session.put('https://auth.riotgames.com/api/v1/authorization',
                                   json=data, headers=headers) as r:
                data = await r.json()
                if 'error' in data:
                    delay = r.headers.get('Retry-After')
                    if delay is None:
                        await asyncio.sleep(2)
                        return
                    print(f'sleeping for {str(delay)} seconds...')
                    await asyncio.sleep(int(delay))
            response = extract_tokens(data)
            access_token = response[0]
            token_id = response[1]
            self.access_token = str(access_token)
            self.token_id = str(token_id)

    async def set_entitlements_token(self):
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.access_token}'}
        async with aiohttp.ClientSession() as session:
            async with session.post('https://entitlements.auth.riotgames.com/api/token/v1',
                                    headers=headers, json={}) as r:
                data = await r.json()
        entitlements_token = data['entitlements_token']
        self.entitlements_token = str(entitlements_token)

    async def set_puuid(self):
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.access_token}'}
        async with aiohttp.ClientSession() as session:
            async with session.post('https://auth.riotgames.com/userinfo',
                                    headers=headers, json={}) as r:
                data = await r.json()

        self.puuid = str(data['sub'])

    async def get_market_offers(self):
        headers = {'Authorization': f'Bearer {self.access_token}',
                   'X-Riot-Entitlements-JWT': self.entitlements_token}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://pd.eu.a.pvp.net/store/v2/storefront/{self.puuid}",
                                   headers=headers) as r:
                data = await r.json()
        return data

    async def get_skin_name_from_id(self, skin_id):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://valorant-api.com/v1/weapons/skinlevels/{skin_id}") as r:
                data = await r.json()
        return data['data']['displayName']

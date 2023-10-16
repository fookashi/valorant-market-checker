import asyncio
import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import aiohttp
from aiohttp_socks import ProxyConnector

from marketchecker import MarketChecker
from GsheetManager import GsheetManager, get_creds
from ProxyParser import get_proxy

EXAMPLE_URL_HTTP = "http://www.instagram.com"
EXAMPLE_URL_HTTPS = "https://www.instagram.com"


async def check(
    url,
    http=True,
    https=True,
    EXAMPLE_URL_HTTP=EXAMPLE_URL_HTTP,
    EXAMPLE_URL_HTTPS=EXAMPLE_URL_HTTPS,
):
    try:
        async with aiohttp.ClientSession(raise_for_status=True) as client_session:
            if http:
                resp = await client_session.get(EXAMPLE_URL_HTTP, proxy=url)
                async with resp:
                    assert resp.status == 200
            if https:
                resp = await client_session.get(EXAMPLE_URL_HTTPS, proxy=url)
                async with resp:
                    assert resp.status == 200
    except Exception as e:
        print(e)
        return False, e
    else:
        return True, ''




async def update_info():
    print('Started process...')
    url = 'https://docs.google.com/spreadsheets/d/1oFWUaERYrdFQbyyrV9U6Z01pRDmU57RO8TDlamFtgFY/edit?usp=sharing'
    gm = GsheetManager(get_creds)
    await gm.parse_accounts_to_file(url=url, index=0)
    print('Parsed accounts from worksheet!')
    print('List of updated accounts: ')
    await MarketChecker.check_market_from_file()
    print('Updating info in worksheet!')
    await gm.update_sheet(url=url, index=0)
    print('Finally updated! Hoorey.')
    asyncio.get_event_loop().stop()


async def main():
    await update_info()

async def main2():
    scheduler = AsyncIOScheduler()
    job = scheduler.add_job(update_info, 'cron', hour=3, minute=5)
    scheduler.start()

    offset = datetime.timedelta(hours=3)
    tz = datetime.timezone(offset, name='МСК')
    now = datetime.datetime.now(tz=tz)
    print('TIME BEFORE START:')
    print(job.next_run_time - now)
    print('----------------------------\n')

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.create_task(main2())
    loop.run_forever()


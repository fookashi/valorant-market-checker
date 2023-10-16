from typing import Callable, Union
import asyncio

from gspread_asyncio import AsyncioGspreadClient, AsyncioGspreadClientManager
import gspread

import aiofiles
import json
from google.oauth2.service_account import Credentials
import aiofiles

def get_creds():
    file_name = 'client_key.json'
    creds = Credentials.from_service_account_file(file_name)
    scoped = creds.with_scopes([
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file'
    ])

    return scoped


class GsheetManager(AsyncioGspreadClient):

    def __init__(self, cred_fn: Callable[[], Credentials]):
        agcm = AsyncioGspreadClientManager(cred_fn, loop=asyncio.get_running_loop())
        gc = gspread.Client(cred_fn())
        AsyncioGspreadClient.__init__(self, agcm, gc)

    async def parse_accounts_to_file(self, url: str, index: int):
        sheets = await self.open_by_url(url)
        worksheet = await sheets.get_worksheet(index)
        not_sold = (await worksheet.findall('FALSE', in_column=4))[:1000]
        records = await worksheet.get_all_records()
        async with aiofiles.open('gsheet_info/accounts.txt', 'wb'):
            pass
        for acc_info in not_sold:
            row = acc_info.row - 2
            username = records[row].get('LOGIN')
            if username == '':
                break
            password = records[row].get('PASSWORD')
            async with aiofiles.open('gsheet_info/accounts.txt', 'a') as f:
                await f.write(f'{username}:{password}\n')

    async def update_sheet(self, url: str, index: int):
        acc_list = dict()
        async with aiofiles.open('results/results.txt', 'r') as f:
            while line := await f.readline():
                info = json.loads(line)
                username = info['username']
                ds_info = ''
                nm_info = ''
                for skin, price in dict(info['default_store']).items():
                    ds_info += f'{skin} : {price}\n'
                for skin, price in dict(info['nightmarket_store']).items():
                    nm_info += f'{skin} : {price}\n'
                acc_list[username] = {'ds_info': ds_info, 'nm_info': nm_info}

        sheet = await self.open_by_url(url)
        worksheet = await sheet.get_worksheet(0)
        not_sold = (await worksheet.findall('FALSE', in_column=4))[:1000]
        cells = list()
        for row in not_sold:
            username = (await worksheet.cell(col=1, row=row.row)).value
            if username == '':
                break
            info = acc_list.get(username)
            if info is None:
                continue
            #nm_inf = info.get('nm_info')
            ds_cell = await worksheet.cell(col=5, row=row.row)
            ds_cell.value = info.get('ds_info')
            cells.append(ds_cell)
            if len(cells) > 20:
                await worksheet.update_cells(cells)
                print('updated cell')
                await asyncio.sleep(2)
                cells.clear()
        if len(cells) > 0:
            await worksheet.update_cells(cells)
            cells.clear()

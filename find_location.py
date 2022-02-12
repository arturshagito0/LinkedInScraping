import gspread
import json
import pandas as pd
import requests
from login import get_credentials
from tqdm import tqdm

csfr, cookies = get_credentials()

headers_location = headers = {
    'authority': 'www.linkedin.com',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    'x-restli-protocol-version': '2.0.0',
    'dnt': '1',
    'x-li-lang': 'en_US',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'x-li-page-instance': 'urn:li:page:d_flagship3_profile_view_base;bHbaEEZiTquzNa6mV60PNg==',
    'accept': 'application/vnd.linkedin.normalized+json+2.1',
    'csrf-token': csfr.replace('"', ''),
    'x-li-track': '{"clientVersion":"1.9.7977","mpVersion":"1.9.7977","osName":"web","timezoneOffset":0,"timezone":"UTC","deviceFormFactor":"DESKTOP","mpName":"voyager-web","displayDensity":1.25,"displayWidth":1920,"displayHeight":1080}',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.linkedin.com/groups/35222/members/',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cookie': f'{cookies}',

    'sec-gpc': '1',
}

regex_loc = "london|\s+uk\s+|united kingdom|great britain|england"

def get_user_location(p_url):
    try:
        response_location = requests.get(f'https://www.linkedin.com/voyager/api/identity/dash/profiles?q=memberIdentity&memberIdentity={p_url}&decorationId=com.linkedin.voyager.dash.deco.identity.profile.FullProfileWithEntities-93', headers=headers_location, timeout=60)
    except Exception as e:
        print(e)
        return ""
    for i in json.loads(response_location.text)['included']:
        for k in i.keys():
            if k == "defaultLocalizedName":
                return i[k]
    return ""

def filter_location(df):
    df.dropna(inplace=True)
    df = df[df['location'].str.contains(regex_loc)]
    return df

def find_locations(table_name, sheet_name, n, filter = True):
    gc = gspread.service_account(filename='creds.json')
    sh = gc.open(table_name)
    worksheet = sh.worksheet(sheet_name)
    data = worksheet.get_all_values()
    headers = data.pop(0)

    
    df = pd.DataFrame(data, columns=headers)
    input(df)
    
    tqdm.pandas()
    df['location'] = df['id'][:n].progress_apply(lambda x: str(get_user_location(x)).lower())
    df = df.fillna("mt")
    if filter: df = filter_location(df); print(f"Location Filtered: {len(df)}")
    if(len(df)>0):
        input("Next...")
        worksheet.clear()
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    else:
        print("There is no leads in this group :(")




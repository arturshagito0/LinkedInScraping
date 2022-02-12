from dataframe_api import create_and_update_worksheet, populate_dataframe, create_new_spreadsheet, update_worksheet
from find_location import find_locations
from login import get_credentials
import json
import numpy as np
import requests
import string
import time
from tqdm import tqdm
from colorama import Fore
import itertools

csfr, cookies = get_credentials()

def get_headers(csfr, cookies):
    headers_users = {
        'authority': 'www.linkedin.com',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'x-restli-protocol-version': '2.0.0',
        'dnt': '1',
        'x-li-lang': 'en_US',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'x-li-page-instance': 'urn:li:page:d_flagship3_groups_members;qDh/9cRsT2S2NOdOp0OiMA==',
        'accept': 'application/vnd.linkedin.normalized+json+2.1',
        'csrf-token': csfr.replace('"', ''),
        'x-li-track': '{"clientVersion":"1.9.8145","mpVersion":"1.9.8145","osName":"web","timezoneOffset":0,"timezone":"UTC","deviceFormFactor":"DESKTOP","mpName":"voyager-web","displayDensity":1.25,"displayWidth":1920,"displayHeight":1080}',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.linkedin.com/groups/40057/members/',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': f'{cookies}'

    }
    return headers_users

global_heads = {
        'authority': 'www.linkedin.com',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'x-restli-protocol-version': '2.0.0',
        'dnt': '1',
        'x-li-lang': 'en_US',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'x-li-page-instance': 'urn:li:page:d_flagship3_groups_members;qDh/9cRsT2S2NOdOp0OiMA==',
        'accept': 'application/vnd.linkedin.normalized+json+2.1',
        'csrf-token': csfr.replace('"', ''),
        'x-li-track': '{"clientVersion":"1.9.8145","mpVersion":"1.9.8145","osName":"web","timezoneOffset":0,"timezone":"UTC","deviceFormFactor":"DESKTOP","mpName":"voyager-web","displayDensity":1.25,"displayWidth":1920,"displayHeight":1080}',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.linkedin.com/groups/40057/members/',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': f'{cookies}'

}

# todo Location, Interface, progress-bar,

COUNT_LENGTH = 100
GROUP_ID = 35222
SAMPLE_FRACTION = 1 #0.001
BLOCK_AUTOMATION = False
SPREADSHEET_NAME = "money_sheet"
WORKSHEET_NAME = "Sheet1"
regex_occ = "\s+ceo\s+|\s+coo\s+|\s+hr\s+|\s+hiring\s+|\s+founder\s+|entrepreneur|\s+talent\s+"


class UserEntry:
    def __init__(self, firstname, lastName, id, occupation):
        self.lastName = lastName
        self.id = id
        self.occupation = occupation
        self.firstname = firstname

    def __eq__(self, other):
        return self.lastName == other.lastName and self.id == other.id


unique_array = np.array([])


def scrape(g_id, heads):
    main_counter = 0
    global unique_array

    headers_users = heads
    keywords = itertools.product(string.ascii_lowercase, repeat = 2)
    keywords = [''.join(elem) for elem in keywords]
    for i in keywords:
        print(f"{keywords.index(i)} out of {len(keywords)}")
        responseNo = 0

        temp_url = f'https://www.linkedin.com/voyager/api/groups/groups/urn%3Ali%3Agroup%3A{g_id}/members?count={COUNT_LENGTH}&filters=List()&membershipStatuses=List(OWNER,MANAGER,MEMBER)&q=typeahead&query={i}&start=0'
        repsonseNo = None
        try:

            responseNo = json.loads(requests.get(temp_url, headers=headers_users, timeout=300).text)['data']['paging']['total']
            # input(responseNo)
        except:
            repsonseNo = 0

        if(repsonseNo == 0):
            continue

        pages = int(responseNo / COUNT_LENGTH + 1)
        pages = pages if pages < 24 else 24
        
        for index in tqdm(range(pages), desc="Looking for users....", colour = 'MAGENTA'):
            main_counter+=1
            time.sleep(0.5)

            p = index * COUNT_LENGTH
            url = f'https://www.linkedin.com/voyager/api/groups/groups/urn%3Ali%3Agroup%3A{g_id}/members?count={COUNT_LENGTH}&filters=List()&membershipStatuses=List(OWNER,MANAGER,MEMBER)&q=typeahead&query={i}&start={p}'
            try:
                response = requests.get(url, headers=headers_users, timeout=300)
                # print(response.status_code)
            except Exception as e:
                print(e)
            # try: 
            #     server_time = response.headers['X-LI-Server-Time']
            #     print(f'X-LI-Server-Time: {server_time}')
            #     new_wait = int(int(server_time)/100)+1
            #     print(f"We'll now wait for: {new_wait}")
            #     time.sleep(new_wait)
            # except Exception:
            #     print("There is no (X-LI-Server-Time)")
            #     print(f"Status Code: {response.status_code}")
            #     time.sleep(5)

           
           

            
            
            # try: elem = response.headers['Expect-CT']; print(f'Expect-CT: {elem}')
            # except Exception: input("There is no (Expect-CT)")
            # try: elem = eval(response.headers['NEL'].replace('true', 'True'))['max_age']; print(f'max_age: {elem}')
            # except Exception: input("There is no (max_age)")
            # try: elem = eval(response.headers['NEL'].replace('true', 'True'))['success_fraction']; print(f'success_fraction: {elem}')
            # except Exception: input("There is no (success_fraction)")
            # try: elem = eval(response.headers['NEL'].replace('true', 'True'))['failure_fraction']; print(f'failure_fraction: {elem}')
            # except Exception: input("There is no (failure_fraction)")

            # input(response.reason)
            json_data = json.loads(response.text)
            # input(json_data)
            # input(len(json_data['included']))

            raw_user_list = json_data['included'][2 * COUNT_LENGTH:]

            # input(raw_user_list)
            # print(len(raw_user_list))
            # check_list = [elem['publicIdentifier'] for elem in raw_user_list]
            # print(len(list(set(check_list))))

            for entry in raw_user_list:
                user = UserEntry(entry['firstName'], entry['lastName'], entry['publicIdentifier'], entry['occupation'])
                if user not in unique_array:
                    unique_array = np.append(unique_array, user)
            
            # if(main_counter % 50 == 0):
            #     time.sleep(120)
            # if(index >= 24):
            #     break

        print(len(unique_array))
        if BLOCK_AUTOMATION:
            ddf = populate_dataframe(unique_array)
            update_worksheet(unique_array.size, ddf, SPREADSHEET_NAME, WORKSHEET_NAME)
            unique_array = np.array([])
        
        # from login import get_credentials
        # csfr, cookies = get_credentials()
        # headers_users = get_headers(csfr, cookies)



ans = int(input("Group No: "))
# ans = 35222
ans2 = 3428054


def filter_occupation(df):
    df.dropna(inplace=True)
    df = df[df['occupation'].str.contains(regex_occ)]
    return df


def main():
    scrape(ans, global_heads)
    if not BLOCK_AUTOMATION:
        ddf = populate_dataframe(unique_array)
        print(f"Original Size: {len(ddf)}")

        filter = input("Filter?")
        filter = False if filter == "" else True

        if(filter): ddf = filter_occupation(ddf); print(f"Filtered Size: {len(ddf)}")
        input("Next...")
        update_worksheet(ddf, SPREADSHEET_NAME, WORKSHEET_NAME)

    # LOCS = input("Do you also need user locations? (y/n): ")
    # if LOCS == 'y':
        # LOCS_NUM = int(input("How many locations do you need? (<1000 recommended): "))
    if(filter):
        LOCS_NUM = len(ddf)
        find_locations(SPREADSHEET_NAME, WORKSHEET_NAME, LOCS_NUM)
    print(f'https://www.linkedin.com/groups/{str(ans)}/members/')


# main()

find_locations(SPREADSHEET_NAME, WORKSHEET_NAME, 107217, filter=False)



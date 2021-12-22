from dataframe_api import create_and_update_worksheet, populate_dataframe, create_new_spreadsheet, update_worksheet
from find_location import find_locations
from login import get_credentials
import json
import numpy as np
import requests
import string
import time

csfr, cookies = get_credentials()



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
    'referer': 'https://www.linkedin.com/groups/35222/members/',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': f'{cookies}'

}

# todo Location, Interface, progress-bar,

COUNT_LENGTH = 100
GROUP_ID = 35222
SAMPLE_FRACTION = 0.0001
BLOCK_AUTOMATION = False
SPREADSHEET_NAME = "TEST_USERS"
WORKSHEET_NAME = "Sheet2"


class UserEntry:
    def __init__(self, firstname, lastName, id, occupation):
        self.lastName = lastName
        self.id = id
        self.occupation = occupation
        self.firstname = firstname

    def __eq__(self, other):
        return self.lastName == other.lastName and self.id == other.id


unique_array = np.array([])


def scrape(g_id):
    global unique_array

    for i in string.ascii_lowercase:

        responseNo = 0

        temp_url = f'https://www.linkedin.com/voyager/api/groups/groups/urn%3Ali%3Agroup%3A{g_id}/members?count={COUNT_LENGTH}&filters=List()&membershipStatuses=List(OWNER,MANAGER,MEMBER)&q=typeahead&query={i}&start=0'

        try:

            responseNo = json.loads(requests.get(temp_url, headers=headers_users).text)['data']['paging'][
                             'total'] * SAMPLE_FRACTION
        except:
            repsonseNo = 0

        for index in range(int(responseNo / 100 + 1)):
            time.sleep(1)

            p = index * 100
            url = f'https://www.linkedin.com/voyager/api/groups/groups/urn%3Ali%3Agroup%3A{g_id}/members?count={COUNT_LENGTH}&filters=List()&membershipStatuses=List(OWNER,MANAGER,MEMBER)&q=typeahead&query={i}&start={p}'

            response = requests.get(url, headers=headers_users)
            json_data = json.loads(response.text)

            raw_user_list = json_data['included'][2 * COUNT_LENGTH:]

            for entry in raw_user_list:
                user = UserEntry(entry['firstName'], entry['lastName'], entry['publicIdentifier'], entry['occupation'])
                if user not in unique_array:
                    unique_array = np.append(unique_array, user)

        if BLOCK_AUTOMATION:
            ddf = populate_dataframe(unique_array)
            update_worksheet(unique_array.size, ddf, SPREADSHEET_NAME, WORKSHEET_NAME)
            unique_array = np.array([])

        print(f"Total users for letter {(i)}: {int(responseNo)}")


ans = int(input("Group No: "))
# ans = 35222
ans2 = 3428054

def main():
    scrape(ans)
    if not BLOCK_AUTOMATION:
        ddf = populate_dataframe(unique_array)
        update_worksheet(ddf, SPREADSHEET_NAME, WORKSHEET_NAME)
    find_locations(SPREADSHEET_NAME, WORKSHEET_NAME, 50)


main()

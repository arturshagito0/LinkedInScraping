import gspread
import numpy as np
import pandas as pd

def create_new_spreadsheet(name):
    gc = gspread.service_account(filename='creds.json')
    sh = gc.create(name)
    sh.share('art_shagi@mail.ru', perm_type='user', role='writer')


def create_and_update_worksheet(df, name, wsname):
    gc = gspread.service_account(filename='creds.json')
    sh = gc.open(name)
    worksheet = sh.add_worksheet(title=f"{wsname}", rows="10000", cols="20")
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())


def update_worksheet(df, name, wsname):
    gc = gspread.service_account(filename='creds.json')
    ws = gc.open(name).worksheet(wsname)
    ws.append_rows(df.values.tolist())


def populate_dataframe(user_list):
    print("Populating dataframe...")
    leads = np.array([])
    for i in user_list:
        leads = np.append(leads, dict(
            zip(['firstname', 'lastname', 'occupation', 'id'], [i.firstname, i.lastName, i.occupation, i.id])))
    df = pd.DataFrame.from_dict(list(leads), orient='columns')
    print(df)
    try:
        df['user_url'] = df['id'].apply(lambda x: f"https://www.linkedin.com/in/{x}")
    except:
        df = pd.DataFrame()
    return df

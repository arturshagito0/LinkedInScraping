from selenium import webdriver
import os
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from dotenv import dotenv_values
import time
from py_utilities.message_in_group import message_user
import requests
import pandas as pd
import re
import time
import pyautogui
import sys

ENV_VAR = dotenv_values(".env")

user = ENV_VAR['GRIG_LINKD_USER']
passw = ENV_VAR['GRIG_LINKD_PASS']
heads = eval(ENV_VAR['SHDB_HEADS'])
saved=False

# driver.get("https://www.linkedin.com/groups/8265998/members")


#FOR DEBUGGING ONLY
# print(driver.command_executor._url)
# print(driver.session_id)


def sign_in(user, passw, url = "https://www.linkedin.com/groups/8265998/members"):
    driver.get(url)
    time.sleep(5)
    try:
        cookies_button = driver.find_element_by_xpath('//*[@id="artdeco-global-alert-container"]/div/section/div/div[2]/button[2]')
        cookies_button.click()
    except Exception:
        pass
    time.sleep(5)
    sign_in_link = driver.find_element_by_xpath('/html/body/div[1]/main/p/a')
    if(sign_in_link):
        sign_in_link.click()
    else:
        input("Couldn't sign in, please sign in manually...")
    time.sleep(5)
    try:
        user_field = driver.find_elements_by_xpath('/html/body/div/main/div[2]/div[1]/form/div[1]/input')[0]
        user_field.send_keys(user)
        passw_field = driver.find_elements_by_xpath('/html/body/div/main/div[2]/div[1]/form/div[2]/input')[0]
        passw_field.send_keys(passw)
        time.sleep(5)
        sign_in_btn = driver.find_elements_by_xpath('//*[@id="organic-div"]/form/div[3]/button')[0]
        sign_in_btn.click()
    except Exception:
        input("Couldn't sign in, please sign in manually...")
    try:
        inside = driver.find_elements_by_xpath('//*[@id="ember48"]/div[1]/h1')
    except Exception:
        input("There was a problem logging in, check the browser window pls...")
        time.sleep(5)

def read_master():
    global master_sheet

    read_url = ENV_VAR['SHDB_READ_URL'].format(ENV_VAR['SHDB_LEADS_ID'])
    x = requests.get(read_url, headers=heads, params={'sheet':master_sheet})
    data = x.text
    data = eval(data)
    df = pd.DataFrame(data)
    df['profile_url'] = df['profile_url'].apply(lambda x: x.replace('\\', ''))
    # df['image_url'] = df['image_url'].apply(lambda x: x.replace('\\', ''))
    df['group_url'] = df['group_url'].apply(lambda x: x.replace('\\', ''))
    # df['about'] = df['about'].apply(lambda x: ' '.join(re.sub('[^0-9a-zA-Z ,]', '', str(x)).split()))
    # df['experience'] = df['experience'].apply(lambda x: ' '.join(re.sub('[^0-9a-zA-Z ,]', '', str(x)).split()))
    df['location'] = df['location'].apply(lambda x: ' '.join(re.sub('[^0-9a-zA-Z ,]', '', str(x)).split()))
    # df['mutual_connections'] = df['mutual_connections'].apply(lambda x: ' '.join(re.sub('[^0-9a-zA-Z ,]', '', str(x)).split()))
    # try:
    #     df=df.drop('Image', axis=1)
    # except Exception:
    #     pass
    
    return df

def read_avoid():
    read_url = ENV_VAR['SHDB_READ_URL'].format(ENV_VAR['SHDB_BLACKLIST_ID'])
    x = requests.get(read_url, headers=heads, params={'sheet':'avoid'})
    data_avoid = x.text
    data_avoid = eval(data_avoid)
    data_avoid = [elem['profile_url'] for elem in data_avoid]
    profiles_avoid = [x.replace('\\', '') for x in data_avoid]
    return profiles_avoid


def send_messages(profiles_avoid):
    global df_master, size, message_requests, direct_message, request_message
    
    #Remove avoid profiles
    df_master = df_master[~df_master['profile_url'].isin(profiles_avoid)]
    gd_size = int(message_requests * size) if len(df_master)>= size else int(message_requests * len(df_master))
    gr_size = size - gd_size if len(df_master)>= size else len(df_master) - gd_size
    
    df_gd = df_master.sample(n=gd_size)
    df_gd['Type'] = ['direct']*len(df_gd)

    #Removing selected profiles from master
    messaged_profiles = list(df_gd['profile_url'].values)
    df_master = df_master[~df_master['profile_url'].isin(messaged_profiles)]

    df_gr = df_master.sample(n=gr_size)
    df_gr['Type'] = ['request']*len(df_gr)

    #Removing selected profiles from master
    messaged_profiles = list(df_gr['profile_url'].values)
    df_master = df_master[~df_master['profile_url'].isin(messaged_profiles)]

    df_sub = pd.concat([df_gd, df_gr], ignore_index=True)
    df_sub = df_sub.sample(frac=1).reset_index().drop('index', axis=1)

    #Send group messages
    unique_groups = list(set(list(df_sub['group_url'].values)))
    outcomes = []
    for g in unique_groups:
        driver.get(g)
        time.sleep(2)
        df_sub_g = df_sub[df_sub['group_url']==g]
        first_names = list(df_sub_g['first_name'].values)
        second_names = list(df_sub_g['second_name'].values)
        profiles = list(df_sub_g['profile_url'].values)
        types = list(df_sub_g['Type'].values)
        search_bar = driver.find_element_by_css_selector("input[class='artdeco-typeahead__input ']")
        for i in range(len(first_names)):
            first_name = first_names[i]
            full_name = first_name + " " + second_names[i]
            full_name = full_name.split(' ')
            print(full_name)
            for n in full_name:
                index = full_name.index(n)
                if('.' in n): n = n.replace(".", "")
                search_bar.send_keys(n)
                if(index!=len(full_name)-1): search_bar.send_keys(' ')        
            
            time.sleep(1)
            profile = profiles[i]
            message_type = types[i]
            print(profile)
            if(message_type=="direct"):
                print("direct")
                message = direct_message.format(first_name)
            else:
                print("request")
                message = request_message.format(first_name)
            time.sleep(1)
            outcome = message_user(profile, message, driver, type=message_type)
            if(outcome != "Success" and outcome != "Failure"):
                df_sub = df_sub[df_sub['profile_url'] != profile]
            time.sleep(5)
            search_bar = driver.find_element_by_css_selector("input[class='artdeco-typeahead__input ']")
            search_bar.clear()
            time.sleep(2)
            outcomes.append(outcome)
    succ_out = outcomes.count("Success")
    print(f"{succ_out} successful direct messages out of {len(outcomes)} attempts")
    input("Move on?...")
    driver.close()

    return df_sub 


def update_db(df_sub, df_master, profiles_avoid):
    sub_profiles = [] if df_sub.empty else list(df_sub['profile_url'].values)
    
    #Deleting old groups master
    delete_url = ENV_VAR['SHDB_DELETE_URL'].format(ENV_VAR['SHDB_LEADS_ID'], master_sheet)
    x = requests.delete(delete_url)
    print(x)
    #deleting old avoid profiles
    delete_url = ENV_VAR['SHDB_DELETE_URL'].format(ENV_VAR['SHDB_BLACKLIST_ID'], 'avoid')
    x = requests.delete(delete_url)
    print(x)

    #Removing general request and part-time proposal profiles from master (group message profiles
    # have already been removed)
    data_out = df_master.to_dict('records')
    data_out = str(data_out).replace("'", '"')
    out = '{"json":'+ data_out +'}'

    #Updating groups master
    send_url = ENV_VAR['SHDB_SEND_URL'].format(ENV_VAR['SHDB_LEADS_ID'])
    x = requests.post(send_url, data = out, headers=heads, params={'sheet':master_sheet})
    print(x)

    #Adding selected profiles to avoid profiles
    profiles_avoid = profiles_avoid + sub_profiles
    profiles_avoid = list(set(profiles_avoid))
    columns = ['profile_url']*len(profiles_avoid)
    out = [{avoid[0]:avoid[1]} for avoid in list(zip(columns, profiles_avoid))]
    out = str(out).replace("'", '"')
    out = '{"json":'+ out +'}'
    
    #Updating avoid profiles in blacklist
    send_url = ENV_VAR['SHDB_SEND_URL'].format(ENV_VAR['SHDB_BLACKLIST_ID'])
    x = requests.post(send_url, data = out, headers=heads, params={'sheet':'avoid'})
    print(x)

    return "Done"
    

chromedriver = '/Users/grigorijmordkovic/Desktop/linkedin_automation/py_utilities/chromedriver'
# os.chdir('/Users/grigorijmordkovic/Desktop/linkedin_automation')
driver = webdriver.Chrome(chromedriver)
sign_in(user, passw)
master_sheet = input("enter the name of the master sheet you want to process\n") if(len(sys.argv)<2) else sys.argv[1]

df_master = read_master()
input(df_master)
profiles_avoid = read_avoid()


direct_message=input("Which direct message do you use?\n") if(len(sys.argv)<3) else sys.argv[2]
request_message=input("Which request message do you use?\n") if(len(sys.argv)<4) else sys.argv[3]
size=int(input('Choose how many requests you want to send\n')) if(len(sys.argv)<5) else int(sys.argv[4])
message_requests=float(input('Which proportion as message requests?\n')) if(len(sys.argv)<6) else int(sys.argv[5])


df_sub = send_messages(profiles_avoid)
update_db(df_sub, df_master, profiles_avoid)

    


    
    
    




import time
import re
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

emoji_dic = {'rocket': '\🚀', 'tree': '\🎄', 'smile': '\😀'}

def process_direct_message(text, driver):
    regex = ":[A-Za-z]+[0-9]*:"
    regex_n = "[0-9]*"
    text_area = driver.find_element_by_css_selector("div[class='msg-form__msg-content-container--scrollable scrollable relative']").find_element_by_css_selector("div[class='flex-grow-1']").find_elements_by_tag_name('div')[0].find_elements_by_tag_name('p')[0]
    text_area.send_keys(text)
    paragraphs = driver.find_element_by_css_selector("div[class='msg-form__msg-content-container--scrollable scrollable relative']").find_element_by_css_selector("div[class='flex-grow-1']").find_elements_by_tag_name('div')[0].find_elements_by_tag_name('p')
    # print(len(paragraphs))
    for p in paragraphs:
        # print("A")
        p_text = driver.execute_script("return arguments[0].innerHTML", p)
        # print(p)
        # print("B")
        emojis = re.findall(regex, p_text)
        # print(emojis)
        if emojis:
            # print("Here")
            for emo in emojis:
                number =[elem for elem in re.findall(regex_n, emo) if elem != '']
                # print(number)
                if(number):
                    # print("There")
                    number = number[0]
                    emo_repeated = (emoji_dic[emo.replace(number, '').replace(':', '')])*int(number)
                    print(emo)
                    print(emo_repeated)
                    driver.execute_script("arguments[0].innerHTML = arguments[0].innerHTML.replace('{}', '{}')".format(emo, emo_repeated),p)
                else:
                    # print("Hello")
                    # print(p)
                    print(emo)
                    print(emoji_dic[emo.replace(':', '')])
                    driver.execute_script("arguments[0].innerHTML = arguments[0].innerHTML.replace('{}', '{}')".format(emo, emoji_dic[emo.replace(':', '')]),p)
        else:
            continue
        
    text_area = driver.find_element_by_css_selector("div[class='msg-form__msg-content-container--scrollable scrollable relative']").find_element_by_css_selector("div[class='flex-grow-1']").find_elements_by_tag_name('div')[0].find_elements_by_tag_name('p')[0]
    text_area.send_keys('a')
    text_area.send_keys(Keys.BACKSPACE)


def process_request_message(text, driver):
    text_area = driver.find_element_by_css_selector("textarea[class='ember-text-area ember-view connect-button-send-invite__custom-message mb3']")
    regex = ":[A-Za-z]+[0-9]*:"
    regex_n = "[0-9]*"
    text_area.send_keys(text)
    p_text = driver.execute_script("return arguments[0].value", text_area)
    # print(p_text)
    emojis = re.findall(regex, p_text)
    # print(emojis)
    if (emojis):
        for emo in emojis:
            number =[elem for elem in re.findall(regex_n, emo) if elem != '']
            # print(number)
            if(number):
                number = number[0]
                emo_repeated = (emoji_dic[emo.replace(number, '').replace(':', '')])*int(number)
                print(emo)
                print(emo_repeated)
                driver.execute_script("arguments[0].value = arguments[0].value.replace('{}', '{}')".format(emo, emo_repeated), text_area)
            else:
                print(emo)
                print(emoji_dic[emo.replace(':', '')])
                driver.execute_script("arguments[0].value = arguments[0].value.replace('{}', '{}')".format(emo, emoji_dic[emo.replace(':', '')]), text_area)


def message_user(profile_url, text, driver, type='direct'):
    url_href = profile_url.replace("https://www.linkedin.com", '')
    if(url_href[len(url_href)-1]!='/'): url_href = url_href + '/'
    print(url_href)
    driver.execute_script(f"guy = document.querySelector(\"a[href='{url_href}']\");")
    time.sleep(1)
    print("A")
    #Find the right guy?
    confirm = driver.execute_script("return guy")
    if(confirm or type=="simple_request"):
        if(type =='direct'):
            driver.execute_script("message_button = guy.parentElement.querySelector(\"button[class='message-anywhere-button artdeco-button artdeco-button--secondary artdeco-button--2']\");")
            time.sleep(0.5)
            driver.execute_script("message_button.click();")
            time.sleep(1)
            try:
                # text_area = driver.find_element_by_css_selector("div[class='msg-form__msg-content-container--scrollable scrollable relative']").find_element_by_css_selector("div[class='flex-grow-1']").find_elements_by_tag_name('div')[0].find_elements_by_tag_name('p')[0]
                text = text.strip()
                text = text.replace('\n \n', '\n\n')
                text = text.split('\n\n')
                text = [elem.strip() for elem in text]
                text = [[elem, "\n\n"] for elem in text]
                text = [item for sublist in text for item in sublist]
                print(text)
                process_direct_message(text, driver)
                time.sleep(2)
                send_button = driver.find_element_by_css_selector("button[class='msg-form__send-button artdeco-button artdeco-button--1']")
                send_button.submit()
                time.sleep(2)
                connect_button = driver.find_element_by_css_selector("button[class='msg-nonconnection-banner__connect-btn artdeco-button artdeco-button--circle artdeco-button--1 artdeco-button--secondary ember-view']")
                connect_button.click()
                time.sleep(1)
                #close the message tab after sending
                driver.execute_script("document.querySelector(\"button[class='msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view']\").click()")
            except Exception:
                return "Failure"
            return "Success"
        else:
            print("B")
            if(type!="simple_request"):
                driver.execute_script("guy.click();")
                time.sleep(3)
            try:
                #i.e. type is connection request
                print("C")
                # connect_button = False
                try:
                    time.sleep(1)
                    connect_button = driver.find_element_by_css_selector("button[class='artdeco-button artdeco-button--2 artdeco-button--primary ember-view pvs-profile-actions__action']")
                    # driver.execute_script("connect_btn = document.querySelector(\"button[class='artdeco-button artdeco-button--2 artdeco-button--primary ember-view pvs-profile-actions__action']\");")
                    # connect_btn = driver.execute_script("return connect_btn")
                except Exception:
                    connect_button = False
                #Method 1
                if(connect_button):
                    print('D')
                    connect_button.click()
                    # driver.sleep(1)
                    # driver.execute_script("connect_btn.click();")
                    time.sleep(2)
                #Method 2
                else:
                    print("E")
                    driver.execute_script("window.scrollTo(0,200)")
                    time.sleep(1)
                    more_button = driver.find_elements_by_css_selector("button[aria-label='More actions']")
                    try:
                        elements_num = len(more_button) 
                        more_button = more_button[len(more_button)-1]
                    except Exception:
                        more_button = more_button[0]
                    more_button.click()
                    time.sleep(0.1)
                    driver.execute_script("connect_btn=document.querySelectorAll(\"li-icon[type='connect-icon']\")[1].parentElement;")
                    # connect_link = driver.find_elements_by_css_selector("li-icon[type='connect-icon']")[1]
                    time.sleep(0.1)
                    driver.execute_script("connect_btn.click();")
                    # ActionChains(driver).move_to_element(connect_link).click(connect_link).perform()
                    time.sleep(2)
                    try:
                        connect_button = driver.find_element_by_css_selector("button[class='mr2 artdeco-button artdeco-button--muted artdeco-button--2 artdeco-button--secondary ember-view']")
                    except Exception:
                        connect_button = driver.find_element_by_css_selector("button[class='artdeco-button artdeco-button--muted artdeco-button--2 artdeco-button--secondary ember-view mr2']")
                    time.sleep(1)
                    connect_button.click()
                    time.sleep(2)
                    
                note_button = driver.find_element_by_css_selector("button[aria-label='Add a note']")
                note_button.click()
                time.sleep(2)
                process_request_message(text, driver)
                time.sleep(2)
                send_button = driver.find_element_by_css_selector("button[aria-label='Send now']")
                send_button.click()
                time.sleep(4)
                print("F")
                driver.execute_script("window.history.go(-1);")
                time.sleep(5)
            except Exception as e:
                print(e)
                return "Failure"
            return "Success"
    else:
        print(f"Unforunately couldn't find record for {profile_url} in this group, skipping...")
        return profile_url
    

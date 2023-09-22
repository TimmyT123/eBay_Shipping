from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from collections import Counter
from selenium.webdriver.common.action_chains import ActionChains
from tkinter import *
import os
import re
import time


def setup():
    global driver1
    driver1 = webdriver.Chrome()

    driver1.get('https://www.ebay.com/')
    time.sleep(2)

    # driver1.set_window_size(3840, 2160)
    driver1.set_window_position(-1500, -700)

    driver1.maximize_window()

    # Click on sign in
    try:
        driver1.find_element("xpath", '//*[@id="gh-ug"]/a').click()
    except:
        # If an error happens when loading a refresh page usually will fix it
        driver1.refresh()
        time.sleep(3)
        driver1.find_element("xpath", '//*[@id="gh-ug"]/a').click()

    timeout = 40  # verification puzzles might pop up
    try:
        element_present = EC.visibility_of_element_located((By.ID, 'userid'))
        WebDriverWait(driver1, timeout).until(element_present)
    except TimeoutException:
        print("Timed out waiting for the page to load")

    time.sleep(.5)
    
    driver1.find_element("xpath", '//*[@id="userid"]').send_keys(os.environ.get('My_eBay_username'))
    driver1.find_element("xpath", '//*[@id="signin-continue-btn"]').click()

    #time.sleep(2)
    # input('When ready, press enter for password....please')

    timeout = 40  # security puzzle may pop up here
    try:
        element_present = EC.visibility_of_element_located((By.ID, 'pass'))
        WebDriverWait(driver1, timeout).until(element_present)
    except TimeoutException:
        print("Timed out waiting for the page to load")

    driver1.find_element("xpath", '//*[@id="pass"]').send_keys(os.environ.get('My_eBay_password'))
    driver1.find_element("xpath", '//*[@id="sgnBt"]').click()

    timeout = 40  # verification puzzle may pop up
    tot_time = 0
    time1 = time.perf_counter()
    try:
        element_present = EC.visibility_of_element_located((By.ID, 'continue-wrapper'))
        WebDriverWait(driver1, timeout).until(element_present)

    except TimeoutException:
        #print("Timed out waiting for the page to load")
        return driver1  # continue-wrapper does not popup so we can return
    time2 = time.perf_counter()
    tot_time = int(time2 - time1)
    # print(f'total time = {tot_time}')
    if tot_time < 5:  # if tot_time is less than 5 then press continue button
        driver1.find_element("xpath", '//*[@id="continue-wrapper"]').click()
    return driver1

def my_tkinter_window(my_statement):
    # Open tkinter window
    window = Tk()
    window.title("eBay Shipping")
    window.minsize(width=800, height=400)
    my_label = Label(text=my_statement)
    my_label.pack()
    exitButton = Button(window, text="click to exit", command=window.destroy)
    exitButton.pack()
    window.mainloop()


def check_messages():
    driver1.get('https://mesg.ebay.com/mesgweb/ViewMessages/0')
    my_tkinter_window('IS THERE ANY CANCELLED ORDERS IN THE MESSAGES?')


# move to TEXT
def move_to(text):
    element = driver1.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
    desired_y = (element.size['height'] / 2) + element.location['y']
    window_h = driver1.execute_script('return window.innerHeight')
    window_y = driver1.execute_script('return window.pageYOffset')
    current_y = (window_h / 2) + window_y
    scroll_y_by = desired_y - current_y
    driver1. execute_script("window.scrollBy(0, arguments[0]);", scroll_y_by)
    time.sleep(.5)


def press_print(mail_ship_rate):
    #  match mail_ship_rate with ship_rate_pop_up to make sure they equal and then click on print
    result_ship = re.search(r'.*FLATRATE-([A-Z]+)_([A-Z]+)', mail_ship_rate).groups()
    ship_rate_pop_up = driver1.find_element(By.CSS_SELECTOR, "#sticky_breakpoint > div > section > div > div.bHHlHzB3jev8rUf0aAO4 > div:nth-child(1) > div.CSf7GSC1oCSqyo9ANmTM").text
    if result_ship[0].upper() in ship_rate_pop_up.upper() and result_ship[1] in ship_rate_pop_up.upper():
        #  print(f'{result_ship[0]} and {result_ship[1]} is in {ship_rate_pop_up}')
        # Click on the first 'Print Label'
        driver1.find_element(By.CSS_SELECTOR, '#sticky_breakpoint > div > section > div > div.qjeKQ7eZzKAGTDD5Wx7g > button').click()
        time.sleep(12)

        # print(f'all windows opened are {driver1.window_handles}')

        driver1.switch_to.window(driver1.window_handles[-1])
        try:
            print1 = driver1.execute_script(
                "return document.querySelector('print-preview-app').shadowRoot.querySelector('print-preview-sidebar#sidebar').shadowRoot.querySelector('print-preview-button-strip').shadowRoot.querySelector('div.controls').querySelector('cr-button.action-button')")
            print1.click()
        except:
            driver1.switch_to.window(driver1.window_handles[0])
            input('There has been a print error with the second window.\n'
                  'Did you print it and now you want to continue to next item?')

        driver1.switch_to.window(driver1.window_handles[0])

    # input('we are at press print')


def main(main_window):

    driver1.get('https://www.ebay.com/sh/ord/?filter=status%3AAWAITING_SHIPMENT&sort=paiddate')

    timeout = 5  # presence_of_element_located((By.ID, 'pass'))
    try:
        element_present = EC.visibility_of_element_located((By.ID, 'mod-main-cntr'))
        WebDriverWait(driver1, timeout).until(element_present)
    except TimeoutException:
        print("Timed out waiting for the page to load")

    table = driver1.find_element("xpath", '//*[@id="mod-main-cntr"]/table/tbody')
    trs = table.find_elements("xpath", 'tr')

    item_amounts = driver1.find_elements(By.CSS_SELECTOR, "tr td div p strong")
    my_next_item_amount = iter(item_amounts)

    # CHECK IF MORE THAN ONE WAS ORDERED LOOP
    for tr in trs:
        tds = tr.find_elements("xpath", 'td')

        td_text_re_hold = ''
        for tdnum, td in enumerate(tds):
            td_text = td.text
            td_text_re = re.search(r'.*(\d{2}-\d{5}-\d{5})', td_text)
            if td_text_re:
                td_text_re_hold = td_text_re.group(1)  # Save the order number
            # print(tdnum, td.text)
            # print()
            if tdnum == 3 and 'available' in td.text:
                # td_text = td.text
                item_amount = next(my_next_item_amount).text
                # print(item_amount)
                if item_amount == '500':
                    min_avail = 14
                elif item_amount == '1000':
                    min_avail = 10
                else:
                    min_avail = 6

                amount = int(td.text[0])
                available = int(td.text[2:4])
                if available < min_avail:
                    my_tkinter_window(f'WE NEED TO REPLENISH {item_amount} BECAUSE WE HAVE {available} AVAILABLE')
                    quit()
                if amount > 1:
                    # Make it go to the item in the website
                    driver1.get(f'https://www.ebay.com/sh/ord/?filter=status%3AAWAITING_SHIPMENT&search=ordernumber%3A{td_text_re_hold}')
                    my_tkinter_window(f"We don't need to replenish, but\nWE NEED TO SEND {amount} IN A PACKAGE")
                    quit()


    # input('stop and check')

    # GET ITEM NAMES AND AMOUNTS
    item_names = driver1.find_elements(By.CSS_SELECTOR, "tr td div p .item-title")
    item_amounts = driver1.find_elements(By.CSS_SELECTOR, "tr td div p strong")

    ebay_link_list = []
    item_label_link = driver1.find_elements(By.CSS_SELECTOR, "tr td div .order-line-actions [href]")
    for e_item in item_label_link:
        ebay_link = (re.findall(r'https\:\/\/www\.ebay\.com\/lbr\/go\?t=\d{12}-\d{13}', e_item.get_attribute('href')))
        if len(ebay_link) == 0:
            continue
        else:
            ebay_link_list.append(ebay_link)

    inventory = []
    items = {}
    for n in range(len(item_names)):
        inventory.append(item_amounts[n].text)  # count how many of the same amounts
        items[n] = {
            "item": item_names[n].text,
            "amount": item_amounts[n].text,
            "link": ebay_link_list[n],
        }
    #  print(items) # prints (in dictionary) -> item, amount, link

    # sort by the amount
    new_items_dict = sorted(items.items(), key=lambda item: item[1].get('amount'), reverse=True)
    print(new_items_dict)

    # Count the values in amount and display for inventory ex. '500': 10   '1000': 4   '5000': 2
    my_tkinter_window(Counter(inventory))


    print('\n\n\n')
    for i, it in enumerate(new_items_dict):
        #print(f'{len(new_items_dict)-i} - {it}')
        driver1.get(''.join(it[1].get('link')))

        # timeout = 5  # verification puzzles might pop up
        # try:
        #     element_present = EC.visibility_of_element_located((By.CSS_SELECTOR, 'tr td button .fake-link'))
        #     WebDriverWait(driver1, timeout).until(element_present)
        # except TimeoutException:
        #     print("Timed out waiting for the page to load")

        print()

        test1 = it[1].get('amount')

        pp = False  # press print initial as False

        if test1 != '500':  # Let's skip 500 for now
            time.sleep(5)

            # Move to click on expand
            driver1.execute_script("window.scrollTo(0,700);")
            time.sleep(1)
            # click on expand
            driver1.find_element(By.XPATH, '//*[@id="webapp"]/main/div/section[2]/fieldset/table/tfoot/tr/td/button').click()
            time.sleep(1)

            mail = ''
            mail_id = ''
            if test1 == '1000':
                mail = 'USPS Priority Mail Flat Rate Small Box'
                # mail_id = 'USPS-STANDARD_FLATRATE-SMALL_BOX-DROP_OFF'
                pp = True
            elif test1 == '2000':
                mail = 'USPS Priority Mail Flat Rate Padded Envelope'
                # mail_id = 'USPS-STANDARD_FLATRATE-PADDED_ENVELOPE-DROP_OFF'
                pp = True
            elif test1 == '5000':
                mail = 'USPS Priority Mail Flat Rate Medium Box'
                # mail_id = 'USPS-STANDARD_FLATRATE-MEDIUM_BOX-DROP_OFF'
                pp = True
            if mail:  # CLICK ON RADIO BUTTON OF mail CHOICE
                move_to(mail)

                time.sleep(.5)
                # Click on radio button using XPATH with mail
                driver1.find_element(By.XPATH, f"//*[contains(text(), '{mail}')]").click()
                # Clicking on radio button using CSS_SELECTOR and id
                # driver1.find_element(By.CSS_SELECTOR, f"input[type='radio'][id={mail_id}]").click()
                time.sleep(.5)

            driver1.execute_script("window.scrollTo(0,100);")  # MOVE SCREEN BACK TO ORIGINAL POSITION

            if pp:
                press_print(mail)

            my_tkinter_window(f'{len(new_items_dict)-i}\n{it}')



    # # ORDERING LOOP
    # for tr in trs:
    #     print("new one?")
    #     tds = tr.find_elements("xpath", 'td')
    #     for tdnum, td in enumerate(tds):
    #
    #         print(tdnum, td.text)
    #         print()

    # Get last items like the 500 amount
    driver1.get('https://www.ebay.com/sh/ord/?filter=status%3AAWAITING_SHIPMENT&sort=paiddate')
    # TODO get the last item 500 amount
    table = driver1.find_element("xpath", '//*[@id="mod-main-cntr"]/table/tbody')
    trs = table.find_elements("xpath", 'tr')
    for tr in trs:
        tds = tr.find_elements("xpath", 'td')

        td_text_re_hold = ''
        for tdnum, td in enumerate(tds):
            td_text = td.text
            print(tdnum, td_text)

    input('wait for a key')
            # if tdnum == 1 and 'Purchase shipping label' in td.text:
            #     print(td.text)
            #
            #     input('\nfind shipping label')  #TODO find css_selector
            #
            #     # Press 'Print shipping label'
            #     td.find_element("css_selector", 'span.default-action.fake-link').click()
            #
            #     input('temp stay')


if __name__ == "__main__":
    driver1 = setup()
    check_messages()
    main_window = driver1.current_window_handle
    main(main_window)
    quit()


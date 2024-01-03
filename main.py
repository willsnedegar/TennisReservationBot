import pause
import pytz
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tempfile import mkdtemp
import time

def handler(event, context):
    options = webdriver.ChromeOptions()
    service = webdriver.ChromeService("/opt/chromedriver")

    options.binary_location = '/opt/chrome/chrome'
    options.add_argument("--headless=new")
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(options=options, service=service)
    driver.get("https://app.courtreserve.com/Online/Account/login/3683?returnUrl=%252fOnline%252fReservations%252fIndex%252f3683")
    driver.implicitly_wait(2)

    login(driver, event.get('username'), event.get('password'))
    open_form(driver, event.get('time_index'), event.get('same_day'))
    populate_form(driver, event.get('reservation_name'), event.get('partner_first_name'), event.get('partner_last_name'), event.get('is_guest'))
    submit_form(driver, event.get('same_day'), int(event.get('time_index')))

    print("Submitted; going to sleep for a sec")
    time.sleep(10)

    return {
        "statusCode": 200,
        "body": "Be rootin', be tootin', and by God be shootin'; but most of all, be kind"
    }

def login(driver, username, password):
    username_input = driver.find_element(By.ID, "UserNameOrEmail")
    username_input.send_keys(username)

    password_input = driver.find_element(By.ID, "Password")
    password_input.send_keys(password)

    login_button = driver.find_element(By.XPATH, '//*[@id="loginForm"]/button')
    login_button.click()

def open_form(driver, time_index, same_day):
    if not same_day:
        increment_day_button = driver.find_element(By.XPATH, '//*[@id="CourtsScheduler"]/div/span[1]/button[3]')
        for _ in range(7):
            increment_day_button.click()

    time.sleep(2)
    for court_num in [1, 2, 0]:
        try:
            court_button = driver.find_element(By.XPATH, '//*[@id="CourtsScheduler"]/table/tbody/tr[2]/td[2]/div/table/tbody/tr[{}]/td[{}]/span/button'.format(time_index, court_num + 2))
            court_button.click()
            break
        except Exception as e:
            print(e)
            continue

def populate_form(driver, reservation_name, partner_first_name, partner_last_name, is_guest):
    if reservation_name:
        select_reservation_name(driver, reservation_name)
    select_singles(driver)
    if is_guest:
        add_guest(driver, partner_first_name, partner_last_name)
    else:
        add_member(driver, partner_first_name, partner_last_name)

def select_reservation_name(driver, reservation_name):
    reserve_for_dropdown = driver.find_element(By.XPATH, '//*[@id="reservation-general-info"]/div/div[1]/div/div/span')
    time.sleep(0.5)
    reserve_for_dropdown.send_keys(reservation_name)
    reserve_for_dropdown.send_keys(Keys.ENTER)


def select_singles(driver):
    reservation_dropdown = driver.find_element(By.XPATH, '//*[@id="reservation-general-info"]/div/div[2]/div/div/span')
    reservation_dropdown.click()

    time.sleep(0.5)
    singles_option = driver.find_element(By.XPATH, '//*[@id="ReservationTypeId_listbox"]/li[1]')
    singles_option.click()

def add_guest(driver, first_name, last_name):
    num_guests_span = driver.find_element(By.XPATH, '//*[@id="guestsDiv"]/div/span')
    num_guests_span.click()
    time.sleep(0.5)
    num_guests_span.send_keys(1)
    num_guests_span.send_keys(Keys.ENTER)

    time.sleep(2)
    guest_first_name_input = driver.find_element(By.XPATH, '//*[@id="ReservationGuests_0__FirstName"]')
    guest_first_name_input.send_keys(first_name)

    guest_last_name_input = driver.find_element(By.XPATH, '//*[@id="ReservationGuests_0__LastName"]')
    guest_last_name_input.send_keys(last_name)

def add_member(driver, first_name, last_name):
    additional_players_input = driver.find_element(By.XPATH, '//*[@id="tglAllowMemberToPickOtherMembersToPlayWith"]/div/div/span/input[1]')
    additional_players_input.send_keys(first_name + " " + last_name)

    time.sleep(1)
    players_first_option = driver.find_element(By.XPATH, '//*[@id="OwnersDropdown_listbox"]/li/span')
    players_first_option.click()

def submit_form(driver, same_day, time_index):
    submit_button = driver.find_element(By.XPATH, '//*[@id="createReservation-Form"]/div[3]/div/button[2]')
    time.sleep(1)

    if not same_day:
        total_min_into_day = (time_index - 1) * 90 + 30
        hour = total_min_into_day // 60
        minutes = total_min_into_day % 60

        pacific_time_zone = pytz.timezone("US/Pacific")
        today = datetime.now(pacific_time_zone)
        target_time = pacific_time_zone.localize(datetime(today.year, today.month, today.day, hour, minutes))
        print(today)
        print(target_time)
        pause.until(target_time)

    submit_button.click()


# if __name__ == "__main__":
#     handler({
#         "username": "czlzred@gmail.com",
#         "password": "XPC@hug_cfz9amk@qdf",
#         "time_index": "15",
#         "reservation_name": "Martin Tak",
#         "partner_first_name": "Will",
#         "partner_last_name": "Snedegar",
#         "is_guest": True,
#     }, "")

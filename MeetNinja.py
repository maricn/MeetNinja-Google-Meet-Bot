#!/usr/bin/env python3

from selenium import webdriver; import requests
from selenium.webdriver.remote.utils import dump_json
from selenium.webdriver.support import expected_conditions as when
from selenium.webdriver.common.by import By as by
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
import pause; import os; import re
import time; from datetime import datetime
import colorama; from termcolor import colored
from googleapiclient.discovery import build

colorama.init()

###################################################################
#                        Meets                  HH:MM:SS DD/MM/YYYY
# MEETS = {"1 https://meet.google.com/fdb-ftby-qmc": "2021-04-29T22:45:00+02:00",
         # "2 https://meet.google.com/meetURL2": "23:59:59 31/12/2020",
         # "3 https://meet.google.com/meetURL3": "23:59:59 31/12/2020",
         # "4 https://meet.google.com/meetURL4": "23:59:59 31/12/2020",
         # Add more Meet URLs (if any) using the same format as above
         # }

DURATION_MINS = 60 # Duration of each Meet in minutes
USERNAME = "emailaddress@gmail.com"
PASSWORD = "passw0rd"
BROWSER_DRIVER = "Browser Driver Path Goes Here (options below)"

#                   Google Chrome
#           Linux: "ChromeDrivers/linux64/chromedriver"
#             Mac: "ChromeDrivers/mac64/chromedriver"
#        Mac (M1): "ChromeDrivers/mac64_m1/chromedriver"
#         Windows: "ChromeDrivers/win32/chromedriver.exe"

#                   Mozilla Firefox
#     Linux (x32): "FirefoxDrivers/linux32/geckodriver"
#     Linux (x64): "FirefoxDrivers/linux64/geckodriver"
#             Mac: "FirefoxDrivers/mac64/geckodriver"
#   Windows (x32): "FirefoxDrivers/win32/geckodriver.exe"
#   Windows (x64): "FirefoxDrivers/win64/geckodriver.exe"
##################################################################

# All required interactive elements' locators (text fields, buttons, etc.)
usernameFieldPath = "identifierId"
usernameNextButtonPath = "identifierNext"
passwordFieldPath = "password"
passwordNextButtonPath = "passwordNext"
joinButton1Path = "//span[contains(text(), 'Join')]"
joinButton2Path = "//span[contains(text(), 'Ask to join')]"
endButtonPath = "[aria-label='Leave call']"

currentVersionNumber = "v3.1.1"
VERSION_CHECK_URL = "https://raw.githubusercontent.com/SHUR1K-N/MeetNinja-Google-Meet-Bot/master/versionfile.txt"
BANNER1 = colored('''
   ███▄ ▄███▓▓█████ ▓█████▄▄▄█████▓ ███▄    █  ██▓ ███▄    █  ▄▄▄██▀▀▀▄▄▄
  ▓██▒▀█▀ ██▒▓█   ▀ ▓█   ▀▓  ██▒ ▓▒ ██ ▀█   █ ▓██▒ ██ ▀█   █    ▒██  ▒████▄
  ▓██    ▓██░▒███   ▒███  ▒ ▓██░ ▒░▓██  ▀█ ██▒▒██▒▓██  ▀█ ██▒   ░██  ▒██  ▀█▄
  ▒██    ▒██ ▒▓█  ▄ ▒▓█  ▄░ ▓██▓ ░ ▓██▒  ▐▌██▒░██░▓██▒  ▐▌██▒▓██▄██▓ ░██▄▄▄▄██
  ▒██▒   ░██▒░▒████▒░▒████▒ ▒██▒ ░ ▒██░   ▓██░░██░▒██░   ▓██░ ▓███▒   ▓█   ▓██▒
  ░ ▒░   ░  ░░░ ▒░ ░░░ ▒░ ░ ▒ ░░   ░ ▒░   ▒ ▒ ░▓  ░ ▒░   ▒ ▒  ▒▓▒▒░   ▒▒   ▓▒█░
  ░  ░      ░ ░ ░  ░ ░ ░  ░   ░    ░ ░░   ░ ▒░ ▒ ░░ ░░   ░ ▒░ ▒ ░▒░    ▒   ▒▒ ░
  ░      ░      ░      ░    ░         ░   ░ ░  ▒ ░   ░   ░ ░  ░ ░ ░    ░   ▒
         ░      ░  ░   ░  ░                 ░  ░           ░  ░   ░        ░  ░''', 'blue')
BANNER2 = colored('''                    ------------------------------------''', 'blue')
BANNER3 = colored('''                    || MeetNinja: The Google Meet Bot ||''', 'red')
BANNER4 = colored('''                    ------------------------------------''', 'blue')


def printBanner():
    print(BANNER1), print(BANNER2), print(BANNER3), print(BANNER4)


def versionCheck():
    global currentVersionNumber

    print("\nChecking for MeetNinja updates...", end="")

    crawlVersionFile = requests.get(VERSION_CHECK_URL)
    crawlVersionFile = str(crawlVersionFile.content)
    crawlVersionFile = re.findall(r"([0-9]+)", crawlVersionFile)
    latestVersionNumber = int(''.join(crawlVersionFile))

    currentVersionNumber = re.findall(r"([0-9]+)", currentVersionNumber)
    currentVersionNumber = int(''.join(currentVersionNumber))

    if currentVersionNumber >= latestVersionNumber:
        print(colored(" You are using the latest version!\n", "green"))
    elif currentVersionNumber < latestVersionNumber:
        print(colored(" You are using an older version of MeetNinja.", "red"))
        print(colored("\nGet the latest version at https://github.com/SHUR1K-N/MeetNinja-Google-Meet-Bot", "yellow"))
        print(colored("Every new version comes with fixes, improvements, new features, etc..", "yellow"))
        print(colored("Please do not open an Issue if you see this message and have not yet tried the latest version.", "yellow"))


def fixTimeFormat(rawTime):
    rawTime = list(rawTime.split())
    times = list(map(int, rawTime[0].split(":")))
    dates = list(map(int, reversed(rawTime[1].split("/"))))
    startTime = dates + times
    return startTime


def timeStamp():
    timeNow = str(datetime.now())
    timeRegEx = re.findall(r"([0-9]+:[0-9]+:[0-9]+)", timeNow)
    return(timeRegEx[0])


def initBrowser():
    print("\nInitializing browser...", end="")
    if BROWSER_DRIVER.lower().startswith("chrom"):
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument("--disable-infobars")
        chromeOptions.add_argument("--disable-gpu")
        chromeOptions.add_argument("--disable-extensions")
        chromeOptions.add_argument("--window-size=800,800")
        # chromeOptions.add_argument("--incognito")
        chromeOptions.add_argument("--disable-blink-features=AutomationControlled")
        chromeOptions.add_argument("user-data-dir=./profile/")
        chromeOptions.add_experimental_option('excludeSwitches', ['enable-logging'])
        chromeOptions.add_experimental_option("prefs", {"profile.default_content_setting_values.media_stream_mic": 2,
                                                        "profile.default_content_setting_values.media_stream_camera": 2,
                                                        "profile.default_content_setting_values.notifications": 2
                                                        })
        if BROWSER_DRIVER.lower().endswith(".exe"):
            driver = webdriver.Chrome(executable_path=BROWSER_DRIVER, options=chromeOptions)
        else:
            servicePath = Service(BROWSER_DRIVER)
            driver = webdriver.Chrome(service=servicePath, options=chromeOptions)

    elif (BROWSER_DRIVER.lower().startswith("firefox") or BROWSER_DRIVER.lower().startswith("gecko")):
        firefoxOptions = webdriver.FirefoxOptions()
        firefoxOptions.add_argument("--width=800"), firefoxOptions.add_argument("--height=800")
        # firefoxOptions.headless = True
        firefoxOptions.set_preference("layers.acceleration.disabled", True)
        firefoxOptions.set_preference("browser.privatebrowsing.autostart", True)
        firefoxOptions.set_preference("permissions.default.microphone", 2)
        firefoxOptions.set_preference("permissions.default.camera", 2)
        if BROWSER_DRIVER.lower().endswith(".exe"):
            driver = webdriver.Firefox(executable_path=BROWSER_DRIVER, options=firefoxOptions)
        else:
            servicePath = Service(BROWSER_DRIVER)
            driver = webdriver.Firefox(service=servicePath, options=firefoxOptions)
    print(colored(" Success!", "green"))
    return(driver)


def getMeetings(since: datetime):
    calendarService = build('calendar', 'v3', client_options={ 'credentials_file': '/home/nikola/.google-credentials.json' })
    calendarEventsResponse = calendarService.events().list(
            calendarId='nikola.maric@mimi.io', 
            maxResults=20, 
            timeMin=since.strftime('%Y-%m-%dT%H:%M:%S+02:00')
    ).execute()
    # calendarEventsResponse = requests.get(
    #     'https://www.googleapis.com/calendar/v3/calendars/calendarId/events',
    #     { 
    #         'timeMin': timeMin,
    #         'maxResults': 20
    #     }
    # ).json()
    allEvents = calendarEventsResponse["items"]
    confirmedEvents = list(map(
        lambda event: event.get("start", {}).get("dateTime", None) + "#" + event.get("hangoutLink", None),
        list(filter(
            lambda ev: 
                ev.get("status", None) == "confirmed" and ev.get("hangoutLink", None) is not None
            , 
            allEvents
        ))
    ))
    print(confirmedEvents)
    return confirmedEvents


def login():
    print("Logging into Google account...", end="")
    driver.get('https://accounts.google.com/signin')

    usernameField = wait.until(when.element_to_be_clickable((by.ID, usernameFieldPath)))
    time.sleep(1)
    usernameField.send_keys(USERNAME)

    usernameNextButton = wait.until(when.element_to_be_clickable((by.ID, usernameNextButtonPath)))
    usernameNextButton.click()

    passwordField = wait.until(when.element_to_be_clickable((by.NAME, passwordFieldPath)))
    time.sleep(1)
    passwordField.send_keys(PASSWORD)

    passwordNextButton = wait.until(when.element_to_be_clickable((by.ID, passwordNextButtonPath)))
    passwordNextButton.click()
    time.sleep(3)
    print(colored(" Success!", "green"))


def attendMeet(URL: str):
    print(f"\n\nNavigating to Google Meet #{meetIndex}...", end="")
    driver.get(URL)
    print(colored(" Success!", "green"))

    print(f"Turning off microphone and camera...")
    turnOffMicCam()
    print(f"Turned off microphone and camera.")

    print(f"Entering Google Meet #{meetIndex}...", end="")

    try:
        joinButton = wait.until(when.element_to_be_clickable((by.XPATH, joinButton1Path)))
    except:
        joinButton = wait.until(when.element_to_be_clickable((by.XPATH, joinButton2Path)))
    if BROWSER_DRIVER.lower().startswith("chrom"):
        time.sleep(1)
        action.send_keys(Keys.ESCAPE).perform()
    time.sleep(1)
    joinButton.click()

    print(colored(" Success!", "green"))
    time.sleep(1)
    print(colored(f"Now attending Google Meet #{meetIndex} @{timeStamp()}", "green"), end="")

    try:
        joinButton = wait.until(when.element_to_be_clickable((by.XPATH, joinButton1Path)))   # For another prompt that pops up for Meets being recorded
        time.sleep(1)
        joinButton.click()
    except:
        pass


# explicit function to turn off mic and cam
def turnOffMicCam():
  
    # turn off Microphone
    time.sleep(2)
    driver.find_element_by_xpath(
        '/html/body/div[1]/c-wiz/div/div/div[9]/div[3]/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[4]/div[1]/div/div/div').click()
        # '//*[@id="yDmH0d"]/c-wiz/div/div/div[8]/div[3]/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[4]/div[1]/div/div/div').click()
    driver.implicitly_wait(3000)
  
    # turn off camera
    time.sleep(1)
    driver.find_element_by_xpath(
        '/html/body/div[1]/c-wiz/div/div/div[9]/div[3]/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[4]/div[2]/div/div').click()
        # '//*[@id="yDmH0d"]/c-wiz/div/div/div[8]/div[3]/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[4]/div[2]/div/div').click()
    driver.implicitly_wait(3000)


def endMeet():
    endButton = driver.find_element_by_css_selector(endButtonPath)
    endButton.click()
    print(colored(f"\nSuccessfully ended Google Meet #{meetIndex} @{timeStamp()}\n", "red"), end="")


def genericError():
    # clrscr()
    print(colored(" Failed!", "red"), end="")
    print("\n\nPossible fixes:\n")
    print("1.1 Make sure you have downloaded the latest version of MeetNinja from the GitHub page (every new iteration brings fixes and new capabilities)")
    print("1.2 Make sure you have pip-installed all the required python packages mentioned in the README")
    print("1.3 UNIX-based systems (Linux / Mac): Make sure you have given all the contents of MeetNinja the correct permissions (eg: 'chmod 777 ./ -R')")
    print("2.1 Check your inputs and run MeetNinja again (make sure there are no leading zeros in the Meet start times)")
    print("2.2 And / Or make sure you have chosen the correct webdriver file respective of your web browser and operating system")
    print("3. Make sure the generated web browser is not \"Minimized\" while MeetNinja is working")
    print("4.1. Make sure the webdriver file is of the latest stable build (https://chromedriver.chromium.org/ or https://github.com/mozilla/geckodriver/releases)")
    print("4.2. And / Or make sure your chosen web browser is updated to the latest version")
    print("4.3. And / Or make sure the webdriver file is at least of the same version as your chosen web browser (or lower)")
    print("5. Make sure the small \"time.sleep()\" delays (in seconds) in the login() and attendMeet() functions are comfortable for your internet speed")
    print("6. Make sure your internet connection is stable throughout the process")
    print("\nPress Enter to exit.")
    input()
    try:
        driver.quit()
    except:
        pass


def clrscr():
    if os.name == 'posix':
        _ = os.system('clear')
    else:
        _ = os.system('cls')
    printBanner()


############### Main ###############

if __name__ == "__main__":

    printBanner()

    versionCheck()

    try:
        driver = initBrowser()
        wait = webdriver.support.ui.WebDriverWait(driver, 7)
        action = ActionChains(driver)

        meetings = getMeetings(datetime.now())
        for meetIndex, meeting in enumerate(meetings):
            (rawTime, URL) = meeting.split('#')
            if (meetIndex <= 1):
                print(colored(f"Waiting until first Meet start time [{rawTime}]...", "yellow"), end="")
            else:
                print(colored(f"\n\nWaiting until next Meet start time [{rawTime}]...", "yellow"), end="")
            meetStartsAt = datetime.strptime(rawTime, '%Y-%m-%dT%H:%M:%S%z')
            # @TODO: maricn - actually we shouldn't pause that long, but should recheck occasionally to detect if 
            #  an event had been created in the meantime
            pause.until(meetStartsAt)
            print(colored(" Started!", "green"))
            # @TODO: maricn - find out if you're logged in or not - if not, disturb and ask user to login manually
            # if (meetIndex <= 1):
                # login()
            attendMeet(URL)
            # time.sleep(DURATION_MINS * 60)
            endMeet()
        print("\n\nAll Meets completed successfully.")
        print("Press Enter to exit.")
        input()
        print("\nCleaning up and exiting...", end="")
        driver.quit()

    except KeyboardInterrupt:
        # clrscr()
        print("\n\nCTRL ^C\n\nThrew a wrench in the works.")
        print("Press Enter to exit.")
        input()
        print("\nCleaning up and exiting...", end="")
        driver.quit()
    except:
        # print(e)
        # Uncomment above to display error traceback (use when reporting issues)
        genericError()

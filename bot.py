from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

PORT = os.environ.get('PORT', 8443)
TOKEN = os.environ.get('TOKEN')
URL = os.environ.get('URL')
PATH = executable_path = os.environ.get("CHROMEDRIVER_PATH")

starting_message = 'Send \"get\" to for current occupancy at The Nick'


def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    handleStartCommand = CommandHandler('start', start)
    dispatcher.add_handler(handleStartCommand)

    handleMessageCommand = MessageHandler(Filters.text, handleMessage)
    dispatcher.add_handler(handleMessageCommand)

    updater.start_webhook(listen='0.0.0.0', port=PORT,
                          url_path=TOKEN, webhook_url=URL + TOKEN)

    updater.idle()


def start(update, context):
    update.message.reply_text(starting_message)


def handleMessage(update, context):
    user_text = update.message.text
    if (user_text == 'get'):
        update.message.reply_text('Please wait a couple of seconds')
        currentOccupancy = getCurrentOccupancy()
        update.message.reply_text(currentOccupancy)
    else:
        update.message.reply_text('Invalid command: ' + starting_message)


def getCurrentOccupancy():
    url = "https://services.recwell.wisc.edu/FacilityOccupancy"

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(PATH, chrome_options=chrome_options)
    driver.get(url)

    max_occupancy = driver.find_element_by_class_name("max-occupancy").text
    int_max_occupancy = int(max_occupancy[15: len(max_occupancy)])
    current_occupacy = driver.find_element_by_class_name(
        "occupancy-count").text
    int_current_occupacy_percentage = int(
        current_occupacy[0: len(current_occupacy) - 1])
    int_current_occupancy = int(
        (int_max_occupancy / 100) * int_current_occupacy_percentage)
    facility_count = "Overall occupancy at the Nick: " + \
        str(int_current_occupancy) + "/" + str(int_max_occupancy) + "\n\n"
    driver.quit()

    # retrieving specific facility count
    driver = webdriver.Chrome(PATH, chrome_options=chrome_options)
    url = "https://recwell.wisc.edu/liveusage/"
    driver.get(url)
    time.sleep(3)

    data_all_locations = []

    for element in driver.find_elements_by_class_name("live-tracker"):

        data_for_curr_location = []
        locations = element.find_element_by_class_name("tracker-location").text
        current_person_count = element.find_element_by_class_name(
            "tracker-current-count").text
        max_capacity = element.find_element_by_class_name(
            "tracker-max-count").text
        last_updated_time = element.find_element_by_class_name(
            "tracker-update-time").text
        data_for_curr_location.append(locations)
        data_for_curr_location.append(current_person_count)
        data_for_curr_location.append(max_capacity)
        data_for_curr_location.append(last_updated_time)
        data_all_locations.append(data_for_curr_location)

    num_of_locations = len(data_all_locations)
    for area in range(num_of_locations):
        location = data_all_locations[area][0]
        current_occ = data_all_locations[area][1]
        max_capacity = data_all_locations[area][2]
        last_updated_time = data_all_locations[area][3]
        facility_count += location + ": " + current_occ + \
            "/" + max_capacity + " (" + last_updated_time + ")\n\n"

    return facility_count


if (__name__ == '__main__'):
    main()

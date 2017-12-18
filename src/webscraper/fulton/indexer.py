from scraper import scrape
from selenium import webdriver
import csv
from datetime import datetime
import os

def insert_to_csv(record_number):
  empty_counter = 0
  while True:
    cur_res = scrape(driver, record_number)
    if cur_res == []:
      empty_counter += 1
    else:
      empty_counter = 0
      book_date = cur_res[1][1].split(':')[1].strip()
      par_res = {
        'inmate_id': record_number,
        'booking_date': '' if book_date == '' else datetime.strptime(book_date, '%m/%d/%Y').strftime('%Y-%m-%d')
      }

      csv_writer.writerow(par_res)
    if empty_counter >= 20:
      break
    record_number += 1

dir_path = os.path.dirname(os.path.realpath(__file__))
chrome_path = os.path.join(dir_path, 'chromedriver')
driver = webdriver.Chrome(chrome_path)

fieldnames = ['inmate_id', 'booking_date']

# If date_reference.csv exists, continue scraping from last id and update file
try:
  with open('date_reference.csv', 'r') as csv_file:
    dataList = list(csv.DictReader(csv_file))
    last_id = dataList[len(dataList) - 1]['inmate_id']
    current_record = int(last_id) + 1
    
    csv_file.close()
  with open('date_reference.csv', 'a', newline='') as csv_file:
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=',')
    insert_to_csv(current_record)


# Else if data_reference.csv does not exist, create file and scrape starting from id '1700000'
except FileNotFoundError:
  with open('date_reference.csv', 'w', newline='') as new_file:
    
    csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames, delimiter=',')

    csv_writer.writeheader()

    current_record = 1700000
    insert_to_csv(current_record)

    

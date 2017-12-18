from scraper import scrape
from selenium import webdriver
import csv
import os
import re
from datetime import datetime
from functools import reduce

# For database:
# If race is 'Native Hawaiian or Other Pacific Islander', change to 'pacific-islander'
# If race is 'Indian', change to 'asian'
def checkRace(race):
    return 'pacific-islander' if race == 'Native Hawaiian or Other Pacific Islander' else 'asian' if race == 'Indian' else race

current_record = int( open('last_record.txt','r').read() ) + 1

formatted_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
csv_name_string = '../../../data/fulton_'+formatted_time+'.csv'

dir_path = os.path.dirname(os.path.realpath(__file__))
chrome_path = os.path.join(dir_path,"chromedriver")
driver = webdriver.Chrome(chrome_path)

with open('unreleased.txt','r') as f:
    unreleased = f.readlines()
unreleased = set([int(x.strip()) for x in unreleased])

empty_counter = 0

fieldnames = ['county_name',
              'timestamp',
              'url',
              'inmate_id',
              'inmate_lastname',
              'inmate_firstname',
              'inmate_middlename',
              'inmate_sex',
              'inmate_race',
              'inmate_age',
              'inmate_dob',
              'inmate_address',
              'booking_timestamp',
              'release_timestamp',
              'processing_numbers',
              'agency',
              'facility',
              'charges',
              'severity',
              'bond_amount',
              'current_status',
              'court_dates',
              'days_jailed',
              'other',
              'notes'
        ]

with open(csv_name_string, 'a') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, lineterminator='\n')
    writer.writeheader()

while True:
    cur_res = scrape(driver, current_record)
    if cur_res == []:
        empty_counter += 1
    else:
        empty_counter = 0
        
        par_res = {}
        par_res['url'] = None
        par_res['inmate_age'] = None
        par_res['inmate_dob'] = None
        par_res['court_dates'] = None
        par_res['days_jailed'] = None
        par_res['notes'] = ''
        par_res['county_name'] = 'fulton'
        par_res['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')
        
        par_res['inmate_id'] = current_record
        par_res['inmate_lastname'] = cur_res[2][2].split(' ')[0].strip(',')
        par_res['inmate_firstname'] = cur_res[2][2].split(' ')[1].strip(',')
        try:
            par_res['inmate_middlename'] = cur_res[2][2].split(' ')[2].strip(',')
        except IndexError:
            par_res['inmate_middlename'] = None
        par_res['inmate_sex'] = cur_res[2][4].split('\xa0')[2][0]
        par_res['inmate_race'] = checkRace(cur_res[2][4].split('\xa0')[0])
        # not totally sure if this is inmate address or address of the crime
        par_res['inmate_address'] = cur_res[2][14]
        # not sure what SO number is
        par_res['processing_numbers'] = cur_res[2][10]
        
        book_date = cur_res[1][1].split(':')[1].strip()
        try:
            par_res['booking_timestamp'] = datetime.strptime(book_date, '%m/%d/%Y').strftime('%Y-%m-%d')
        except ValueError:
            par_res['notes'] = par_res['notes']+'no booking date recorded; '
        rel_date = cur_res[1][2].split(':')[1].strip()
        if rel_date == '':
            unreleased.add(current_record)
        else:
            par_res['release_timestamp'] = datetime.strptime(rel_date, '%m/%d/%Y').strftime('%Y-%m-%d')
        
        par_res['agency'] = cur_res[0][1]
        par_res['facility'] = cur_res[1][0].split(':')[1]
        
        # seems bookings can have an arbitrary number of charges
        num_charges = len(cur_res) - 13
        if num_charges > 0:
            charge_list = [re.sub('|','',cur_res[13+i][1]) for i in range(num_charges)]
            par_res['charges'] = reduce((lambda x,y: x + ' | ' + y), charge_list)
            sev_list = ['' for x in range(num_charges)]
            for charge in range(num_charges):
                if 'Felony' in charge_list[charge]:
                    sev_list[charge] = 'Felony'
                if 'Misdemeanor' in charge_list[charge]:
                    sev_list[charge] = 'Misdemeanor'
            par_res['severity'] = reduce((lambda x,y: x + ' | ' + y), sev_list)
            
            bond_amount_list = [re.sub('\D','',cur_res[13+i][4])[:-2] for i in range(num_charges)]
            for i in range(len(bond_amount_list)):
                if bond_amount_list[i] != '':
                    bond_amount_list[i] = '$' + bond_amount_list[i]        
            bond_type_list = [re.sub('[^a-zA-Z\s]','',cur_res[13+i][4]) for i in range(num_charges)]
            bond_list = [ bond_amount_list[i]+' '+bond_type_list[i] for i in range(num_charges)]
            par_res['bond_amount'] = reduce((lambda x,y: x + ' | ' + y), bond_list)
            
            disp_list = [re.sub('|','',cur_res[13+i][6]) for i in range(num_charges)]
            par_res['current_status'] = reduce((lambda x,y: x + ' | ' + y), disp_list)
            
            offense_d_list = [cur_res[13+i][3] for i in range(num_charges)]
            par_res['other'] = reduce((lambda x,y: x + ' | ' + y), offense_d_list)
        else:
            par_res['charges'] = None
            par_res['bond_amount'] = None
            par_res['current_status'] = None
            par_res['severity'] = None
        
        with open(csv_name_string, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, lineterminator='\n')
            writer.writerow(par_res)
    
    if empty_counter >= 20:
        break
    current_record += 1
        
last_record_scraped = current_record - 20

with open('last_record.txt', 'w') as f:
    f.write(str(last_record_scraped))

unreleased_file = open('unreleased.txt','w')
for booking in unreleased:
  unreleased_file.write("%s\n" % booking)
unreleased_file.close()

driver.close()

def binarySearch(data, date):
  mid = (len(data))/2

  inmate_id_range = []

  if not len(data):
    raise 'Error'
  if date == data[mid]:
    for i in range(mid, 0, -1):
      print(data[i])
      if data[i] != data[mid]:
        inmate_id_range[0] = data[i+1]['inmate_id']

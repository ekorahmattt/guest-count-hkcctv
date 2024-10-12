import requests
import time
from datetime import datetime
from pytz import timezone

############################ SETTING API ######################################

SAVED_COUNT = 'http://api-hkiot.kazuyosan.my.id:8081/database/history/HKCCTV_DH001/guest_count/'
format_date = "%d_%m_%Y"

################################ DATABASES FUNCTION  ###############################################

def getHour():
    hours = datetime.now(timezone("Asia/Makassar")).strftime("%#H")
    return hours

def getDate():
    date_now = datetime.now(timezone('Asia/Makassar')).strftime(format_date)
    return date_now

def sendData(vanue, people_in, people_out):
    format_data = {
        'name':vanue,
        'in':people_in,
        'out':people_out
    }
    response = requests.post(SAVED_COUNT+getDate()+"?key="+getHour(), json=format_data)

def getCounted():
    
    response = requests.get(SAVED_COUNT+getDate()+"?key="+getHour())
    
    if response.status_code!=200:
        people_in = 0
        people_out = 0
    
    else:
        data_count = response.json()
        people_in = data_count['in']
        people_out = data_count['out']
    
    return people_in, people_out
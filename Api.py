from cmath import e
import csv
import json
from logging import raiseExceptions
import pandas as pd

from operator import index

import requests

url = "https://www.cradlepointecm.com/api/v2/routers/?state=online&account__in=92725&fields=account,id,ipv4_address,description,state"

headers = {
    'X-CP-API-ID': 'a2fb9d1d',
    'X-CP-API-KEY': '608f3a84ae2e1666b81c2757b7f98252',
    'X-ECM-API-ID': '4661a3de-6b31-4b5f-a8e0-01ba67679310',
    'X-ECM-API-KEY': 'b9bfcdf82c187a428fdffd22c25d338d0b915a0b',
    'Content-Type': 'application/json'
}

routers = []


def get_routers():
    Exceptions = []
    req = requests.get(url, headers=headers)
    response = req.json()
    routers_response = response["data"]
    for router in routers_response:
        try:
            router["zip"] = get_zip_code_from_router(router)
            router_location_data = get_state_and_city_from_router(router)
            if "city" in router_location_data:
                router["city"] = router_location_data["city"]
            else:
                raise Exception("Error, couldn´t find city for router with id: "+router["id"])
            if "state" in router_location_data:
                router["state_location"] = router_location_data["state"]
            else:
                raise Exception("Error, couldn't find state for router with id: "+router["id"])
        except Exception as e:
            log_file_error(str(e))
    save_data_csv(routers_response)


def get_zip_code_from_router(router):
    description: str = router["description"]
    zip_code = description.split(', ')[1]
    return zip_code
    
def get_state_and_city_from_router(router):
    file = open("US_GeoStats.csv", "r")
    csvreader = csv.reader(file)
    for row in csvreader:
        if router["zip"] == row[0]:
            city = row[1]
            state = row[2]
            return {"city": city, "state": state}
    return {}
    
def save_data_csv(routers):
    file = open("routers.csv", "w")
    routers_to_string = json.dumps(routers)
    df = pd.read_json (routers_to_string)
    df.to_csv (file, index = None)


def log_file_error(error):
    file = open("error.txt", "a")
    file.write(error)
    file.write('\n')


get_routers()



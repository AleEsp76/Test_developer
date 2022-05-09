#Libraries and packages that are used within the script
from cmath import e
import csv
import json
from logging import raiseExceptions
import pandas as pd
from operator import index
import requests

#URL used to fetch information from the API
url = "https://www.cradlepointecm.com/api/v2/routers/?state=online&account__in=92725&fields=account,id,ipv4_address,description,state"

#Permissions required to access the API
headers = {
    'X-CP-API-ID': 'a2fb9d1d',
    'X-CP-API-KEY': '608f3a84ae2e1666b81c2757b7f98252',
    'X-ECM-API-ID': '4661a3de-6b31-4b5f-a8e0-01ba67679310',
    'X-ECM-API-KEY': 'b9bfcdf82c187a428fdffd22c25d338d0b915a0b',
    'Content-Type': 'application/json'
}

routers = []

#Function used to obtain information from routers
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
                #If it doesn't find the required information it will write an error message to a .txt file
                raise Exception("Error, couldn´t find city for router with id: "+router["id"])
            if "state" in router_location_data:
                router["state_location"] = router_location_data["state"]
            else:
                raise Exception("Error, couldn't find state for router with id: "+router["id"])
        except Exception as e:
            log_file_error(str(e))
    save_data_csv(routers_response)

#This function reads the description string that comes from the router and takes only the zip code that is found by separating the text by commas
def get_zip_code_from_router(router):
    description: str = router["description"]
    zip_code = description.split(', ')[1]
    return zip_code
#Esta funcion lee el archivo cvs donde se encuentran la informacion de la ubicacion de los routers utilizando de parametro de busqueda el codigo zip    
def get_state_and_city_from_router(router):
    file = open("US_GeoStats.csv", "r")
    csvreader = csv.reader(file)
    for row in csvreader:
        if router["zip"] == row[0]:
            city = row[1]
            state = row[2]
            return {"city": city, "state": state}
    return {}

#This function takes the information from the routers, opens a .cvs file and saves the information.
def save_data_csv(routers):
    file = open("routers.csv", "w")
    routers_to_string = json.dumps(routers)
    df = pd.read_json (routers_to_string)
    df.to_csv (file, index = None)

#This function receives an error string, opens a .txt file and writes the error that was found in it
def log_file_error(error):
    file = open("RouterStateErrors.txt", "a")
    file.write(error)
    file.write('\n')


get_routers()



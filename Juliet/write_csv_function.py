import csv
from csv import DictWriter
import time
import random

headersCSV = ['Latitude','Longitude']  
dict={'Longitude':'','Latitude':''}

def add_value(): 
    with open('CSVFILE.csv', 'a', newline='') as f_object:
        lat = random.uniform(35.9, 36.1)
        long = random.uniform(-78.9, -79.1)
        dict["Longitude"] = str(long)
        dict["Latitude"] = str(lat)
        dictwriter_object = DictWriter(f_object, fieldnames=headersCSV)
        # Pass the data in the dictionary as an argument into the writerow() function
        dictwriter_object.writerow(dict)
        # Close the file object
        f_object.close()

while True:
    time.sleep(2)
    add_value()

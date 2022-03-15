import tkinter
from tkinter import *
from  tkinter import ttk
import random
import csv

from tkintermapview import TkinterMapView

root_tk = tkinter.Tk()
root_tk.geometry(f"{600}x{400}")
root_tk.title("map_view_simple_example.py")

# create map widget
map_widget = TkinterMapView(root_tk, width=600, height=400, corner_radius=0)
map_widget.pack(fill="both", expand=True, side=LEFT)

map_widget.set_address("Durham North Carolina", marker=True)

id = 1
rows = []
prev = None

def save_csv():
    print("csv")
    f = open('test.csv', 'w')
    writer = csv.writer(f)
    writer.writerow(['id', 'lat', 'long'])
    writer.writerows(rows)
    f.close()
    
def run_drone(lat, long):
    global prev, id, rows
    #lat = random.uniform(35.9, 36.1)
    #long = random.uniform(-78.9, -79.1)
    rows.append([id, lat, long])
    marker = map_widget.set_marker(lat, long, text=str("marker") + str(id))

    if (prev is not None):
        path_1 = map_widget.set_path([marker.position, prev.position])
    table.insert(parent='',index='end',iid=id,text='',
        values=(str(id),str(lat),str(long)))
    prev = marker
    id += 1

frame = Frame(root_tk)
frame.pack(side=RIGHT, expand=True)    

#create button to run drone code
button = Button(frame, text ='Run Drone Code', command=run_drone)  
button.pack(side=BOTTOM)

#create button to save csv
button = Button(frame, text ='Save as CSV', command=save_csv)  
button.pack(side=BOTTOM)

table = ttk.Treeview(frame)

table['columns'] = ('id', 'lat', 'long')

table.column("#0", width=0,  stretch=NO)
table.column("id",anchor=CENTER, width=80)
table.column("lat",anchor=CENTER,width=80)
table.column("long",anchor=CENTER,width=80)

table.heading("#0",text="",anchor=CENTER)
table.heading("id",text="Id",anchor=CENTER)
table.heading("lat",text="Lat",anchor=CENTER)
table.heading("long",text="Long",anchor=CENTER)

table.pack(side=TOP,expand=True)
with open('data.csv') as f:
    csv_reader = csv.reader(f, delimiter=',')
    line_count = 0
    for row in csv_reader:
        run_drone(row[0], row[1])
root_tk.mainloop()

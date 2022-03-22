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
last_entry = 0

def save_csv():
    print("csv")
    f = open('test.csv', 'w')
    writer = csv.writer(f)
    writer.writerow(['id', 'lat', 'long'])
    writer.writerows(rows)
    f.close()
    
def run_drone():
    global prev, id, rows, last_entry
    # lat = random.uniform(35.9, 36.1)
    # long = random.uniform(-78.9, -79.1)
    # rows.append([id, lat, long])
    with open('CSVFILE.csv') as fd:
        reader=csv.reader(fd)
        # interestingrows=[row for idx, row in enumerate(reader) if idx == last_entry]
        interestingrows = list(reader)
        for index in range(last_entry, len(interestingrows)):
            lat = float(interestingrows[index][0])
            long = float(interestingrows[index][1])
            
            marker = map_widget.set_marker(lat, long, text=str("marker") + str(id))

            if (prev is not None):
                path_1 = map_widget.set_path([marker.position, prev.position])
            table.insert(parent='',index='end',iid=id,text='',
                values=(str(id),str(lat),str(long)))
            prev = marker
            id += 1
        last_entry = len(interestingrows)

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

def task():
    run_drone()
    root_tk.after(2000, task)  # reschedule event in 2 seconds

root_tk.after(2000, task)
root_tk.mainloop()

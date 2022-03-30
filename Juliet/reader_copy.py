from curses.textpad import Textbox
import tkinter
from tkinter import *
from  tkinter import ttk
import tkinter.messagebox
import random
import csv
from csv import DictWriter
from datetime import datetime
import shutil
import os

from tkintermapview import TkinterMapView

root_tk = tkinter.Tk()
root_tk.geometry(f"{900}x{600}")
root_tk.title("map_view_simple_example.py")

# create map widget
map_widget = TkinterMapView(root_tk, width=600, height=400, corner_radius=0)
map_widget.pack(fill="both", expand=True, side=LEFT)

map_widget.set_address("Durham North Carolina", marker=True)

id = 1
rows = []
prev = None
last_entry = 0
base_path = os.getcwd()
original_path = base_path + "/CSVFILE.csv"

headersCSV = ['Longitude','Latitude']  
dict={'Longitude':'','Latitude':''}

def save_csv():
    global base_path, original_path
    now = datetime.now()
    dt_string = "Flight on " + now.strftime("%b-%m-%Y %H:%M:%S") + ".csv"
    new_path = base_path + "/" + dt_string
    shutil.copyfile(original_path, new_path)
    open_save_csv_popup(dt_string)

def clear_csv():
    global base_path, original_path, prev, id, rows, last_entry
    f = open(original_path, "w+")
    f.close()
    id = 1
    rows = []
    prev = None
    last_entry = 0
    clear_map()

def clear_map():
    for item in table.get_children():
      table.delete(item)
    map_widget.canvas_marker_list.clear()
    map_widget.canvas_path_list.clear()

def run_drone():
    global prev, id, rows, last_entry
    with open('CSVFILE.csv') as fd:
        reader=csv.reader(fd)
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

def clear_choice(option):
    pop.destroy()
    if option == "yes":
        clear_csv()
    else:
        print("no")

def open_save_csv_popup(dt_string):
    global pop
    pop = Toplevel(root_tk)
    pop.title("Save CSV")
    pop.geometry("450x150")
    pop.config(bg="white")

    info = "CSV has been saved!\n Filename: " + dt_string

    pop_label = Label(pop, text=info)
    pop_label.pack(pady=10)

def open_clear_popup():
    global pop
    pop = Toplevel(root_tk)
    pop.title("Clear CSV")
    pop.geometry("450x150")
    pop.config(bg="white")
    
    pop_label = Label(pop, text="Are you sure you would like to clear the CSV and Flight Data")
    pop_label.pack(pady=10)
    
    my_frame = Frame(pop)
    my_frame.pack(pady=5)
    
    yes = Button(my_frame, text="YES", command=lambda: clear_choice("yes"))
    yes.grid(row=0, column=1, padx=10)
    no = Button(my_frame, text="NO", command=lambda: clear_choice("no"))
    no.grid(row=0, column=2, padx=10)

def tag_marker_popup():
    global pop
    pop = Toplevel(root_tk)
    pop.title("Save CSV")
    pop.geometry("450x150")
    pop.config(bg="white")

    pop_label = Label(pop, text="Please enter the coordinate id")
    pop_label.pack(pady=10)

    my_frame = Frame(pop)
    my_frame.pack(pady=5)

    ok = Button(my_frame, text="Save Marker", command=lambda: tag_marker(pop_input.get()))
    ok.grid(row=0, column=1, padx=10)

    pop_input = Entry(pop)
    pop_input.pack()


def tag_marker(pop_input):
    id = int(pop_input)
    print(id)
    pop.destroy()

frame = Frame(root_tk)
frame.pack(side=RIGHT, expand=True)    

#create button to confirm clearing flight
button = Button(frame, text ='Clear Flight', command=open_clear_popup)  
button.pack(side=BOTTOM)

#create button to save csv
button = Button(frame, text ='Save as CSV', command=save_csv)  
button.pack(side=BOTTOM)

button = Button(frame, text ='Tag Marker', command=tag_marker_popup)  
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

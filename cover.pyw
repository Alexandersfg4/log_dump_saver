from tkinter import *
from tkinter.ttk import Combobox
from tkinter import filedialog
from tkinter.ttk import Progressbar
from tkinter import messagebox
import logging, sys
import background
import os, re
import threading
from time import sleep
#def logging setting
logging.basicConfig(filename='logsaver.log',format='%(asctime)s %(levelname)s: %(message)s',level=logging.DEBUG)


def slect_mysql_db():
    global mysql_window
    mysql_window = Toplevel()
    mysql_window.title("Founded db's")
    mysql_window.geometry('250x250')
    db_label_found = Label(window, text="Please select databases: ")
    db_label_found.grid(column=0, row=0)
    global found_db
    found_db = background.mysql_show_tables()
    logging.info(f'The next tabes have been found {found_db}')
    for i in range(len(found_db)):
        globals()['tabel_' + str(i)] = BooleanVar()
        # create a new variables for checkboxes
        logging.info(f"The next variable has been created: {found_db[i]}")
        globals()[found_db[i]] = Checkbutton(mysql_window, text=found_db[i], var=globals()['tabel_' + str(i)])
        globals()[found_db[i]].grid(column=0, row=i + 1, sticky=W)
    apply = Button(mysql_window, text="Apply", command=getting_mysql_db)
    apply.grid(column=0, row=len(found_db)+1, sticky=W)
    mysql_window.mainloop()



#get values from mysql_window
def getting_mysql_db():
    logging.info('Button SQL slection is pressed')
    global selected_db
    selected_db = []
    for i in range(len(found_db)):
        if globals()['tabel_' + str(i)].get():
            logging.info(f'the next table {found_db[i]} has been selected')
            selected_db.append(found_db[i])
    mysql_window.destroy()


#select all checkboxes for server1
def select_all_command_1(): # Corrected
    for component in list_of_components_variables_server_1:
        if globals()[component].get():
            globals()[component].set(0)
        else:
            globals()[component].set(1)

#select all checkboxes for server2
def select_all_command_2(): # Corrected
    for component in list_of_components_variables_server_2:
        if globals()[component].get():
            globals()[component].set(0)
        else:
            globals()[component].set(1)

#quit main window
def quit_command():
    sys.exit()

def downloader_components_server_1():
     # select checked checkboxes 1st server
    for i in range(len(list_of_components_variables_server_1)):
        if globals()[list_of_components_variables_server_1[i]].get():
            logging.info(f'{list_of_components_variables_server_1[i]} is Checked')
            task.set(f'Server 1: Downloading the next file {list_of_components_1[i]}')
            p1['value'] += task_reward
            try:
                background.log_downloading_server_1(list_of_components_1[i], os.path.join(full_path, 'server_1', list_of_components_1[i]))
            except Exception as exc:
                logging.error(f'log_downloading_server_1 {exc}')
        task.set('Server 1  - COMPLETED')


def downloader_components_server_2():
    # select checked checkboxes 2nd server
    for i in range(len(list_of_components_variables_server_2)):
        if globals()[list_of_components_variables_server_2[i]].get():
            logging.info(f'{list_of_components_variables_server_2[i]} is Checked')
            task_2.set(f'Server 2: Downloading the next file {list_of_components_2[i]}')
            p1['value'] += task_reward
            try:
                background.log_downloading_server_2(    list_of_components_2[i], os.path.join(full_path, 'server_2', list_of_components_2[i]))
            except Exception as exc:
                logging.error(f'log_downloading_server_2 {exc}')
        task_2.set('Server 2  - COMPLETED')


def downloader_mongodump():
    # select checked mongo db
    if mongo_state.get() == True:
        host = combo_mongo.get()
        logging.info(f'Will be completed mongodum: {host}')
        task_3.set(f'Making mongodump of the next server: {host}')
        background.mongo_dump(host, full_path)
        task_3.set('mongodump  - COMPLETED')
        p1['value'] += task_reward

def downloader_mysql_dump():
    # verify that mysqldump checkbox is checked
    if mysql_state.get() == True:
        logging.info(f'the next MYSQL db {selected_db} are going to be dumped')
        task_4.set(f'Making mysqldump')
        background.mysql_dump(selected_db, full_path)
        task_4.set('mysqldump  - COMPLETED')
        p1['value'] += task_reward

def start_clicked_background():
    #create a text_variable
    global task
    task = StringVar()
    task.set("Server 1 no task is scheduled")
    global task_2
    task_2 = StringVar()
    task_2.set("Server 2 no task is scheduled")
    global task_3
    task_3 = StringVar()
    task_3.set("Mongodump no task is scheduled")
    global task_4
    task_4 = StringVar()
    task_4.set("Mysqldump no task is scheduled")
    # creating folder if at least one component is slected
    # a little delay for declaring the varible p
    sleep(0.1)
    global full_path
    try:
        full_path = background.creating_folder(default_path)
    except Exception as exc:
        folder_error = messagebox.showerror(title='Folder cannot be created', message=exc)
    t_b = threading.Thread(target=downloader_components_server_1, name='downloader_components_server_1()')
    t_b.start()
    try:
        t_b = threading.Thread(target=downloader_components_server_2, name='downloader_components_server_2()')
        t_b.start()
    except Exception as exc:
        server_2_components = messagebox.showerror(title='Server 2 downloading logs error', message=exc)
    try:
        t_b = threading.Thread(target=downloader_mongodump, name='downloader_mongodump()')
        t_b.start()
    except Exception as exc:
        mongo_error = messagebox.showerror(title='mongodump error', message=exc)
    try:
        t_b = threading.Thread(target=downloader_mysql_dump, name='downloader_mysql_dump()')
        t_b.start()
    except Exception as exc:
        mysql_error = messagebox.showerror(title='mysql error', message=exc)




def start_clicked_ui():
    global start_window
    start_window = Toplevel()
    start_window.title("Progress...")
    start_window.geometry('400x150')
    task_label = Label(start_window, textvariable=task)
    task_label.grid(column=0, row=0, sticky=W)
    task_label_2 = Label(start_window, textvariable=task_2)
    task_label_2.grid(column=0, row=1, sticky=W)
    task_label_3 = Label(start_window, textvariable=task_3)
    task_label_3.grid(column=0, row=2, sticky=W)
    task_label_4 = Label(start_window, textvariable=task_4)
    task_label_4.grid(column=0, row=3, sticky=W)
    #progress bar
    global p1
    p1 = Progressbar(start_window, length=300, cursor='spider',mode="determinate", orient=HORIZONTAL)
    p1.grid(column=0, row=4, sticky=W)
    #p1.start(interval=2000)
    #terminate all progress
    Tetminate = Button(start_window, text="Tetminate", command=sys.exit)
    Tetminate.grid(column=1, row=5, stick=E)
    ok = Button(start_window, text="ok", command=start_window.destroy)
    ok.grid(column=0, row=5, stick=W)

def count_checkboxes():
    counter = 0
    #count checked server 1 checkboxes
    for i in range(len(list_of_components_variables_server_1)):
        if globals()[list_of_components_variables_server_1[i]].get():
            counter +=1
            logging.info(f'{list_of_components_variables_server_1[i]} is counted')
    # count checked checkboxes 2nd server
    for i in range(len(list_of_components_variables_server_2)):
        if globals()[list_of_components_variables_server_2[i]].get():
            counter +=1
            logging.info(f'{list_of_components_variables_server_2[i]} is counted')
    #count mongo checkbox
    if mongo_state.get() == True:
        counter += 1
        logging.info(f'mongo state is counted')
    #count mysql checkbox
    if mysql_state.get() == True:
        logging.info(f'MYSQLdump is counted')
        counter += 1
    return counter

def start_clicked():
    counter = count_checkboxes()
    logging.info(f'final counter is {counter}')
    global task_reward
    task_reward = 100/int(counter)
    t = threading.Thread(target=start_clicked_background, name='start_clicked_background()')
    t.start()
    t = threading.Thread(target=start_clicked_ui, name='start_clicked_ui()')
    t.start()





def creating_checkbuttons(server, column, list_of_components):
    returning_list = []
    for i in range(len(list_of_components)):
        variable_component = re.sub('.log', server, list_of_components[i])
        globals()[variable_component] = BooleanVar()
        globals()[variable_component].set(True)
        # create a new variables for checkboxes
        logging.info(f"The next variable has been created: {variable_component}")
        # create a new checkbox's objects
        globals()[server + str(i)] = Checkbutton(window, text=list_of_components[i], var=globals()[variable_component], onvalue=True, offvalue=False).grid(column=column, row=i + 1, sticky=W)
        returning_list.append(variable_component)
    return returning_list




if __name__ == '__main__':
    window = Tk()
    window.title("Logsaver")
    window.geometry('700x900')
    #Server1 UI
    serv_1 = Label(window, text="Server 1:")
    serv_1.grid(column=0, row=0, sticky=W)
    try:
        list_of_components_1 = background.get_list_first() #list of components on 1st server
        list_of_components_variables_server_1 = creating_checkbuttons('server_1', 0, list_of_components_1) #create checkboxes with components server1
    except Exception as exc:
        server_1_un = messagebox.showerror(title='Server 1 is unavailable', message=exc)
        sys.exit()
    #create select all chekcbox server_1
    select_all_1 = BooleanVar()
    select_all_1.set(True)
    select_all_1_b = Checkbutton(window, text='Select All', command=select_all_command_1, var=select_all_1)
    select_all_1_b.grid(column=0, row=len(list_of_components_1) + 1, sticky=W)
    # Server2 UI
    serv_2 = Label(window, text="Server 2:")
    serv_2.grid(column=1, row=0, sticky=W)
    try:
        list_of_components_2 = background.get_list_second()  #list of components on 2nd server
        list_of_components_variables_server_2 = creating_checkbuttons('server_2', 1, list_of_components_2) #create checkboxes with components server2
        # create select all chekcbox server_2
        select_all_2 = BooleanVar()
        select_all_2.set(True)
        select_all_2_b = Checkbutton(window, text='Select All', command=select_all_command_2, var=select_all_2)
        select_all_2_b.grid(column=1, row=len(list_of_components_2) + 1, sticky=W)
    except Exception as exc:
        server_2_un = messagebox.askyesno(title='Server 2 is unavailable', message='Do you want to continue?')
        if not server_2_un:
            sys.exit()
    #DB UI
    db_label = Label(window, text="Make a dump:")
    db_label.grid(column=2, row=0, sticky=W)
    #UI mongodump
    mongo_state = BooleanVar()
    mongo_state.set(False)  # def
    mongo_button = Checkbutton(window, text='Mongo', var=mongo_state, ).grid(column=2, row=1, stick=W)
    combo_mongo = Combobox(window)
    combo_mongo['values'] = background.get_ip_adresses()
    combo_mongo.current(0)  # firs is default
    combo_mongo.grid(column=3, row=1)
    #UI mysqldump
    founded_databases = []
    mysql_state = BooleanVar()
    mysql_state.set(False)  # def
    try:
        mysql_button = Checkbutton(window, text='Mysql',command=slect_mysql_db, var=mysql_state, onvalue=True, offvalue=False).grid(column=2, row=2, stick=W)
    except Exception as exc:
        server_1_un = messagebox.showerror(title='Mysql DB 1 is unavailable', message=exc)
    #path to the files
    default_path = background.get_local_path()
    path_intro = Label(window, text="All files will be saved here: ")
    path_intro.grid(column=3, row=3)
    path = Label(window, text=default_path)
    path.grid(column=3, row=4)
    # Function for opening the file
    def file_opener():
        global default_path
        input = filedialog.askdirectory(initialdir=default_path)
        logging.info(f'Local path: {input}')
        default_path = input
        path.configure(text=input)
    # Button label
    x = Button(window, text='Change local path', command=lambda: file_opener())
    x.grid(column=3, row=5)
    #run button
    start = Button(window, text="Start", command=start_clicked)
    start.grid(column=3, row=6, stick=W)
    #start.grid(column=1, row=len(list_of_components)+3, sticky = W)
    #exit programm
    quit = Button(window, text="Quit", command=quit_command)
    quit.grid(column=3, row=6, stick=E)
    #quit.grid(column=2, row=len(list_of_components) + 3, sticky=W)
    window.mainloop()
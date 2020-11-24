import configparser, os, logging, paramiko, re
import datetime
from time import sleep
import mysql.connector


remoute_log_dir = '/var/log/servicepattern'
#logging
logging.basicConfig(filename='logsaver.log', format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)
#create a configparser object
cfg = configparser.ConfigParser()
cfg.read('config.ini')

#get local path
def get_local_path():
    return cfg.get("Settings", "localpath")

#creatin specific folder by date
def creating_folder(localpath=cfg.get('Settings', 'localpath', raw=False)):
    date_time = datetime.datetime.now()
    name_of_the_folder = date_time.strftime("%H_%M_%S_%d_%m_%Y")
    full_path = os.path.join(localpath, name_of_the_folder)
    if not os.path.exists(full_path):
        os.mkdir(full_path)
        logging.info(f'folder {full_path} has been created')
        os.mkdir(os.path.join(full_path, 'server_1'))
        os.mkdir(os.path.join(full_path, 'server_2'))
        return full_path
    else:
        logging.error(f'folder {name_of_the_folder} exists')

def show_files_in_dir(host, port, username, password, path):
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    files_in_dir = sftp.listdir(path)
    sftp.close()
    transport.close()
    return files_in_dir

def return_essantial_log_names(list_of_files):
    regex = re.compile("(\D)+(.log)")
    list_of_componets = []
    for name in list_of_files:
        if bool(regex.search(name)):
            list_of_componets.append(name)
    return list_of_componets


def gel_log_files_names(host, port, username, password):
    if os.path.exists('config.ini'):
        list_of_files = show_files_in_dir(host, port, username, password, remoute_log_dir)
        list_of_files.sort() #sort list by alphavite
        return return_essantial_log_names(list_of_files)
    else:
        print(f'Error - config.ini file is absent')
        logging.critical('config.ini file is absent')

def get_list_first():
     return gel_log_files_names(cfg.get('Settings', 'host_1', raw=False), cfg.getint('Settings', 'port', raw=False), cfg.get('Settings', 'username', raw=False), cfg.get('Settings', 'password', raw=False))


def get_list_second():
    return gel_log_files_names(cfg.get('Settings', 'host_2', raw=False), cfg.getint('Settings', 'port', raw=False), cfg.get('Settings', 'username', raw=False), cfg.get('Settings', 'password', raw=False))

def get_ip_adresses():
    list = []
    list.append(cfg.get('Settings', 'host_1', raw=False))
    list.append(cfg.get('Settings', 'host_2', raw=False))
    list.append(cfg.get('Settings', 'host_3', raw=False))
    return tuple(list)

#execute any command on bash
def command_execute(hostname, username, password, command):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=hostname, username=username, password=password)
    stdin, stdout, stderr = ssh_client.exec_command(command)
    data = stdout.read() + stderr.read()
    logging.info(f'This is data {data}')
    ssh_client.close()
    return data

#findig zip error (that zip is not installed)
def finding_error(data):
    regex = re.compile('bash: zip: command not found')
    if regex.search(data.decode()) == None:
        logging.info('Zip is installed')
        return False
    else:
        logging.info('Zip is  not installed')
        return True

def mongo_dump(hostname, full_path):
    #make a dump by shell
    command_execute(hostname, cfg.get('Settings', 'username', raw=False), cfg.get('Settings', 'password', raw=False), 'mongodump')
    data = command_execute(hostname, cfg.get('Settings', 'username', raw=False), cfg.get('Settings', 'password', raw=False), 'zip dump -r dump')
    if finding_error(data) == True:
        #if return error, zip util is not install, will be installed zip
        command_execute(hostname, cfg.get('Settings', 'username', raw=False), cfg.get('Settings', 'password', raw=False), 'yum install zip -y')
        logging.info("ZIP is absent, installing zip")
        #make a new archive from erlier created dump
        command_execute(hostname, cfg.get('Settings', 'username', raw=False), cfg.get('Settings', 'password', raw=False), 'zip dump -r dump')
    #downloading the zip arhive to local machine
    file_downloading(hostname, cfg.get('Settings', 'username', raw=False), cfg.get('Settings', 'password', raw=False), 'dump.zip', os.path.join(full_path, 'dump.zip'))
    #remove dump.zip and dump folder
    command_execute(hostname, cfg.get('Settings', 'username', raw=False), cfg.get('Settings', 'password', raw=False), 'rm -rf dump*')
    logging.info("All cash files has been removed")


    # mongorestore --host  --port 3017 --db mongodevdb --username mongodevdb --password YourSecretPwd --drop /backup/dump
#to do
def mysql_dump(list_of_db, full_path):
    db = ''
    for i in range(len(list_of_db)):
        db = db + ' ' + list_of_db[i]
    command_execute(cfg.get('Settings', 'host_1', raw=False), cfg.get('Settings', 'username', raw=False), cfg.get('Settings', 'password', raw=False), 'mysqldump -u {} -p{} --databases {} > mysqldump.sql'.format(cfg.get('Mysql', 'username', raw=False), cfg.get('Mysql', 'password', raw=False), db))
    logging.info('MysqlDUMP has been completed')
    data = command_execute(cfg.get('Settings', 'host_1', raw=False), cfg.get('Settings', 'username', raw=False), cfg.get('Settings', 'password', raw=False), 'zip mysqldump -r mysqldump.sql')
    if finding_error(data) == True:
        # if return error, zip util is not install, will be installed zip
        command_execute(cfg.get('Settings', 'host_1', raw=False), cfg.get('Settings', 'username', raw=False), cfg.get('Settings', 'password', raw=False), 'yum install zip -y')
        logging.info("ZIP is absent, installing zip")
        # make a new archive from erlier created dump
        command_execute(cfg.get('Settings', 'host_1', raw=False), cfg.get('Settings', 'username', raw=False), cfg.get('Settings', 'password', raw=False), 'zip mysqldump -r mysqldump.sql')
    # downloading the zip arhive to local machine
    file_downloading(cfg.get('Settings', 'host_1', raw=False), cfg.get('Settings', 'username', raw=False), cfg.get('Settings', 'password', raw=False),'mysqldump.zip', os.path.join(full_path, 'mysqldump.zip'))
    # remove mysqldump.zip and mysqldump folder
    command_execute(cfg.get('Settings', 'host_1', raw=False), cfg.get('Settings', 'username', raw=False), cfg.get('Settings', 'password', raw=False), 'rm -rf mysqldump*')
    logging.info("All cash files has been removed")



#show presented db's
def mysql_show_tables():
    list_of_tabes = []
    mydb = mysql.connector.connect(
        host=cfg.get('Mysql', 'host', raw=False),
        user=cfg.get('Mysql', 'username', raw=False),
        password=cfg.get('Mysql', 'password', raw=False)
    )
    mycursor = mydb.cursor()
    mycursor.execute("SHOW DATABASES")
    restricted_tabels =['information_schema', 'mysql', 'performance_schema']
    for x in mycursor:
        for db in x:
            if db not in restricted_tabels:
                list_of_tabes.append(db)
    return list_of_tabes

#downloading any file
def file_downloading(hostname, username, password, remote_file, localpath):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=hostname, username=username, password=password)
    logging.info(f'file {remote_file} will be downloaded')
    ftp_client = ssh_client.open_sftp()
    ftp_client.get(remote_file, localpath)
    logging.info(f'file {localpath} has been downloaded')
    ftp_client.close()

def log_downloading_server_1(remote_file, localpath):
    file_downloading(cfg.get('Settings', 'host_1', raw=False), cfg.get('Settings', 'username', raw=False), cfg.get('Settings', 'password', raw=False), remoute_log_dir + '/' + remote_file, localpath)

def log_downloading_server_2(remote_file, localpath):
    file_downloading(cfg.get('Settings', 'host_2', raw=False), cfg.get('Settings', 'username', raw=False), cfg.get('Settings', 'password', raw=False), remoute_log_dir + '/' + remote_file, localpath)

if __name__ == "__main__":
    list_of_tabels = mysql_show_tables()
    print(list_of_tabels)
    mysql_dump(list_of_tabels)
    #full_path = creating_folder()
    #mongo_dump(cfg.get('DBservers', 'mongodb_server_address_1', raw=False), cfg.get('DBservers', 'mongodb_server_user_1', raw=False), cfg.get('DBservers', 'mongodb_server_password_1', raw=False))
    #mysql_show_tables()

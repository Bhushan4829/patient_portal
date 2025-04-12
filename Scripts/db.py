import pyodbc
import configparser

def get_config(section):
    config = configparser.ConfigParser()
    config.read('db_config.ini')
    return {key: value for key, value in config.items(section)}

def get_db_connection():
    conf = get_config('database')
    connection_string = f"""
        DRIVER={{{conf['driver']}}};
        SERVER={conf['server']};
        DATABASE={conf['database']};
        UID={conf['uid']};
        PWD={conf['password']};
        Authentication=ActiveDirectoryInteractive;
        ENCRYPT=yes;
        TrustServerCertificate=yes;
    """
    return pyodbc.connect(connection_string, timeout=10)

def get_hospital_db_connection():
    conf = get_config('hospital_database')
    connection_string = f"""
        DRIVER={{{conf['driver']}}};
        SERVER={conf['server']};
        DATABASE={conf['database']};
        UID={conf['uid']};
        PWD={conf['password']};
        Authentication=ActiveDirectoryInteractive;
        ENCRYPT=yes;
        TrustServerCertificate=yes;
    """
    return pyodbc.connect(connection_string, timeout=10)

def get_mimiciv_db_connection():
    conf = get_config('mimic_database')
    connection_string = f"""
        DRIVER={{{conf['driver']}}};
        SERVER={conf['server']};
        DATABASE={conf['database']};
        UID={conf['uid']};
        PWD={conf['password']};
        Authentication=ActiveDirectoryInteractive;
        ENCRYPT=yes;
        TrustServerCertificate=yes;
    """
    return pyodbc.connect(connection_string, timeout=10)
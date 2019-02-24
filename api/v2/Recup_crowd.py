# coding: utf-8
import requests
import pandas as pd
from io import BytesIO
import requests
import psycopg2
import io
from sqlalchemy import create_engine
from konnect_polen import *
host='localhost:5433'
engine = create_engine('postgresql://'+configuration_db_user_localhost+':'+configuration_db_pass_localhost+'@'+host+'/mehdi.guiraud',encoding='utf-8')



def unload_crow_work_google():
    r = requests.get('https://docs.google.com/spreadsheets/d/e/2PACX-1vQhYVTsFV_Nsd2eKVWG8xfX3aJ5WQHvVBexaJQzq4BpUjFGk7aZImG02xNMOL7sb9HxrqV1kJ2Q6tYx/pub?output=csv')
    data = r.content
    df = pd.read_csv(BytesIO(data))
    df.to_sql('crowd_lex',engine, if_exists='replace', index=False)

if __name__ == '__main__':
   unload_crow_work_google()

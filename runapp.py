# start django dev server in one thread and lunch chrome in another

import os
from threading import Thread
from time import sleep
def runserver():
    os.system('start /min python manage.py runserver')

def lunchchrome():
    os.system('start chrome http://localhost:8000')

t1=Thread(target=runserver)
sleep(5)
t2=Thread(target=lunchchrome)

t1.start()
t2.start()



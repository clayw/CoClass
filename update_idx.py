import os
import time
ctr = 0
while True:
    os.system("python manage.py update_index")
    time.sleep(30)

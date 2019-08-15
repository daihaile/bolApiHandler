import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
import pprint as pp
import datetime
import time

now = datetime.datetime.now()
then = now + datetime.timedelta(minutes = 2)
diff = (then-now).total_seconds()

print(now)
print(then)

while True:
    now = datetime.datetime.now()
    diff = (then-now).total_seconds()
    if diff < 20:
        print(diff)
        print("kleiner 20")
        break
    else:
        print(diff)
        print("größer 20") 
        time.sleep(1)


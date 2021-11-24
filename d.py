import json
import os
import time
import random
import numpy as np
d=[]
while (True):
    p=random.randint(0, 20)
    d.append(p)

    if len(d)==10:
        print(d)
        a=np.max(d)
        d.clear()
        print("max:",a)

    time.sleep(0.2 )
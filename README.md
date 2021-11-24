# branch cloud_componen
Codes for cloud components, running on cloud (or on another PC that does not neccesarily has access to your RPi). Note that in this branch the client (we just use flask_mqtt here) in `app.py` need to connect and send/receive data to the broker on cloud, but unfortunately because I ran out my credits on Azure(where I deploy the broker and other cloud component) I can not keep the cloud broker always running. So if you clone this repo you can't directly run it, instead you need to change the configuration of the mqtt client connection to make it connect to your own cloud broker.

# Setup if you want to run clouds components just on another PC.

First, make sure that the camera & deeplearning for people detection component from branch `main` is running (`publisher\cam.py`), and change the configuration of the mqtt client in `app.py` connection to make it connect to your own cloud broker.



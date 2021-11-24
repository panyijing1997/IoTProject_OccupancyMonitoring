# StudySpaceMonitoring

Study Space Occupancy Monitoring -- Project for the course Building the Internet of Things with P2P and Cloud Computing

# Branches:

- branch `main` : Codes that should run on RPi. Note that in this branch one client need to connect and send data to the broker on cloud, but unfortunately because I ran out my credits on Azure (where I deploy the broker and other cloud component) I can not keep the cloud broker always running. So if you clone this repo you can't directly run it, instead you need to first change the configuration of the client (`c_cloud` in `publisher\cam.py`) which needs to connect to a cloud broker to make it connect to your own broker.

- branch `cloud_component`: Codes for cloud components, running on cloud (or on another PC that does not neccesarily has access to your RPi). Note that in this branch the client (we just use flask_mqtt here) in `app.py` need to connect and send/receive data to the broker on cloud, but unfortunately because I ran out my credits on Azure(where I deploy the broker and other cloud component) I can not keep the cloud broker always running. So if you clone this repo you can't directly run it, instead you need to change the configuration of the mqtt client connection to make it connect to your own broker.

- branch `pure_local` : In this branch, everything runs locally, all clients only connect to the local broker but not the cloud broker. You should be able to run this directly on your RPi.

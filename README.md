# branch cloud_componen
Codes for cloud components, running on cloud (or on another PC that does not neccesarily has access to your RPi). Note that in this branch the client (we just use flask_mqtt here) in `app.py` need to connect and send/receive data to the broker on cloud, but unfortunately because I ran out my credits on Azure(where I deploy the broker and other cloud components) I can not keep the cloud broker always running. So if you clone this repo you can't directly run it, instead you need to change the configuration of the mqtt client connection to make it connect to your own cloud broker.

Cloud component url: queenchrysalisproject.northeurope.azurecontainer.io

Note: it is disabled, because I ran out my free credits on Azure so I can't keep it running 24/7. If you want to have a look please contact me so that I can lauch it for a short time.

# Setup if you want to run cloud components just on another PC (which has no access to your RPi)

First, make sure that the camera & deeplearning for people detection component from branch `main` is running (`publisher\cam.py`), and change the configuration of the mqtt client in `app.py` in this branch connection to make it connect to your own cloud broker. 

If `publisher\cam.py` from the branch `main` is not running, then no clients publish new data, so you can only see histric data and you can't check live photo.

### switch to this branch, build and run the docker image.

```shell
$ git checkout cloud_component
$ docker build -t cloud .
$ docker run -p 80:80 cloud.
```
Then visit `localhost` in your broswer.


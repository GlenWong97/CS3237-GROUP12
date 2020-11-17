import paho.mqtt.client as mqtt
import json
import time
import os
from dotenv import load_dotenv

def setup(hostname):
    USERID = "permasteo"
    PASSWORD = os.getenv("REACT_APP_EC2_PASSWORD")    

    client = mqtt.Client()
    client.username_pw_set(USERID, PASSWORD)
    client.on_connect = on_connect
    client.connect(hostname, port=1883)
    client.loop_start()
    return client

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected")
    else:
        print("Failed to connect. Error code: %d." % rc)

if __name__ == '__main__':
    load_dotenv()

    # Setting MQTT Client
    mqtt_client = setup("13.229.102.188")

    # time.sleep(1)

    result = {
        "Prediction" : "NOD",
        "Shown" : "IDLE",
        "batterylife" : 60
    }
    
    # Publish
    mqtt_client.publish("Group_12/LSTM/predict/Glen", json.dumps(result))

    ### IMPORTANT: sometimes prevent publish when not called
    mqtt_client.loop_stop()


import json
import numpy as np
import tensorflow as tf
import paho.mqtt.client as mqtt

from time import time
from keras.models import load_model
from tensorflow.python.keras.backend import set_session

MODEL_NAME = 'lstm_model.hd5'
loaded_model = None

prediction, temp_predict = '', ''
predict_time = 0.0

session = tf.compat.v1.Session(graph=tf.compat.v1.Graph())
action = {0: 'Nod', 1: 'Shake'}
PREVIOUS_SHOWN = ''
# When calling load_model


def loading_model():
    with session.graph.as_default():
        set_session(session)
        global loaded_model
        loaded_model = load_model(MODEL_NAME)
        print("Model loaded, ready to predict")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Successfully connected to broker")
        print("Loading model... Do not send data!")
        client.subscribe("Group_12/LSTM/classify/Sean")
    else:
        print("Connection failed with code: %d." % rc)


def output_to_user():
    global prediction, temp_predict, predict_time

    if prediction == 'IDLE':
        if temp_predict != 'IDLE':
            if time() - predict_time < 5:
                return temp_predict
            else:
                temp_predict = 'IDLE'
                return prediction
        else:
            return temp_predict
    else:
        temp_predict = prediction
        predict_time = time()
        return temp_predict

# When predicting


def predict(motion_data):
    with session.graph.as_default():
        set_session(session)
        # print("Start classifying")
        global loaded_model, prediction
        result = loaded_model.predict(motion_data)
        themax = np.argmax(result[0])
        confidence = 0.93
        if (result[0][themax] < confidence):
            prediction = 'IDLE'
        else:
            prediction = action[themax]
        # print("Done.")
        shown = output_to_user()
    return {"Prediction": prediction, "Shown": shown}


def on_message(client, userdata, msg):
    # Payload is in msg. We convert it back to a Python dictionary.
    recv_dict = json.loads(msg.payload)
    global PREVIOUS_SHOWN
    # Recreate the data
    motion_data = np.array(recv_dict["data"])
    battery_reading = recv_dict["batterylife"]
    result = predict(motion_data)
    if result["Shown"] != PREVIOUS_SHOWN:
        print("Sending results: ", result)
        result["batterylife"] = battery_reading
        # Select your topic by uncommenting and commenting
        # client.publish("Group_12/LSTM/predict/Glen", json.dumps(result))
        client.publish("Group_12/LSTM/predict/Sean", json.dumps(result))
        # client.publish("Group_12/LSTM/predict/Nicholas", json.dumps(result))
    PREVIOUS_SHOWN = result["Shown"]


def setup(hostname):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(hostname)
    client.loop_start()
    return client


def main():
    setup("test.mosquitto.org")
    with session.graph.as_default():
        set_session(session)
        loading_model()
    while True:
        pass


if __name__ == '__main__':
    main()

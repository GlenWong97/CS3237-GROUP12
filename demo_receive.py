import numpy as np
import json
import paho.mqtt.client as mqtt
import tensorflow as tf

from PIL import Image
from os import listdir
from os.path import join
from keras.models import load_model
from tensorflow.python.keras.backend import set_session

MODEL_NAME='lstm_model.hd5'
loaded_model = None

session = tf.compat.v1.Session(graph=tf.compat.v1.Graph())

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
		client.subscribe("Group_12/LSTM")
	else:
		print("Connection failed with code: %d." % rc)

# When predicting
def predict(motion_data):
	with session.graph.as_default():
		set_session(session)
		print("Start classifying")
		global loaded_model
		result = loaded_model.predict(motion_data)
		themax = numpy.argmax(result[0])
		confidence = 0.93
		if (result[0][themax] < confidence):
			prediction = 'IDLE'
		else:
			prediction = dict[themax]
		print("Done.")
	return {"Prediction": prediction}

def on_message(client, userdata, msg):
	# Payload is in msg. We convert it back to a Python dictionary.
	recv_dict = json.loads(msg.payload)

	# Recreate the data
	motion_data = np.array(recv_dict["data"])
	result = predict(motion_data)
	print("Sending results: ", result)
	client.publish("Group_12/LSTM", json.dumps(result))

def setup(hostname):
	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message
	client.connect(hostname)
	client.loop_start()
	return client

def main():
	setup("127.0.0.1")
	with session.graph.as_default():
		set_session(session)
		loading_model()
	while True:
		pass

if __name__ == '__main__':
	main()
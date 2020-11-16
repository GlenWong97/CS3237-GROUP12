# CS3237 AY20/21  Team 12 Project Repository
## Gesture recognition using LSTM

## Team
- Glen Wong Shu Ze
- Lim Hao Xiang, Sean
- Liu Wei Jie Nicholas
- Permas Teo Pek Neng

## Instructions

### Setting up the environment
1. Create a virtual environment called venv: `python -m venv venv`
2. Activate the environment: `.\venv\Scripts\activate`
3. Install all requirements by executing: `pip3 install -r install.requirements`
4. Exit virtual environment: `deactivate`

### Running React App
1. Change directory to frontendV2: `cd frontendV2` 
2. To install: `npm install`
3. To run: `npm start`

### Setting up of the cc2650 device
1. Please make sure your device is not paired with any device at the moment; this includes closing the SensorTag app on your phone after use.
2. Please make sure you reset your SensorTag device to factory settings using the instructions at
[TI Sensor Tag User Guide ](https://processors.wiki.ti.com/index.php/CC2650_SensorTag_User's_Guide#Firmware_Upgrade); This UI option is only available in Windows;

### Running the live prediction code
1. Open a command prompt
2. At the root directory, change directory to demo folder: `cd src/demo`
3. Start MQTT broker (or server): `python demo_receive.py`
4. Open a new command prompt
5. At the root directory, change directory to demo folder: `cd src/demo`
6. Start MQTT client: `python demo_send.py`

## Notes


## Credits
1. https://github.com/hbldh/bleak/tree/develop/examples
2. https://github.com/IanHarvey/bluepy/blob/a7f5db1a31dba50f77454e036b5ee05c3b7e2d6e/bluepy/sensortag.py
3. [TI SensorTag User Guide # GATT Server](https://processors.wiki.ti.com/index.php/CC2650_SensorTag_User's_Guide#Gatt_Server)
4. Skeletal Code Reference for MQTT React App: (https://www.preciouschicken.com/blog/posts/a-taste-of-mqtt-in-react/).
5. This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).   
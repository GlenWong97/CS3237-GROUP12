import numpy as np
import os
from numpy import mean
from numpy import std
from numpy import dstack
from pandas import read_csv
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers import Dropout
from keras.layers import LSTM
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.models import Sequential, load_model
from matplotlib import pyplot

MODEL_NAME = 'hand_model.hd5'

# number of classes to classify, for now is 4 (nod, shake, up, tilt)
NUM_CLASSES = 4


def load_file(filepath):
    dataframe = read_csv(filepath, header=None, delim_whitespace=False)
    return dataframe.values

# load a list of files and return as a 3d numpy array


def load_group(filenames, prefix=''):
    loaded = list()
    for name in filenames:
        data = load_file(prefix + name)
        loaded.append(data)
    # stack group so that features are the 3rd dimension
    loaded = dstack(loaded)
    return loaded


# load a dataset group, such as train or test
def load_dataset_group(group, prefix=''):
    # # filepath: /ProjectData/IndividualSignals
    # filepath = prefix + 'IndividualSignals\\'

    filepath = prefix + group + '/IndividualSignals/'
    # load all 9 files as a single array
    filenames = list()
    # acceleration
    filenames += ['acc_x_'+group+'.csv', 'acc_y_' +
                  group+'.csv', 'acc_z_'+group+'.csv']
    # body gyroscope
    filenames += ['gyro_x_'+group+'.csv', 'gyro_y_' +
                  group+'.csv', 'gyro_z_'+group+'.csv']
    # magnetometer
    filenames += ['mag_x_'+group+'.csv', 'mag_y_' +
                  group+'.csv', 'mag_z_'+group+'.csv']
    # barometer
    filenames += ['baro_'+group+'.csv']
    # load input data
    X = load_group(filenames, filepath)
    # load class output
    y = load_file(prefix + group + '/y_'+group+'.csv')
    return X, y

# using train test split
def load_dataset(prefix=''):
    # load all train
    all_X, all_y = load_dataset_group('train', prefix + 'ProjectData/')
    print(f"all_X shape: {all_X.shape}, all_y shape: {all_y.shape}")

    trainX, testX, trainy, testy = train_test_split(all_X, all_y, test_size= 0.3)
    print(f"trainX shape: {trainX.shape}, trainy shape: {trainy.shape}, testX shape: {testX.shape}, testy shape: {testy.shape}")
    # zero-offset class values
    trainy = trainy
    testy = testy
    # one hot encode y
    trainy = to_categorical(trainy, num_classes=NUM_CLASSES)
    testy = to_categorical(testy, num_classes=NUM_CLASSES)
    print(f"trainX shape: {trainX.shape}, trainy shape: {trainy.shape}, testX shape: {testX.shape}, testy shape: {testy.shape}")
    return trainX, trainy, testX, testy

# fit and evaluate a model
def train_lstm(model, train_x, train_y, epochs, test_x, test_y, model_name):

    model.compile(loss='categorical_crossentropy',
                  optimizer='adam', metrics=['accuracy'])

    savemodel = ModelCheckpoint(model_name)
    stopmodel = EarlyStopping(min_delta=0.001, patience=10)

    print("Starting training.")

    model.fit(x=train_x, y=train_y, batch_size=64,
              validation_data=(test_x, test_y), shuffle=True,
              epochs=epochs,
              callbacks=[savemodel, stopmodel])

    print("Done. Now evaluating.")
    loss, acc = model.evaluate(x=test_x, y=test_y)
    print("Test accuracy: %3.2f, loss: %3.2f" % (acc, loss))


def buildlstm(model_name, trainX, trainy, testX, testy):
    if os.path.exists(model_name):
        model = load_model(model_name)
        print("loaded model")
    else:
        n_timesteps, n_features, n_outputs = trainX.shape[1], trainX.shape[2], trainy.shape[1]
        model = Sequential()
        model.add(LSTM(200, input_shape=(n_timesteps, n_features)))
        model.add(Dropout(0.1))
        model.add(Dense(500, activation='relu'))
        model.add(Dropout(0.1))
        model.add(Dense(800, activation='relu'))
        model.add(Dropout(0.1))
        model.add(Dense(1000, activation='relu'))
        model.add(Dropout(0.1))
        model.add(Dense(1000, activation='relu'))
        model.add(Dropout(0.1))
        model.add(Dense(500, activation='relu'))
        model.add(Dropout(0.1))
        model.add(Dense(100, activation='relu'))
        model.add(Dropout(0.1))
        model.add(Dense(n_outputs, activation='softmax'))
    return model

# def buildlstm(model_name, trainX, trainy, testX, testy):
#     if os.path.exists(model_name):
#         model = load_model(model_name)
#     else:
#         n_timesteps, n_features, n_outputs = trainX.shape[1], trainX.shape[2], trainy.shape[1]
#         model = Sequential()
#         model.add(LSTM(100, input_shape=(n_timesteps, n_features)))
#         model.add(Dropout(0.5))
#         model.add(Dense(100, activation='relu'))
#         model.add(Dense(n_outputs, activation='softmax'))
#     return model

# run an experiment
def run_experiment(repeats=10):
    # load data
    trainX, trainy, testX, testy = load_dataset()
    model = buildlstm(MODEL_NAME, trainX, trainy, testX, testy)
    print(f"shape of trainy: {trainy.shape}")
    train_lstm(model, trainX, trainy, 100, testX, testy, MODEL_NAME)


# run the experiment
run_experiment()

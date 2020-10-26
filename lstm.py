import numpy as np
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
from matplotlib import pyplot

# file structure for data required:
# /ProjectData
# 	train
# 		y_train.csv
# 		/IndividualSignals
# 			acc_x_train.csv
# 			acc_y_train.csv
# 			acc_z_train.csv
# 			gyro_x_train.csv
# 			gyro_y_train.csv
# 			gyro_z_train.csv
# 			mag_x_train.csv
# 			mag_y_train.csv
# 			mag_z_train.csv
# 			baro_train.csv
# 	test
# 		y_test.csv
# 		/IndividualSignals
# 			acc_x_test.csv
# 			acc_y_test.csv
# 			acc_z_test.csv
# 			gyro_x_test.csv
# 			gyro_y_test.csv
# 			gyro_z_test.csv
# 			mag_x_test.csv
# 			mag_y_test.csv
# 			mag_z_test.csv
# 			baro_test.csv


# load a single file as a numpy array

def load_file(filepath):
    dataframe = read_csv(filepath, header=None, delim_whitespace=False)
    # print(dataframe)
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


# load the dataset, returns train and test X and y elements

def load_dataset(prefix=''):
    # load all train
    trainX, trainy = load_dataset_group('train', prefix + 'ProjectData/')
    # print(trainX.shape, trainy.shape)
    
    # load all test
    testX, testy = load_dataset_group('test', prefix + 'ProjectData/')
    # print(testX.shape, testy.shape)
    # zero-offset class values
    # print("trainy.shape (before zero-offset): {}".format(trainy))
    # print("testy.shape (before zero-offset): {}".format(testy))
    trainy = trainy - 1
    testy = testy - 1
    # one hot encode y
    # print("trainy.shape (after zero-offset): {}".format(trainy))
    # print("testy.shape (after zero-offset): {}".format(testy))
    trainy = to_categorical(trainy , num_classes=2)
    testy = to_categorical(testy, num_classes=2)
    # print("trainX.shape: {}".format(trainX.shape))
    # print("trainy.shape: {}".format(trainy))
    # print("testX.shape: {}".format(testX.shape))
    # print("testy.shape: {}".format(testy))
    # print("n_timesteps, n_features, n_outputs", trainX.shape[1], trainX.shape[2], trainy.shape[1])
    return trainX, trainy, testX, testy


# fit and evaluate a model

def evaluate_model(trainX, trainy, testX, testy):
    verbose, epochs, batch_size = 0, 15, 1
#     verbose, epochs, batch_size = 0, 15, 3
    n_timesteps, n_features, n_outputs = trainX.shape[1], trainX.shape[2], trainy.shape[1]
    model = Sequential()
    model.add(LSTM(100, input_shape=(n_timesteps, n_features)))
    model.add(Dropout(0.5))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(n_outputs, activation='softmax'))
    model.compile(loss='categorical_crossentropy',
                  optimizer='adam', metrics=['accuracy'])
    # fit network
    model.fit(trainX, trainy, epochs=epochs,
              batch_size=batch_size, verbose=verbose)
    # evaluate model
    _, accuracy = model.evaluate(
        testX, testy, batch_size=batch_size, verbose=0)
    return accuracy


# summarize scores

def summarize_results(scores):
    print(scores)
    m, s = mean(scores), std(scores)
    print('Accuracy: %.3f%% (+/-%.3f)' % (m, s))


# run an experiment

def run_experiment(repeats=10):
    # load data
    trainX, trainy, testX, testy = load_dataset()
    print(type(trainX[0][0][0]))
    # repeat experiment
    scores = list()
    for r in range(repeats):
        score = evaluate_model(trainX, trainy, testX, testy)
        score = score * 100.0
        print('>#%d: %.3f' % (r+1, score))
        scores.append(score)
    # summarize results
    summarize_results(scores)


# run the experiment
run_experiment()

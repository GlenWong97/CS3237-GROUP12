import numpy as np
import os
from numpy import mean
from numpy import std
from numpy import dstack
from pandas import read_csv
from matplotlib import pyplot


def load_file(filepath):
    dataframe = read_csv(filepath, header=None, delim_whitespace=False)
    return dataframe.values


x = load_file('ProjectData/train/IndividualSignals/acc_x_train.csv')
print(x)

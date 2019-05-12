#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Authors:
#     Jason Brownlee
#     Alvaro del Castillo <alvaro.delcastillo@gmail.com>
#
# Based on:
# Jason Brownlee, Machine Learning Algorithms in Python, Machine Learning Mastery, accessed May 12th, 2019.
# Available from:
# https://machinelearningmastery.com/how-to-develop-a-cnn-from-scratch-for-fashion-mnist-clothing-classification

# You need to install python3-tk in the host system

# example of loading the fashion mnist dataset
import sys

from keras.datasets import fashion_mnist
from keras.layers import Conv2D
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers import MaxPooling2D
from keras.models import Sequential
from keras.optimizers import SGD
from keras.utils import to_categorical

from matplotlib import pyplot

from numpy import mean
from numpy import std

from sklearn.model_selection import KFold

# TODO
# - Show progress during model training


# load train and test dataset
def load_dataset():
    # load dataset
    (train_x, train_y), (test_x, test_y) = fashion_mnist.load_data()
    # reshape dataset to have a single channel
    train_x = train_x.reshape((train_x.shape[0], 28, 28, 1))
    test_x = test_x.reshape((test_x.shape[0], 28, 28, 1))
    # one hot encode target values
    train_y = to_categorical(train_y)
    test_y = to_categorical(test_y)
    return train_x, train_y, test_x, test_y


# scale pixels in [0,1] range so it is easier to rescale later
def prep_pixels(train, test):
    # convert from integers to floats
    train_norm = train.astype('float32')
    test_norm = test.astype('float32')
    # normalize to range 0-1
    train_norm = train_norm / 255.0
    test_norm = test_norm / 255.0
    # return normalized images
    return train_norm, test_norm


# evaluate a model using k-fold cross-validation
def evaluate_model(model, data_x, data_y, n_folds=5):
    scores, histories = list(), list()
    # prepare cross validation
    kfold = KFold(n_folds, shuffle=True, random_state=1)
    # enumerate splits
    for train_ix, test_ix in kfold.split(data_x):
        # select rows for train and test
        train_x, train_y, test_x, test_y = data_x[train_ix], data_y[train_ix], data_x[test_ix], data_y[test_ix]
        # fit model
        history = model.fit(train_x, train_y, epochs=10, batch_size=32, validation_data=(test_x, test_y), verbose=0)
        # evaluate model
        _, acc = model.evaluate(test_x, test_y, verbose=0)
        print('> %.3f' % (acc * 100.0))
        # stores scores
        scores.append(acc)
        histories.append(history)
    return scores, histories


# Define cnn model
def build_model():
    model = Sequential()
    model.add(Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_uniform', input_shape=(28, 28, 1)))
    model.add(MaxPooling2D((2, 2)))
    model.add(Flatten())
    model.add(Dense(100, activation='relu', kernel_initializer='he_uniform'))
    model.add(Dense(10, activation='softmax'))
    # compile model
    opt = SGD(lr=0.01, momentum=0.9)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


# plot diagnostic learning curves
def summarize_diagnostics(histories):
    for i in range(len(histories)):
        # plot loss
        pyplot.subplot(211)
        pyplot.title('Cross Entropy Loss')
        pyplot.plot(histories[i].history['loss'], color='blue', label='train')
        pyplot.plot(histories[i].history['val_loss'], color='orange', label='test')
        # plot accuracy
        pyplot.subplot(212)
        pyplot.title('Classification Accuracy')
        pyplot.plot(histories[i].history['acc'], color='blue', label='train')
        pyplot.plot(histories[i].history['val_acc'], color='orange', label='test')
    pyplot.show()


# summarize model performance
def summarize_performance(scores):
    # print summary
    print('Accuracy: mean=%.3f std=%.3f, n=%d' % (mean(scores) * 100, std(scores) * 100, len(scores)))
    # box and whisker plots of results
    pyplot.boxplot(scores)
    pyplot.show()

def load_show_images():
    # Test
    # load dataset
    (train_x, trainy), (test_x, test_y) = fashion_mnist.load_data()
    # summarize loaded dataset
    print('Train: x=%s, y=%s' % (train_x.shape, trainy.shape))
    print('Test: x=%s, y=%s' % (test_x.shape, test_y.shape))
    # plot first few images
    for i in range(9):
        # define subplot
        pyplot.subplot(330 + 1 + i)
        # plot raw pixel data
        pyplot.imshow(train_x[i], cmap=pyplot.get_cmap('gray'))
    # show the figure
    pyplot.show()


# run the test harness for evaluating a model
def run_test_harness():
    # load dataset
    train_x, train_y, test_x, test_y = load_dataset()
    # prepare pixel data
    train_x, test_x = prep_pixels(train_x, test_x)
    # define model
    model = build_model()
    # evaluate model
    scores, histories = evaluate_model(model, train_x, train_y)
    # learning curves
    summarize_diagnostics(histories)
    # summarize estimated performance
    summarize_performance(scores)


def main():
    print("Starting DL fashion sample")

    # Load the Fashion MNIST dataset and show a sample of them
    # load_show_images()
    run_test_harness()

    print("All done")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        s = "\n\nReceived Ctrl-C or other break signal. Exiting.\n"
        sys.stderr.write(s)
        sys.exit(0)
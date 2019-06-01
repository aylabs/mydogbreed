#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Alvaro del Castillo
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, 51 Franklin Street, Fifth Floor, Boston, MA 02110-1335, USA.
#
# Authors:
#     Alvaro del Castillo <alvaro.delcastillo@gmail.com>
#
# TODO: All this code are mainly notebooks extracted and pasted here. It needs a refactor once it is consolidated.


import argparse
import logging
import sys

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

from sklearn.preprocessing import OneHotEncoder

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

MLSAMPLES_USAGE_MSG = \
    """%(prog)s [-g] [<args>] | --help"""

MLSAMPLES_DESC_MSG = \
    """Machine learning samples."""

MLSAMPLES_EPILOG_MSG = \
    """Run '%(prog)s --help' to show the help for using the program."""

# Logging formats
MLSAMPLES_LOG_FORMAT = "[%(asctime)s] - %(message)s"
MLSAMPLES_DEBUG_LOG_FORMAT = "[%(asctime)s - %(name)s - %(levelname)s] - %(message)s"

# Pre-trained model to be used
MODELS_DIR = "models"
RESNET_DIR = MODELS_DIR + "/resnet50"
RESNET_H5 = RESNET_DIR + "/resnet50_weights_tf_dim_ordering_tf_kernels.h5"
RESNET_JSON = RESNET_DIR + "/imagenet_class_index.json"

DATA_DIR = "data"

IMAGES_DIR = "images"
IMAGE_DIR_TRAIN = IMAGES_DIR + "/train/"
IMAGE_DIR_TEST = IMAGES_DIR + "/test/"


def configure_logging(debug=True):
    """Configure MyMLSAMPLES logging
    The function configures the log messages produced by machine_learning.py.
    By default, log messages are sent to stderr. Set the parameter
    `debug` to activate the debug mode.
    :param debug: set the debug mode
    """
    if not debug:
        logging.basicConfig(level=logging.INFO,
                            format=MLSAMPLES_LOG_FORMAT)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('urrlib3').setLevel(logging.WARNING)
    else:
        logging.basicConfig(level=logging.DEBUG,
                            format=MLSAMPLES_DEBUG_LOG_FORMAT)


def parse_args():
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(usage=MLSAMPLES_USAGE_MSG,
                                     description=MLSAMPLES_DESC_MSG,
                                     epilog=MLSAMPLES_EPILOG_MSG,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     add_help=False)

    parser.add_argument('-h', '--help', action='help',
                        help=argparse.SUPPRESS)

    return parser.parse_args()


# Function for comparing different models
def score_model(model, x_train, x_valid, y_train, y_valid):
    from sklearn.metrics import mean_absolute_error

    model.fit(x_train, y_train)
    preds = model.predict(x_valid)
    return mean_absolute_error(y_valid, preds)


# Function for comparing different approaches
def score_dataset(x_train, x_valid, y_train, y_valid):
    model = RandomForestRegressor(n_estimators=100, random_state=0)
    model.fit(x_train, y_train)
    preds = model.predict(x_valid)
    return mean_absolute_error(y_valid, preds)


def impute_data(x_train, x_valid, strategy="mean"):
    """
    Fill the null values with imputed values
    :param x_train: data for training
    :param x_valid: data for validation
    :param strategy: strategy to fill the gaps ('mean', 'median', 'most_frequent', 'constant')
    :return: the non empty data for training  and validation
    """

    # Imputation
    my_imputer = SimpleImputer(strategy=strategy)
    imputed_x_train = pd.DataFrame(my_imputer.fit_transform(x_train))
    imputed_x_valid = pd.DataFrame(my_imputer.transform(x_valid))

    # Imputation removed column names; put them back
    imputed_x_train.columns = x_train.columns
    imputed_x_valid.columns = x_valid.columns

    return imputed_x_train, imputed_x_valid


def handle_missing_values():
    # The goal is to show the different strategies for handling features with missing values
    # Strategies: drop the feature values (column), fill with a default value (imputation) and imputation+mark it

    # Read the data
    x_full = pd.read_csv(DATA_DIR + '/input/home-data-for-ml-course/train.csv', index_col='Id')
    x_test_full = pd.read_csv(DATA_DIR + '/input/home-data-for-ml-course/test.csv', index_col='Id')

    # Remove rows with missing target, separate target from predictors
    x_full.dropna(axis=0, subset=['SalePrice'], inplace=True)
    y = x_full.SalePrice
    x_full.drop(['SalePrice'], axis=1, inplace=True)

    # To keep things simple, we'll use only numerical predictors
    X = x_full.select_dtypes(exclude=['object'])
    x_test = x_test_full.select_dtypes(exclude=['object'])

    # Break off validation set from training data
    x_train, x_valid, y_train, y_valid = train_test_split(X, y, train_size=0.8, test_size=0.2,
                                                          random_state=0)

    # Drop columns with missing values
    cols_with_missing = [col for col in x_train.columns
                         if x_train[col].isnull().any()]

    # Fill in the lines below: drop columns in training and validation data
    reduced_x_train = x_train.drop(cols_with_missing, axis=1)
    reduced_x_valid = x_valid.drop(cols_with_missing, axis=1)

    print("MAE (Drop columns with missing values):")
    print(score_dataset(reduced_x_train, reduced_x_valid, y_train, y_valid))

    # Imputation
    imputed_x_train, imputed_x_valid = impute_data(x_train, x_valid)
    print("MAE (Imputation default):")
    print(score_dataset(imputed_x_train, imputed_x_valid, y_train, y_valid))

    # Check with another strategy for Imputation
    final_x_train, final_x_valid = impute_data(x_train, x_valid, 'median')
    print("MAE (Imputation median):")
    print(score_dataset(final_x_train, final_x_valid, y_train, y_valid))

    # Check with another strategy for Imputation
    final_x_train, final_x_valid = impute_data(x_train, x_valid, 'most_frequent')
    print("MAE (Imputation most_frequent):")
    print(score_dataset(final_x_train, final_x_valid, y_train, y_valid))


def kaggle_sample2_ml():
    # Predict house prices for Ames, Iowa
    # https://www.kaggle.com/learn/intermediate-machine-learning

    # Data from: https://www.kaggle.com/c/home-data-for-ml-course/data
    # Read the data
    x_full = pd.read_csv(DATA_DIR + '/input/home-data-for-ml-course/train.csv', index_col='Id')
    x_test_full = pd.read_csv(DATA_DIR + '/input/home-data-for-ml-course/test.csv', index_col='Id')

    # Obtain target and predictors
    print(x_full.columns)

    y = x_full.SalePrice
    features = ['LotArea', 'YearBuilt', '1stFlrSF', '2ndFlrSF', 'FullBath', 'BedroomAbvGr', 'TotRmsAbvGrd']
    features += ['KitchenAbvGr']
    X = x_full[features].copy()
    x_test = x_test_full[features].copy()

    # Break off validation set from training data
    x_train, x_valid, y_train, y_valid = train_test_split(X, y, train_size=0.8, test_size=0.2,
                                                          random_state=0)
    print(x_train.head())

    # Evaluate several models
    from sklearn.ensemble import RandomForestRegressor

    # Define the models
    model_1 = RandomForestRegressor(n_estimators=50, random_state=0)
    model_2 = RandomForestRegressor(n_estimators=100, random_state=0)
    model_3 = RandomForestRegressor(n_estimators=100, criterion='mae', random_state=0)
    model_4 = RandomForestRegressor(n_estimators=200, min_samples_split=20, random_state=0)
    model_5 = RandomForestRegressor(n_estimators=100, max_depth=7, random_state=0)

    models = [model_1, model_2, model_3, model_4, model_5]

    print("Evaluating between different RandomForestRegressor")
    for i in range(0, len(models)):
        mae = score_model(models[i], x_train, x_valid, y_train, y_valid)
        print("Model %d MAE: %d" % (i + 1, mae))

    model_31 = RandomForestRegressor(n_estimators=80, criterion='mae', random_state=0)
    model_32 = RandomForestRegressor(n_estimators=100, criterion='mae', random_state=0)
    model_33 = RandomForestRegressor(n_estimators=110, criterion='mae', random_state=0)
    model_34 = RandomForestRegressor(n_estimators=120, criterion='mae', random_state=0)
    model_35 = RandomForestRegressor(n_estimators=130, criterion='mae', random_state=0)
    model_36 = RandomForestRegressor(n_estimators=200, criterion='mae', random_state=0)
    model_37 = RandomForestRegressor(n_estimators=300, criterion='mae', random_state=0)

    models3 = [model_31, model_32, model_33, model_34, model_35, model_36, model_37]

    print("Evaluating in the same RandomForestRegressor with <>n_estimators")
    for i in range(0, len(models3)):
        mae = score_model(models3[i], x_train, x_valid, y_train, y_valid)
        print("Model %d MAE: %d" % (i + 1, mae))

    my_model = model_3

    # Fit the model to the training data: all train and validation
    my_model.fit(X, y)

    # Generate test predictions
    preds_test = my_model.predict(x_test)

    # Save predictions in format used for competition scoring
    output = pd.DataFrame({'Id': x_test.index,
                           'SalePrice': preds_test})
    output.to_csv('submission.csv', index=False)


def kaggle_sample_ml():
    from sklearn.tree import DecisionTreeRegressor

    # Sample on predicting houses prices with ML
    # https://www.kaggle.com/dansbecker/melbourne-housing-snapshot/downloads/melb_data.csv/5
    melbourne_file_path = DATA_DIR + '/input/melbourne-housing-snapshot/melb_data.csv'
    melbourne_data = pd.read_csv(melbourne_file_path)
    print(melbourne_data.columns)
    # dropna drops missing values (think of na as "not available")
    melbourne_data = melbourne_data.dropna(axis=0)
    y = melbourne_data.Price
    melbourne_features = ['Rooms', 'Bathroom', 'Landsize', 'Lattitude', 'Longtitude']
    X = melbourne_data[melbourne_features]
    print(X.describe())
    print(X.head())

    # Define model. Specify a number for random_state to ensure same results each run
    melbourne_model = DecisionTreeRegressor(random_state=1)
    # Fit model
    melbourne_model.fit(X, y)
    print("Making predictions for the following 5 houses:")
    print(X.head())
    print("The predictions are")
    print(melbourne_model.predict(X.head()))
    from sklearn.metrics import mean_absolute_error
    predicted_home_prices = melbourne_model.predict(X)
    # MAE
    print(mean_absolute_error(y, predicted_home_prices))
    # Let's use some data to train some to validate
    from sklearn.model_selection import train_test_split
    # split data into training and validation data, for both features and target
    # The split is based on a random number generator. Supplying a numeric value to
    # the random_state argument guarantees we get the same split every time we
    # run this script.
    train_X, val_X, train_y, val_y = train_test_split(X, y, random_state=0)
    melbourne_model = DecisionTreeRegressor()
    melbourne_model.fit(train_X, train_y)
    val_predictions = melbourne_model.predict(val_X)
    print(mean_absolute_error(val_y, val_predictions))

    # Play with different models to find the best one
    def get_mae(max_leaf_nodes, train_X, val_X, train_y, val_y):
        model = DecisionTreeRegressor(max_leaf_nodes=max_leaf_nodes, random_state=0)
        model.fit(train_X, train_y)
        preds_val = model.predict(val_X)
        mae = mean_absolute_error(val_y, preds_val)
        return (mae)

    for max_leaf_nodes in [5, 50, 500, 5000]:
        my_mae = get_mae(max_leaf_nodes, train_X, val_X, train_y, val_y)
        print("Max leaf nodes: %d  \t\t Mean Absolute Error:  %d" % (max_leaf_nodes, my_mae))

    from sklearn.ensemble import RandomForestRegressor
    forest_model = RandomForestRegressor(random_state=1)
    forest_model.fit(train_X, train_y)
    melb_preds = forest_model.predict(val_X)
    print(mean_absolute_error(val_y, melb_preds))


def kaggle_digit_dl():
    # Detecting hand written digits
    # A new model is created from scratch
    # The model can be improved changing: number of layers,
    # kernel_size or filter in the convolution layers
    # Download test data from:
    # https://www.kaggle.com/c/digit-recognizer/download/test.csv
    #

    from sklearn.model_selection import train_test_split
    from tensorflow.python import keras
    from tensorflow.python.keras.models import Sequential
    from tensorflow.python.keras.layers import Dense, Flatten, Conv2D, Dropout

    DIR_TRAIN = IMAGES_DIR + "/train/"
    # DIR_TEST = IMAGES_DIR + "/digits/test/"

    img_rows, img_cols = 28, 28
    num_classes = 10

    def data_prep(raw):
        out_y = keras.utils.to_categorical(raw.label, num_classes)

        num_images = raw.shape[0]
        x_as_array = raw.values[:, 1:]
        x_shaped_array = x_as_array.reshape(num_images, img_rows, img_cols, 1)
        out_x = x_shaped_array / 255
        return out_x, out_y

    train_file = DIR_TRAIN + "train.csv"
    raw_data = pd.read_csv(train_file)

    x, y = data_prep(raw_data)

    # Creating a new sequential neural model
    model = Sequential()
    model.add(Conv2D(20, kernel_size=(3, 3),
                     activation='relu',
                     input_shape=(img_rows, img_cols, 1)))
    model.add(Conv2D(20, kernel_size=(3, 3), activation='relu'))
    model.add(Flatten())
    # Helper layer than improve the predictions
    model.add(Dense(128, activation='relu'))
    # Output layer, with num_classes predictions
    model.add(Dense(num_classes, activation='softmax'))

    model.compile(loss=keras.losses.categorical_crossentropy,
                  optimizer='adam',
                  metrics=['accuracy'])
    model.summary()
    model.to_json()
    # x training data, y predictions
    model.fit(x, y,
              batch_size=128,
              epochs=2,
              validation_split=0.2)


def kaggle_sample_dl():
    # For deep learning we must to cover
    # Howto to use pre created models
    # Howto use transfer learning to reuse models in new similar topics
    # Howto create new models
    from os.path import join

    img_paths = [join(IMAGE_DIR_TRAIN, filename) for filename in
                 ['0246f44bb123ce3f91c939861eb97fb7.jpg',
                  '84728e78632c0910a69d33f82e62638c.jpg',
                  '8825e914555803f4c67b26593c9d5aff.jpg',
                  '91a5e8db15bccfb6cfa2df5e8b95ec03.jpg']]

    img_paths_mina = [IMAGES_DIR + "/mina/mina1.jpg"]

    from tensorflow.python.keras.applications.resnet50 import preprocess_input
    from tensorflow.python.keras.preprocessing.image import load_img, img_to_array

    image_size = 224

    def read_and_prep_images(img_paths, img_height=image_size, img_width=image_size):
        imgs = [load_img(img_path, target_size=(img_height, img_width)) for img_path in img_paths]
        img_array = np.array([img_to_array(img) for img in imgs])
        output = preprocess_input(img_array)
        return output

    from tensorflow.python.keras.applications import ResNet50

    my_model = ResNet50(weights=RESNET_H5)
    test_data = read_and_prep_images(img_paths)
    preds = my_model.predict(test_data)

    from learntools.deep_learning.decode_predictions import decode_predictions
    from PIL import Image

    most_likely_labels = decode_predictions(preds, top=3, class_list_path=RESNET_JSON)

    for i, img_path in enumerate(img_paths):
        Image.open(img_path).show()
        print(most_likely_labels[i])


def handle_categorical():
    # Different approaches for managing categories in the data and their impact in the MAE
    # Read the data
    x = pd.read_csv(DATA_DIR + '/input/home-data-for-ml-course/train.csv', index_col='Id')
    x_test = pd.read_csv(DATA_DIR + '/input/home-data-for-ml-course/test.csv', index_col='Id')

    # Remove rows with missing target, separate target from predictors
    x.dropna(axis=0, subset=['SalePrice'], inplace=True)
    y = x.SalePrice
    x.drop(['SalePrice'], axis=1, inplace=True)

    # To keep things simple, we'll drop columns with missing values
    cols_with_missing = [col for col in x.columns if x[col].isnull().any()]
    x.drop(cols_with_missing, axis=1, inplace=True)
    x_test.drop(cols_with_missing, axis=1, inplace=True)

    # Break off validation set from training data
    x_train, x_valid, y_train, y_valid = train_test_split(x, y, train_size=0.8, test_size=0.2,
                                                          random_state=0)
    # Get list of categorical variables
    object_cols = [col for col in x_train.columns if x_train[col].dtype == "object"]
    print("Categorical variables:")
    print(object_cols)

    # Score from Approach 1 (Drop Categorical Variables)
    drop_x_train = x_train.drop(object_cols, axis=1)
    drop_x_valid = x_valid.drop(object_cols, axis=1)

    print("MAE from Approach 1 (Drop categorical variables):")
    print(score_dataset(drop_x_train, drop_x_valid, y_train, y_valid))

    # Score from Approach 2 (Label Encoding)
    from sklearn.preprocessing import LabelEncoder

    # Make copy to avoid changing original data
    label_x_train = x_train.copy()
    label_x_valid = x_valid.copy()

    # Apply label encoder to each column with categorical data
    label_encoder = LabelEncoder()

    # Explore category columns to check all the categories are shared between train and valid data
    # Columns that can be safely label encoded
    good_label_cols = [col for col in object_cols if
                       set(x_train[col]) == set(x_valid[col])]

    # Problematic columns that will be dropped from the dataset
    bad_label_cols = list(set(object_cols) - set(good_label_cols))

    label_x_train = label_x_train.drop(bad_label_cols, axis=1)
    label_x_valid = label_x_valid.drop(bad_label_cols, axis=1)

    for col in good_label_cols:
        label_x_train[col] = label_encoder.fit_transform(x_train[col])
        label_x_valid[col] = label_encoder.transform(x_valid[col])

    print("MAE from Approach 2 (Label Encoding):")
    print(score_dataset(label_x_train, label_x_valid, y_train, y_valid))

    # Categorical metrics
    # Get number of unique entries in each column with categorical data
    object_nunique = list(map(lambda col: x_train[col].nunique(), object_cols))
    d = dict(zip(object_cols, object_nunique))

    # Print number of unique entries by column, in ascending order
    print(sorted(d.items(), key=lambda x: x[1]))

    # Apply one-hot encoder to each column with categorical data
    # but only for columns with cardinality < 10

    oh_encoder = OneHotEncoder(handle_unknown='ignore', sparse=False)

    # Columns that will be one-hot encoded
    low_cardinality_cols = [col for col in object_cols if x_train[col].nunique() < 10]
    # Columns that will be dropped from the dataset
    high_cardinality_cols = list(set(object_cols) - set(low_cardinality_cols))

    low_x_train = x_train.drop(high_cardinality_cols, axis=1)
    low_x_valid = x_valid.drop(high_cardinality_cols, axis=1)

    oh_cols_train = pd.DataFrame(oh_encoder.fit_transform(low_x_train[low_cardinality_cols]))
    oh_cols_valid = pd.DataFrame(oh_encoder.transform(low_x_valid[low_cardinality_cols]))

    # One-hot encoding removed index; put it back
    oh_cols_train.index = x_train.index
    oh_cols_valid.index = x_valid.index

    # Remove categorical columns (will replace with one-hot encoding)
    num_x_train = x_train.drop(object_cols, axis=1)
    num_x_valid = x_valid.drop(object_cols, axis=1)

    # Add one-hot encoded columns to numerical features
    oh_x_train = pd.concat([num_x_train, oh_cols_train], axis=1)
    oh_x_valid = pd.concat([num_x_valid, oh_cols_valid], axis=1)

    print("MAE from Approach 3 (One-Hot Encoding):")
    print(score_dataset(oh_x_train, oh_x_valid, y_train, y_valid))


def use_pipelines():

    # Read the data
    x_full = pd.read_csv(DATA_DIR + '/input/home-data-for-ml-course/train.csv', index_col='Id')
    x_test_full = pd.read_csv(DATA_DIR + '/input/home-data-for-ml-course/test.csv', index_col='Id')


    # Remove rows with missing target, separate target from predictors
    x_full.dropna(axis=0, subset=['SalePrice'], inplace=True)
    y = x_full.SalePrice
    x_full.drop(['SalePrice'], axis=1, inplace=True)

    # Break off validation set from training data
    x_train_full, x_valid_full, y_train, y_valid = train_test_split(x_full, y,
                                                                    train_size=0.8, test_size=0.2,
                                                                    random_state=0)

    # "Cardinality" means the number of unique values in a column
    # Select categorical columns with relatively low cardinality (convenient but arbitrary)
    categorical_cols = [cname for cname in x_train_full.columns if
                        x_train_full[cname].nunique() < 10 and
                        x_train_full[cname].dtype == "object"]

    # Select numerical columns
    numerical_cols = [cname for cname in x_train_full.columns if
                      x_train_full[cname].dtype in ['int64', 'float64']]

    # Keep selected columns only
    my_cols = categorical_cols + numerical_cols
    x_train = x_train_full[my_cols].copy()
    x_valid = x_valid_full[my_cols].copy()
    x_test = x_test_full[my_cols].copy()

    # Preprocessing for numerical data
    numerical_transformer = SimpleImputer(strategy='constant')

    # Preprocessing for categorical data
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    # Bundle preprocessing for numerical and categorical data
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_cols),
            ('cat', categorical_transformer, categorical_cols)
        ])

    # Define model
    model = RandomForestRegressor(n_estimators=100, random_state=0)

    # Bundle preprocessing and modeling code in a pipeline
    clf = Pipeline(steps=[('preprocessor', preprocessor),
                          ('model', model)
                          ])

    # Preprocessing of training data, fit model
    clf.fit(x_train, y_train)

    # Preprocessing of validation data, get predictions
    preds = clf.predict(x_valid)

    print('MAE:', mean_absolute_error(y_valid, preds))


def use_crossvalidation():

    # Read the data
    train_data = pd.read_csv(DATA_DIR + '/input/home-data-for-ml-course/train.csv', index_col='Id')
    test_data = pd.read_csv(DATA_DIR + '/input/home-data-for-ml-course/test.csv', index_col='Id')

    # Remove rows with missing target, separate target from predictors
    train_data.dropna(axis=0, subset=['SalePrice'], inplace=True)
    y = train_data.SalePrice
    train_data.drop(['SalePrice'], axis=1, inplace=True)

    # Select numerical columns
    numeric_cols = [cname for cname in train_data.columns if
                      train_data[cname].dtype in ['int64', 'float64']]
    X = train_data[numeric_cols].copy()
    X_test = test_data[numeric_cols].copy()

    my_pipeline = Pipeline(steps=[
        ('preprocessor', SimpleImputer()),
        ('model', RandomForestRegressor(n_estimators=50, random_state=0))
    ])

    from sklearn.model_selection import cross_val_score

    # Multiply by -1 since sklearn calculates *negative* MAE
    scores = -1 * cross_val_score(my_pipeline, X, y,
                                  cv=50,
                                  scoring='neg_mean_absolute_error')

    print("Average MAE score:", scores.mean())


def main():
    args = parse_args()

    configure_logging()

    logging.info("Starting machine_learning.py samples.")

    # TODO: add params to execute a specific sample
    # kaggle_sample_dl()
    # kaggle_digit_dl()
    # kaggle_sample_ml()
    # kaggle_sample2_ml()
    # handle_missing_values()
    # handle_categorical()
    # use_pipelines()
    use_crossvalidation()

    logging.info("Samples execution finished..")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        s = "\n\nReceived Ctrl-C or other break signal. Exiting.\n"
        sys.stderr.write(s)
        sys.exit(0)
import tensorflow as tf
import matplotlib.pyplot as plt
import os
import IPython.display as display
import pandas as pd
from math import log
import csv
import numpy as np
import pathlib

# https://analyticsindiamag.com/multi-label-image-classification-with-tensorflow-keras/
# https://www.tensorflow.org/tutorials/images/cnn


AUTOTUNE = tf.data.experimental.AUTOTUNE

'''
PREPROCESSING DATA
'''
train_data_dir = "./ISIC2018_Task3_Training_GroundTruth.csv"
train_data_path = pathlib.Path(train_data_dir)  # turning all / into \ in the path
image_count = len(list(train_data_path.glob('*.jpg')))

# our predictions will be 0 or 1 from 7 types of skin cancers.
LABEL_COLUMNS = ['MEL', 'NV', 'BCC', 'AKIEC', 'BKL', 'DF', 'VASC']
LABELS = [0, 1]

# modifying our csv file.
training_set = pd.read_csv("D:/Users/arad/ISIC2018T3/data/ISIC2018_Task3_Training_GroundTruth/"
                           "ISIC2018_Task3_Training_GroundTruth.csv")
training_imgs = ["{}.jpg".format(x) for x in list(training_set.image)]  # adding .jpg to image column
# setting up labels to predict.
training_labels_MEL = list(training_set['MEL'].astype(int))
training_labels_NV = list(training_set['NV'].astype(int))
training_labels_BCC = list(training_set['BCC'].astype(int))
training_labels_AKIEC = list(training_set['AKIEC'].astype(int))
training_labels_BKL = list(training_set['BKL'].astype(int))
training_labels_DF = list(training_set['DF'].astype(int))
training_labels_VASC = list(training_set['VASC'].astype(int))

training_set = pd.DataFrame({'Images': training_imgs,
                             'MEL': training_labels_MEL,
                             'NV': training_labels_NV,
                             'BCC': training_labels_BCC,
                             'AKIEC': training_labels_AKIEC,
                             'BKL': training_labels_BKL,
                             'DF': training_labels_DF,
                             'VASC': training_labels_VASC})

# converting to string values in order to concat and create 'class' for cancer type, ie '0100000'
MEL_str = training_set.MEL.astype(str)
NV_str = training_set.NV.astype(str)
BCC_str = training_set.BCC.astype(str)
AKIEC_str = training_set.AKIEC.astype(str)
BKL_str = training_set.BKL.astype(str)
DF_str = training_set.DF.astype(str)
VASC_str = training_set.VASC.astype(str)

training_set['prediction'] = MEL_str + NV_str + BCC_str + AKIEC_str + BKL_str + DF_str + VASC_str

# creating a test csv with test filenames
with open('D:/Users/arad/ISIC2018T3/data/ISIC2018_Task3_Test_Input/test_set.csv', 'w', newline='') as writeFile:
    data = []
    writer = csv.writer(writeFile)
    data.append('Images')
    writer.writerow(data)
    data = []
    for filename in os.listdir('D:/Users/arad/ISIC2018T3/data/ISIC2018_Task3_Test_Input/images'):
        data.append(filename)
        writer.writerow(data)
        data = []
writeFile.close()

test_set = pd.read_csv("D:/Users/arad/ISIC2018T3/data/ISIC2018_Task3_Test_Input/test_set.csv")
test_imgs = ["D:/Users/arad/ISIC2018T3/data/ISIC2018_Task3_Test_Input/images/{}.jpg".format(x) for x in
             list(test_set.id)]
test_set = pd.DataFrame({'Images': test_imgs})

BATCH_SIZE = 32
IMG_HEIGHT = 600
IMG_WIDTH = 450
STEPS_PER_EPOCH = np.ceil(image_count / BATCH_SIZE)

# The 1./255 is to convert from uint8 to float32 in range [0,1].
image_generator = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1. / 255)
train_data_gen = image_generator.flow_from_dataframe(
    dataframe=training_set,
    directory='data/ISIC2018_Task3_Training_Input/images',
    x_col="Images",
    y_col="prediction",
    class_mode="categorical",  # 2D numpy array of one-hot encoded labels. supports multi-label output.
    shuffle=False,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    validate_filenames=True)

'''
BASIC CNN MODEL
'''
model = tf.keras.models.Sequential()  # creating a sequential model for our CNN
model.add(tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)))
model.add(tf.keras.layers.MaxPooling2D((2, 2)))
model.add(tf.keras.layers.Conv2D(64, (3, 3), activation='relu'))
model.add(tf.keras.layers.MaxPooling2D((2, 2)))
model.add(tf.keras.layers.Conv2D(64, (3, 3), activation='relu'))

model.add(tf.keras.layers.Flatten())  # flatten the output into vector
model.add(tf.keras.layers.Dense(64, activation='relu'))
model.add(tf.keras.layers.Dense(7, activation='softmax'))  # 7 output layers for the features

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

model.summary()
model.fit_generator(train_data_gen, epochs=50, steps_per_epoch=60)  # train the model

'''
Our model will be predicting the labels in the range 0 to 6 based on the above dictionary for each category. 
We will need to reverse these to the original classes to later convert the predictions to actual classes.

'''
classes = train_data_gen.class_indices
inverted_classes = dict({v: k for k, v in classes.items()})
print(classes)

Y_pred = []
for i in range(len(test_set)):
    img = tf.keras.preprocessing.image.load_img(path=test_set.Images[i], target_size=(IMG_HEIGHT, IMG_WIDTH, 3))
    img = tf.keras.preprocessing.image.img_to_array(img)
    test_img = img.reshape((1, IMG_HEIGHT, IMG_WIDTH, 3))
    img_class = model.predict_classes(test_img)
    prediction = img_class[0]
    Y_pred.append(prediction)

print(Y_pred)

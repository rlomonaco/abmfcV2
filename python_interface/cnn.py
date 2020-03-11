import keras
from keras.preprocessing import image as im
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout, Activation
from keras.optimizers import Adam
from keras import optimizers
import tensorflow as tf
import keras.backend as K
from keras.utils.generic_utils import get_custom_objects



import numpy as np
import matplotlib.pyplot as plt
import os
import cv2

os.chdir('/home/godfrey/abm-fc/python_interface/')

def view(region, player_pos):
    plt.figure()
    plt.imshow(region)
    plt.scatter(player_pos[:11,2]+50, player_pos[:11,3]+35, c='r')
    plt.scatter(player_pos[11:, 2] + 50, player_pos[11:, 3] + 35, c='b')

def gen_input(opp_regions, player_poss):
    input_data = []
    for num in range(opp_regions.shape[2]):
        opp_region = opp_regions[:,:,num]
        player_pos = player_poss[:,:,num]

        # view(opp_region, player_pos)

        a = cv2.resize(opp_region, dsize=(10, 7), interpolation=cv2.INTER_CUBIC)
        a = -a.astype(int)
        a[a>=0] = -1
        a[2:5, -1] = 10
        a[3, -1] = 50
        a[3, -2] = 10
        x = (player_pos[:11,2]+50)/10
        x = x.astype(int)
        y = (player_pos[:11,3]+35)/10
        y = y.astype(int)

        for i in range(len(x)):
            # plt.figure()
            b = a.copy()
            b[y[i], x[i]] = 0
            input_data.append(b)

    return input_data

file_dir = os.getcwd()+'/saved_heatmaps/'
file_num = 0

regions = np.load(file_dir + f'regions_{file_num}.npy')
team_regions = np.load(file_dir + f'team_regions_{file_num}.npy')
opp_regions = np.load(file_dir + f'opp_regions_{file_num}.npy')
player_poss = np.load(file_dir + f'player_pos_{file_num}.npy')

input_data = gen_input(opp_regions, player_poss)

import keras
from keras.preprocessing import image as im
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout, Activation
from keras.optimizers import Adam
from keras import optimizers
import tensorflow as tf
import keras.backend as K
from keras.utils.generic_utils import get_custom_objects

X = np.array(input_data)/50
X = X.reshape(X.shape[0],7,10,1)
Y = np.load(os.getcwd()+f'/moves{file_num}.npy')
Y = np.dstack(list(Y))

output_size = X.shape[1] * X.shape[2]
y = Y.reshape(70, Y.shape[2]).T

from sklearn.model_selection import train_test_split

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)
# X_train = X_train.reshape(7,10,X_train.shape[0])
# X_test = X_train.reshape(7,10,X_test.shape[0])
# y_train = X_train.reshape(70,y_train.shape[0])
# y_test = X_train.reshape(70,y_test.shape[0])

# def custom_activation(x):
#     if K.sigmoid(x) >= 0.5:
#         return 1
#     return 0

# get_custom_objects().update({'custom_activation': Activation(custom_activation)})

batch_size = 200
epochs = 20

model = Sequential()

model.add(Conv2D(64, kernel_size=(3, 3),padding='valid',strides=1,
                 activation='relu',
                 input_shape=(7,10,1)))
model.add(Conv2D(128, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(1, 2)))
model.add(Dropout(0.25))
model.add(Conv2D(32, (3, 3), activation='relu'))
# model.summary()
model.add(Flatten())
model.add(Dense(280, activation='relu'))
model.add(Dense(140, activation='relu'))
model.add(Dense(70, activation='sigmoid'))
# model.add(Activation(custom_activation, name='SpecialActivation'))

model.summary()

model.compile(loss=keras.losses.categorical_crossentropy,
              optimizer=keras.optimizers.Adam(),
              metrics=['accuracy'])

model.fit(X, y,
          batch_size=batch_size,
          epochs=epochs,
          verbose=1,
          validation_split=0.2)

score = model.evaluate(X, y, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])
model.save_weights('model.h5')

file_num = 1

regions = np.load(file_dir + f'regions_{file_num}.npy')
team_regions = np.load(file_dir + f'team_regions_{file_num}.npy')
opp_regions = np.load(file_dir + f'opp_regions_{file_num}.npy')
player_poss = np.load(file_dir + f'player_pos_{file_num}.npy')

input_data = gen_input(opp_regions, player_poss)
X = np.array(input_data)/50
X = X.reshape(X.shape[0],7,10,1)

Y = np.load(os.getcwd()+f'/moves{file_num}.npy')
Y = np.dstack(list(Y))
y = Y.reshape(70, Y.shape[2]).T
answers = model.predict(X, batch_size=None, verbose=0, steps=None, callbacks=None, max_queue_size=10, workers=1, use_multiprocessing=False)

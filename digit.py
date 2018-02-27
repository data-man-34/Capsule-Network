
"""
    The digit caps model in the paper.
"""

import numpy as np
from keras.models import Sequential, Model
from keras.datasets import mnist
from keras.utils import to_categorical
from keras.layers import Input, Conv2D, Dense, Reshape
from keras_capsnet import margin_loss, conv2d_caps, DenseCapsule, Mask

img_dim = (28, 28, 1)
output_shape = 10

def load_mnist_data():

    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x_train = x_train.reshape(-1, 28, 28, 1).astype('float32')/255.0
    x_test = x_test.reshape(-1, 28, 28, 1).astype('float32')/255.0
    y_train = to_categorical(y_train.astype('float32'))
    y_test = to_categorical(y_test.astype('float32'))

    return (x_train, y_train), (x_test, y_test)


def build_models():
    global img_dim, output_shape

    input_layer = Input(shape=(img_dim[0], img_dim[1], img_dim[2]))
    conv1 = Conv2D(filters=256, kernel_size=9, strides=1, padding='valid', activation='relu')(input_layer)
    primarycaps = conv2d_caps(
        input_layer=conv1,
        nb_filters=32,
        capsule_size=8,
        kernel_size=9,
        strides=2
    )
    digitcaps = DenseCapsule(capsule_size=16, nb_capsules=output_shape)(primarycaps)

    # Decoder part..
    true_labels_input = Input(shape=(output_shape,))  # use the true label to mask the capsule
    masked_by_true_label = Mask()([digitcaps, true_labels_input])  # for training process
    masked_by_max = Mask(digitcaps)  # for prediction process

    decoder = Sequential()
    decoder.add(Dense(512, activation='relu', input_dim=16*output_shape))
    decoder.add(Dense(1024, activation='relu'))
    decoder.add(Dense(np.prod(img_dim), activation='sigmoid'))
    decoder.add(Reshape(target_shape=img_dim))

    train_model = Model(
        inputs=[input_layer, true_labels_input],
        outputs=[decoder(masked_by_true_label), digitcaps]
    )

    eval_model = Model(
        inputs=input_layer,
        outputs=[decoder(masked_by_max), digitcaps]
    )

    return train_model, eval_model


def main():

    train_data, test_data = load_mnist_data()
    train_model, eval_model = build_models()


if __name__ == '__main__':
    main()
from keras.initializers import Initializer
from keras.layers import Dense, Input
from keras.models import Model
from typing import List, Tuple, Union, TypeVar

KernelInitializer = TypeVar('KernelInitializer', bound=Union[str, Initializer])


def autoencoder(dims: List[int],
                activation: str = 'relu',
                kernel_initializer: KernelInitializer = 'glorot_uniform') -> Tuple[Model, Model]:
    """
    Fully connected symmetric autoencoder model.

    Args:
        dims (List[int]): List of the sizes of layers of encoder.
                          dims[0] is input dim, dims[-1] is size of the latent hidden layer.
        activation (str, optional): Activation function. Defaults to 'relu'.
        kernel_initializer (KernelInitializer, optional): Kernel initializer. Defaults to 'glorot_uniform'.

    Returns:
        Tuple[Model, Model]: Autoencoder and encoder models
    """
    n_stacks = len(dims) - 1

    input_layer = Input(shape=(dims[0], ), name='input')
    layer = input_layer

    # Encoder internal layers
    for i_layer in range(n_stacks - 1):
        layer = Dense(dims[i_layer + 1],
                      activation=activation,
                      kernel_initializer=kernel_initializer,
                      name=f"encoder_{i_layer}")(layer)

    # Latent hidden layer
    encoded_layer = Dense(dims[-1], kernel_initializer=kernel_initializer, name=f"encoder_{n_stacks - 1}")(layer)

    # Decoder internal layers
    layer = encoded_layer
    for i_layer in range(n_stacks - 1, 0, -1):
        layer = Dense(dims[i_layer],
                      activation=activation,
                      kernel_initializer=kernel_initializer,
                      name=f"decoder_{i_layer}")(layer)

    # Decoder output
    layer = Dense(dims[0], kernel_initializer=kernel_initializer, name='decoder_0')(layer)
    decoded_layer = layer

    _autoencoder = Model(inputs=input_layer, outputs=decoded_layer, name='autoencoder')
    _encoder = Model(inputs=input_layer, outputs=encoded_layer, name='encoder')

    return _autoencoder, _encoder

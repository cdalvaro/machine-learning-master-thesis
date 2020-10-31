from keras.initializers import Initializer
from keras.layers import Dense, Input
from keras.models import Model
from typing import List, Tuple, Union, TypeVar

KernelInitializer = TypeVar('KernelInitializer', bound=Union[str, Initializer])


def autoencoder(dims: List[int],
                activation: str = 'relu',
                kernel_initializer: KernelInitializer = 'glorot_uniform') -> Tuple[Model, Model]:
    """
    Fully connected symmetric auto-encoder model.

    Args:
        dims (List[int]): List of the sizes of layers of encoder like [500, 500, 2000, 10].
                          dims[0] is input dim, dims[-1] is size of the latent hidden layer.
        activation (str, optional): Activation function. Defaults to 'relu'.
        kernel_initializer (KernelInitializer, optional): Kernel initializer. Defaults to 'glorot_uniform'.

    Returns:
        Tuple[Model, Model]: Autoencoder and encoder models
    """
    n_stacks = len(dims) - 1

    input_data = Input(shape=(dims[0], ), name='input')
    x = input_data

    # Internal layers of encoder
    for i in range(n_stacks - 1):
        x = Dense(dims[i + 1], activation=activation, kernel_initializer=kernel_initializer, name=f"encoder_{i}")(x)

    # Latent hidden layer
    encoded = Dense(dims[-1], kernel_initializer=kernel_initializer, name=f"encoder_{n_stacks - 1}")(x)

    # Internal layers of decoder
    x = encoded
    for i in range(n_stacks - 1, 0, -1):
        x = Dense(dims[i], activation=activation, kernel_initializer=kernel_initializer, name=f"decoder_{i}")(x)

    # Decoder output
    x = Dense(dims[0], kernel_initializer=kernel_initializer, name='decoder_0')(x)
    decoded = x

    autoencoder_model = Model(inputs=input_data, outputs=decoded, name='autoencoder')
    encoder_model = Model(inputs=input_data, outputs=encoded, name='encoder')

    return autoencoder_model, encoder_model

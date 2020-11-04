from keras.models import Model
from keras.optimizers import Adam, Optimizer, SGD
import numpy as np
import os
from sklearn.cluster import KMeans
from typing import List, Union

from .autoencoder import autoencoder, KernelInitializer
from .clustering_layer import ClusteringLayer
from ..utils import estimate_n_clusters


class DEC(object):
    def __init__(self,
                 dims: List[int],
                 n_clusters: int,
                 activation: str = 'relu',
                 alpha: float = 1.0,
                 initializer: KernelInitializer = 'glorot_uniform'):
        """
        Unsupervised Deep Embedding for Clustering Analysis (DEC)
        Link: http://proceedings.mlr.press/v48/xieb16.pdf

        DEC learns a mapping from the data space to a lower-dimensional feature space
        in which it iteratively optimizes a clustering objective.

        Args:
            dims (List[int]): DEC layers configuration. First element must be the number of features.
            n_clusters (int): The number of clusters to be found.
            activation (str, optional): Activation function used in encoder models. Defaults to relu.
            alpha (float, optional): Degrees of freedom of the Student's t-distribution. Defaults to 1.0.
            initializer (KernelInitializer, optional): Kernel initializer used in encoder models. Defaults to glorot_uniform.
            optimizer (Optimizer, optional): Optimizer used in encoder models. Defaults to SGD.
        """
        super(DEC, self).__init__()

        self._dims = dims
        self._n_clusters = n_clusters
        self._pretrained = False

        # Autoencoder and encoder models
        self._autoencoder, self._encoder = autoencoder(dims=dims, activation=activation, initializer=initializer)

        # DEC model
        clustering_layer = ClusteringLayer(n_clusters, alpha=alpha, name='clustering')(self._encoder.output)
        self._model = Model(inputs=self._encoder.input, outputs=[clustering_layer, self._autoencoder.output])

    @property
    def dims(self):
        return self._dims

    @property
    def n_clusters(self):
        return self._n_clusters

    @property
    def model(self):
        return self._model

    @property
    def autoencoder(self):
        return self._autoencoder

    @property
    def encoder(self):
        return self._encoder

    def load_weights(self, weights: str):
        """
        Load weights for DEC model from file

        Args:
            weights (str): The file path with saved weights
        """
        self._model.load_weights(weights)

    def extract_features(self, x):
        return self._encoder.predict(x)

    def pretrain(self,
                 x,
                 optimizer: Optimizer = Adam(),
                 loss: Union[str, List[str]] = 'mse',
                 epochs: int = 200,
                 batch_size: int = 256,
                 save_dir: str = None,
                 verbose: int = 1):
        """
        Pretrain autoencoder model.

        Args:
            x: The data used for pretraining.
            optimizer (Optimizer, optional): [description]. Defaults to Adam.
            loss (Union[str, List[str]], optional): [description]. Defaults to 'mse'.
            epochs (int, optional): The number of epochs for pretraining. Defaults to 200.
            batch_size (int, optional): The batch size for pretraining. Defaults to 256.
            save_dir (str, optional): The directory for saving autoencoder model weights. Defaults to None.
            verbose (int, optional): The verbosity level. Defaults to 0.
        """
        if verbose > 0:
            print("Pretraining autoencoder model...")
        self._autoencoder.compile(optimizer=optimizer, loss=loss)
        self._autoencoder.fit(x, x, batch_size=batch_size, epochs=epochs, verbose=verbose)
        self._pretrained = True

        if save_dir is not None:
            if not os.path.isdir(save_dir):
                os.makedirs(save_dir)
            file_path = f"{save_dir}/dec_ae_weights.h5"
            self._autoencoder.save_weights(file_path)
            print(f"Pretrained weights have been saved to: {file_path}")

    def compile(self,
                optimizer: Optimizer = SGD(1, 0.9),
                loss: Union[str, List[str]] = 'kld',
                loss_weights: List[float] = None):
        """
        Compile the DEC model.

        Args:
            optimizer (Optimizer, optional): Optimizer instance. Defaults to SGD(1, 0.9).
            loss (Union[str, List[str]], optional): The loss metric to be minimized. Defaults to 'kld'.
            loss_weights (List[int], optional): Scalar coefficients to weight the loss contributions of different model outputs. Defaults to None.
        """
        self._model.compile(optimizer=optimizer, loss=loss, loss_weights=loss_weights)

    def fit(self,
            x,
            batch_size: int = 256,
            maxiter: int = 2000,
            tol: float = 1e-3,
            update_interval: int = 140,
            save_dir: str = None,
            verbose: int = 1):
        """
        Fit DEC model and give predictions for dataset `x`.

        Args:
            x: The dataset used for training and predicting.
            batch_size (int, optional): The batch size. Defaults to 256.
            maxiter (int, optional): Maximum iterations for training. Defaults to 1000.
            tol (float, optional): Tolerance threshold to stop training. Defaults to 1e-3.
            update_interval (int, optional): Number of iterations before updating internal predictions. Defaults to 140.
            save_dir (str, optional): The directory for saving dec model weights. Defaults to None.
            verbose (int, optional): The verbosity level. Defaults to 1.

        Returns:
            Array with the predicted group for each `x` sample.
        """
        if verbose > 0:
            print("Training DEC model...")

        # DEC - Phase 1: parameter initialization with a deep autoencoder
        # Reference:
        #     Unsupervised Deep Embedding for Clustering Analysis - 3.2 Parameter initialization
        kmeans = KMeans(self._n_clusters, n_init=20)
        y_pred = kmeans.fit_predict(self._encoder.predict(x))
        y_pred_last = np.copy(y_pred)
        self._model.get_layer(name='clustering').set_weights([kmeans.cluster_centers_])

        # DEC - Phase 2: Optimization
        # Reference:
        #     Unsupervised Deep Embedding for Clustering Analysis - 3.1 Clustering with KL divergence
        loss, index = 0, 0
        index_array = np.arange(x.shape[0])
        for it in range(maxiter):
            if it % update_interval == 0:
                q, _ = self._model.predict(x, verbose=0)
                p = self._target_distribution(q)
                y_pred = q.argmax(1)

                # Stop criteria
                delta_label = np.sum(y_pred != y_pred_last).astype(np.float32) / y_pred.shape[0]
                y_pred_last = np.copy(y_pred)
                if it > 0 and delta_label < tol:
                    if verbose > 0:
                        print(f"Delta label: {delta_label:.4e} < tolerance: {tol}")
                        print("Reached tolerance threshold. Stopping training.")
                    break

            # Train on batch
            idx = index_array[index * batch_size:min((index + 1) * batch_size, x.shape[0])]
            loss = self._model.train_on_batch(x=x[idx], y=[p[idx], x[idx]])
            index = index + 1 if (index + 1) * batch_size <= x.shape[0] else 0
            if verbose > 0:
                print(f"Iteration {it + 1}/{maxiter} - loss: {np.max(loss):.4e}")

        self._trained = True
        if save_dir is not None:
            if not os.path.isdir(save_dir):
                os.makedirs(save_dir)
            file_path = f"{save_dir}/dec_model_weights.h5"
            self._autoencoder.save_weights(file_path)
            print(f"DEC model weights have been saved to: {file_path}")

    def predict(self, x, verbose: int = 0) -> np.ndarray:
        """
        Generate predictions for the given dataset

        Args:
            x: The input data

        Returns:
            np.ndarray: Numpy array of predictions
        """
        if not self._trained:
            raise Exception("This model has not been trained yet")
        q, _ = self._model.predict(x, verbose=verbose)
        return q.argmax(1)

    @staticmethod
    def _target_distribution(q: np.ndarray) -> np.ndarray:
        """
        Kullback-Leibler (KL) divergence

        Args:
            q (np.ndarray): Model predictions

        Returns:
            np.ndarray: The computed distribution
        """
        weight = q**2 / q.sum(0)
        return (weight.T / weight.sum(1)).T

from enum import auto
from keras.backend.cntk_backend import update
from keras.models import Model
from keras.optimizers import Optimizer, SGD
import numpy as np
from scipy.cluster.hierarchy import weighted
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from typing import List, Union

from .autoencoder import autoencoder, KernelInitializer
from .clustering_layer import ClusteringLayer


class DEC:
    def __init__(self, data, dims: List[int] = None, n_clusters: int = None, n_jobs: int = None, save_dir: str = None):
        # TODO: Add documentation
        if dims is None:
            self._dims = [data.shape[-1], 500, 500, 2000, 10]
        elif dims[0] != data.shape[-1]:
            ValueError(f"First dims value must be equal to data.shape[-1] -> {dims[0]} != {data.shape[-1]}")
        else:
            self._dims = dims

        self._data = data
        self._n_clusters = n_clusters
        self._n_jobs = n_jobs
        self.save_dir = save_dir
        self._kmeans = None
        self._model = None
        self._pretrain_autoencoder = None
        self._encoder = None
        self._autoencoder = None
        self._built = False

    @property
    def dims(self):
        return self._dims

    @property
    def n_clusters(self):
        return self._n_clusters

    @property
    def model(self):
        return self._model

    def fit_predict(self, n_epochs):
        # TODO: Add documentation
        pass

    def build(self,
              activation: str = 'relu',
              kernel_initializer: KernelInitializer = 'glorot_uniform',
              optimizer: Optimizer = None,
              loss: Union[str, List[str]] = 'mse'):
        # TODO: Add documentation
        if optimizer is None:
            optimizer = SGD(lr=1, momentum=0.9)

        if self._n_clusters is None:
            self._n_clusters = self._estimate_n_clusters()

        # K-Means
        self._kmeans = KMeans(self._n_clusters, n_jobs=self._n_jobs)

        # Pretrain autoencoder
        self._pretrain_autoencoder, _ = autoencoder(dims=self._dims,
                                                    activation=activation,
                                                    kernel_initializer=kernel_initializer)

        self._pretrain_autoencoder.compile(optimizer=optimizer, loss=loss)

        # TODO: Check if we need here a previous model

        # Jointly refining DEC model
        self._autoencoder, self._encoder = autoencoder(dims=self._dims,
                                                       activation=activation,
                                                       kernel_initializer=kernel_initializer)

        ## Soft labeling layer
        clustering_layer = ClusteringLayer(n_clusters=self._n_clusters, name='clustering')(self._encoder.output)

        self._model = Model(inputs=self._encoder.input, outputs=[clustering_layer, self._autoencoder.output])
        self._model.compile(optimizer=optimizer, loss=['kld', 'mse'], loss_weights=[0.1, 1])

        self._built = True

    def fit(self,
            epochs: int = 100,
            batch_size: int = 128,
            maxiter: int = 1000,
            tolerance: float = 0.001,
            update_interval: int = 100):
        # TODO: Add documentation
        if not self._built:
            raise Exception("You must build your model before fitting it")

        # K-Means
        y_pred_last = self._kmeans.fit_predict(self._encoder.predict(self._data))

        # Autoencoder
        self._pretrain_autoencoder.fit(self._data, self._data, batch_size=batch_size, epochs=epochs)

        # Jointly refining DEC model
        self._autoencoder.set_weights(self._pretrain_autoencoder.weights)
        self._model.get_layer(name='clustering').set_weights([self._kmeans.cluster_centers_])

        index = 0
        index_array = np.arange(self._data.shape[0])
        for it in range(maxiter):
            if it % update_interval == 0:
                q, _ = self._model.predict(self._data, verbose=0)
                p = self._target_distribution(q)
                y_pred = q.argmax(1)

                # Stop criteria
                delta_label = np.sum(y_pred != y_pred_last).astype(np.float32) / y_pred.shape[0]
                y_pred_last = np.copy(y_pred)
                if it > 0 and delta_label < tolerance:
                    # TODO: Change print for logger
                    print("Delta label", delta_label, "< tolerance", tolerance)
                    print("Reached tolerance threshold. Stopping training.")
                    break

            idx = index_array[index * batch_size:min((index + 1) * batch_size, self._data.shape[0])]
            loss = self._model.train_on_batch(x=self._data[idx], y=[p[idx], self._data[idx]])
            index = index + 1 if (index + 1) * batch_size <= self._data.shape[0] else 0

    def predict(self, data) -> np.ndarray:
        # TODO: Add documentation
        q, _ = self._model.predict(data, verbose=0)
        return q.argmax(1)

    def _target_distribution(self, q: np.ndarray) -> np.ndarray:
        # TODO: Add documentation
        weight = q**2 / q.sum(0)
        return (weight.T / weight.sum(1)).T

    def _estimate_n_clusters(self) -> int:
        """
        Estimate the number of clusters based on silhoutte score.

        Raises:
            ValueError: If the number of clusters cannot be estimated.

        Returns:
            int: The estimated number of clusters
        """
        best_score = -1.0
        best_n_clusters = None
        for n_clusters in range(2, 10):
            kmeans = KMeans(n_clusters=n_clusters, n_jobs=self._n_jobs)
            pred = kmeans.fit_predict(self._data)
            score = silhouette_score(self._data, pred, metric='euclidean')
            if score > best_score:
                best_score = score
                best_n_clusters = n_clusters

        if best_n_clusters is None:
            raise ValueError("Unable to estimate the number of clusters to be used")

        return best_n_clusters

import keras.backend as K
from keras.layers import InputSpec, Layer


class ClusteringLayer(Layer):
    def __init__(self, n_clusters, weights=None, alpha: float = 1.0, **kwargs):
        """
        This layer converts the input sample to soft label, i.e. a vector that represents
        the probability of the sample belonging to each cluster.

        The probability is calculated with student's t-distribution.

        Args:
            n_clusters (int): Number of clusters.
            weights (optional): List of Numpy array with shape `(n_clusters, n_features)` which represents the initial cluster centers.
            alpha (float, optional): Degrees of freedom of the Student's t-distribution. Defaults to 1.0.

        Input shape:
            2D tensor with shape: `(n_samples, n_features)`

        Output shape:
            2D tensor with shape: `(n_samples, n_clusters)`
        """
        if 'input_shape' not in kwargs and 'input_dim' in kwargs:
            kwargs['input_shape'] = (kwargs.pop('input_dim'), )
        super(ClusteringLayer, self).__init__(**kwargs)
        self.n_clusters = n_clusters
        self.alpha = alpha
        self.initial_weights = weights
        self.input_spec = InputSpec(ndim=2)

    def build(self, input_shape):
        assert len(input_shape) == 2
        input_dim = input_shape[1]
        self.input_spec = InputSpec(dtype=K.floatx(), shape=(None, input_dim))
        self.clusters = self.add_weight(name='clusters',
                                        shape=(self.n_clusters, input_dim),
                                        initializer='glorot_uniform')

        if self.initial_weights is not None:
            self.set_weights(self.initial_weights)
            del self.initial_weights
        self.built = True

    def call(self, inputs, **kwargs):
        """
        Student t-distribution, as used in t-SNE algorithm.
        It measures the similarity between embedded point z_i and centroid µ_j.
            q_ij = 1.0 / (1.0 + dist(x_i, µ_j)^2), then normalize it.
            q_ij can be interpreted as the probability of assingning sample i to cluster j.
            (i.e., a soft assignment)

        Reference:
            Unsupervised Deep Embedding for Clustering Analysis - 3.1.1 Soft Assignment

        Args:
            inputs: The variable containing data, shape=(n_samples, n_features)

        Returns:
            Student's t-distribution, or soft labels for each sample. shape=(n_samples, n_clusters)
        """
        q = 1.0 / (1.0 + (K.sum(K.square(K.expand_dims(inputs, axis=1) - self.clusters), axis=2) / self.alpha))
        q = K.pow(q, (self.alpha + 1.0) / 2.0)
        q = K.transpose(K.transpose(q) / K.sum(q, axis=1))

        return q

    def compute_output_shape(self, input_shape):
        assert input_shape and len(input_shape) == 2
        return input_shape[0], self.n_clusters

    def get_config(self):
        config = {'n_clusters': self.n_clusters}
        base_config = super(ClusteringLayer, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))

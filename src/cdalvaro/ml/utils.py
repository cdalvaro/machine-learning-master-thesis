from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def estimate_n_clusters(x, metric: str = 'euclidean', max_clusters: int = 10, verbose: bool = False) -> int:
    """
        Estimate the number of clusters based on silhoutte score.

        Args:
            x (array-like): Data to be fit for best number of clusters estimation.
            metric (str, optional): The metric to use when calculating distance between instances in a feature array. Defaults to euclidean.
            max_clusters (int, optional): The maximum number of clusters to be tested. Defaults to 10.
            verbose (bool, optional): Show algorithm progress. Defaults to False.

        Raises:
            ValueError: If the number of clusters cannot be estimated.

        Returns:
            int: The estimated number of clusters
        """
    best_score = -1.0
    best_n_clusters = None
    for n_clusters in range(2, max_clusters + 1):
        kmeans = KMeans(n_clusters=n_clusters)
        pred = kmeans.fit_predict(x)
        score = silhouette_score(x, pred, metric=metric)
        if verbose:
            print(f"Silhouette score for {n_clusters} clusters: {score:.4f}")
        if score > best_score:
            best_score = score
            best_n_clusters = n_clusters

    if best_n_clusters is None:
        raise ValueError("Unable to estimate the number of clusters to be used")

    if verbose:
        print(f"Best silhouette score is {best_score} for {best_n_clusters} clusters")

    return best_n_clusters

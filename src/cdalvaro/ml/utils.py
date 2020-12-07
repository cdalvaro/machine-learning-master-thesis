import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from typing import List, Tuple


def estimate_n_clusters(x,
                        metric: str = 'euclidean',
                        min_clusters: int = 2,
                        max_clusters: int = 10,
                        verbose: bool = False) -> Tuple[int, KMeans]:
    """
    Estimate the number of clusters based on silhoutte score.

    Args:
        x (array-like): Data to be fit for best number of clusters estimation.
        metric (str, optional): The metric to use when calculating distance between instances in a feature array. Defaults to euclidean.
        min_clusters (int, optional): The minimum number fo clusters to be tested. Defaults to 2.
        max_clusters (int, optional): The maximum number of clusters to be tested. Defaults to 10.
        verbose (bool, optional): Show algorithm progress. Defaults to False.

    Raises:
        ValueError: If the number of clusters cannot be estimated.

    Returns:
        int: The estimated number of clusters
    """
    best_score = -1.0
    best_n_clusters: int = None
    best_kmeans: KMeans = None
    for n_clusters in range(min_clusters, max_clusters + 1):
        kmeans = KMeans(n_clusters=n_clusters)
        pred = kmeans.fit_predict(x)
        score = silhouette_score(x, pred, metric=metric)
        if verbose:
            print(f"Silhouette score for {n_clusters} clusters: {score:.4f}")
        if score > best_score:
            best_score = score
            best_n_clusters = n_clusters
            best_kmeans = kmeans

    if best_n_clusters is None:
        raise ValueError("Unable to estimate the number of clusters to be used")

    if verbose:
        print(f"Best silhouette score is {best_score:.4f} for {best_n_clusters} clusters")

    return best_n_clusters, best_kmeans


def filter_outliers(df: pd.DataFrame, q: float = 0.05) -> pd.Series:
    """
    Return a mask indicating those entries inside the specified quantile `q`.

    Args:
        df (DataFrame): Pandas DataFrame to be filtered.
        q (float): The quantile threshold.

    Returns:
        pd.Series: A series indicating those entries inside the quantiles.
    """
    upper = df.quantile(1.0 - q)
    lower = df.quantile(q)
    mask = (df < upper) & (df > lower)
    return mask


def cluster_centers(df: pd.DataFrame, key: str, columns: List[str] = []) -> pd.DataFrame:
    """
    Return a Pandas DataFrame with centers for each cluster.

    Args:
        df (pd.DataFrame): The DataFrame with data to be analyzed.
        key (str): The key of the cluster reference column.
        columns (List[str], optional): List of columns to take into account. Defaults to [].

    Returns:
        pd.DataFrame: A DataFrame with center for each cluster and column.
    """
    if len(columns) > 0 and key not in columns:
        columns.append(key)
    __df = df[columns] if len(columns) > 0 else df

    return __df.groupby(by=key).mean()


def cluster_stats(df: pd.DataFrame, key: str, columns: List[str] = [], **kwargs) -> pd.DataFrame:
    """
    Return a Pandas DataFrame with statistics for each cluster.

    Args:
        df (pd.DataFrame): The DataFrame with data to be analyzed.
        key (str): The key of the cluster reference column.
        columns (List[str], optional): List of columns to take into account. Defaults to [].
        **kwargs (optional): Extra arguments are passed to Pandas.DataFrame.describe() method.
        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.core.groupby.DataFrameGroupBy.describe.html

    Returns:
        pd.DataFrame: A DataFrame with statistics for each cluster and column.
    """
    if len(columns) > 0 and key not in columns:
        columns.append(key)
    __df = df[columns] if len(columns) > 0 else df

    return __df.groupby(by=key).describe(**kwargs)

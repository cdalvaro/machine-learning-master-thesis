#!/usr/bin/env python3

from cdalvaro.catalogues import OpenClust
from cdalvaro.data_base import DB
from cdalvaro.graphics import plot as cplt
from cdalvaro.logging import Logger
from cdalvaro.ml import DEC
from cdalvaro.ml.utils import estimate_n_clusters, filter_outliers
from IPython.display import Image
import logging
import numpy as np
import os
import pandas as pd
from pathlib import Path
import re
from sklearn.preprocessing import MinMaxScaler
import sys

from keras.initializers import glorot_uniform, VarianceScaling
from keras.optimizers import SGD
from keras.utils import plot_model


logger = Logger.instance()
logger.setLevel(logging.ERROR)

db = DB.instance(host='gaia.cdalvaro.io', port=15432)

clusters = OpenClust.catalogue()
cluster = clusters["Melotte 22"]

# Directories
project_dir = Path(os.path.dirname(sys.argv[0])).parent.parent

cluster_name = cluster.name.replace(' ', '_').lower()
figures_path = project_dir / "figures" / cluster_name
results_path = project_dir / "results" / cluster_name

for dir in [figures_path, results_path]:
    dir.mkdir(exist_ok=True)

variables = [
    "ra", "ra_error", "dec", "dec_error", "pmra", "pmra_error",
    "pmdec", "pmdec_error", "parallax", "parallax_error",
    "phot_g_mean_mag", "bp_rp"
]

non_null_columns = list(filter(lambda x: not re.search(r'_error', x), variables))

# Stars selection
stars_df = db.get_stars(region=cluster, columns=variables, filter_null_columns=non_null_columns)

stars_df = stars_df[(np.abs(stars_df['pmra']) > 0.0)
                    & (np.abs(stars_df['pmdec']) > 0.0)
                    & (np.abs(stars_df['parallax']) > 0.0)]

stars_df['pmra_corr'] = stars_df['pmra'] * 1000.0 / stars_df['parallax']
stars_df['pmdec_corr'] = stars_df['pmdec'] * 1000.0 / stars_df['parallax']

stars_df['pmmod'] = np.sqrt(stars_df['pmra_corr'] ** 2 + stars_df['pmdec_corr'] ** 2)
stars_df['pmang'] = np.arctan2(stars_df['pmdec_corr'], stars_df['pmra_corr'])

stars_df.head()

# Feature selection
features = ['pmra_corr', 'pmdec_corr', 'pmmod', 'parallax']

## Feature rescaling
scaler = MinMaxScaler()
x = scaler.fit_transform(stars_df[features])

# K-Means

## Step 1 - Creating and training K-means model
n_clusters, kmeans = estimate_n_clusters(x, min_clusters=3, max_clusters=10, verbose=True)
stars_df['cluster_g'] = np.array([f"g{g}" for g in kmeans.predict(x)], dtype=str)

fig, ax, g = cplt.plot_cluster_proper_motion(stars_df, xlim=(-30, 50), ylim=(-70, 40))
cplt.save_figure(fig, name=f"kmeans_pm_{cluster.name}", save_dir=figures_path)

fig, ax, g = cplt.plot_cluster_parallax_histogram(stars_df, xlim=(-4, 10), stat='density')
cplt.save_figure(fig, name=f"kmeans_parallax_{cluster.name}", save_dir=figures_path)

fig, ax, g = cplt.plot_cluster_isochrone_curve(stars_df, xlim=(-1, 4), ylim=(3, 21))
cplt.save_figure(fig, name=f"kmeans_isochrone_{cluster.name}", save_dir=figures_path)

stars_df['cluster_g'].value_counts()

# Step 2 - Deep Embedded Clustering (DEC)
# https://arxiv.org/pdf/1511.06335.pdf
#
# Reference:
#     Unsupervised Deep Embedding for Clustering Analysis - 4.3 Implementation
# dims = [x.shape[-1], 500, 500, 2000, 10]
dims = [x.shape[-1], 50, 50, 200, n_clusters]

loss = 'kld'
optimizer = SGD(1, 0.9)
init = VarianceScaling(scale=1.0/3.0, mode='fan_in', distribution='uniform', seed=0)
#init = glorot_uniform(seed=0)

# DEC model
dec = DEC(dims=dims, n_clusters=n_clusters, initializer=init)
dec.compile(optimizer=optimizer, loss=loss)
dec.model.summary()

plot_model(dec.model, to_file=f'{results_path}/dec_model.png', show_shapes=True)
Image(filename=f'{results_path}/dec_model.png')

# Training parameters
epochs = 30
batch_size = 128
maxiter = 2000
update_interval = 20
verbose = 1

dec.pretrain(x, optimizer=optimizer, epochs=epochs, batch_size=batch_size)
dec.fit(x, batch_size=batch_size, maxiter=maxiter, update_interval=update_interval, verbose=verbose)

stars_df['cluster_g'] = np.array([f"g{g}" for g in dec.predict(x)], dtype=str)
stars_df['cluster_g'].value_counts()

fig, ax, g = cplt.plot_cluster_proper_motion(stars_df, xlim=(-30, 50), ylim=(-70, 40))
cplt.save_figure(fig, name=f"dec_pm_{cluster.name}", save_dir=figures_path)

fig, ax, g = cplt.plot_cluster_parallax_histogram(stars_df, xlim=(-4, 10), stat='density')
cplt.save_figure(fig, name=f"dec_parallax_{cluster.name}", save_dir=figures_path)

fig, ax, g = cplt.plot_cluster_isochrone_curve(stars_df, xlim=(-1, 4), ylim=(3, 21))
cplt.save_figure(fig, name=f"dec_isochrone_{cluster.name}", save_dir=figures_path)

filtered_df = None
q = 0.25
for i in [f"g{x}" for x in range(n_clusters)]:
    df = stars_df[stars_df['cluster_g'] == i]
    mask = filter_outliers(df['parallax'], q)
    if filtered_df is None:
        filtered_df = df[mask]
    else:
        filtered_df = pd.concat([filtered_df, df[mask]])

fig, ax, g = cplt.plot_cluster_proper_motion(filtered_df, xlim=(-30, 50), ylim=(-70, 40))
cplt.save_figure(fig, name=f"dec_pm_{cluster.name}_filtered", save_dir=figures_path)

fig, ax, g = cplt.plot_cluster_parallax_histogram(filtered_df, xlim=(-4, 10), stat='density')
cplt.save_figure(fig, name=f"dec_parallax_{cluster.name}_filtered", save_dir=figures_path)

fig, ax, g = cplt.plot_cluster_isochrone_curve(filtered_df, xlim=(-1, 4), ylim=(3, 21))
cplt.save_figure(fig, name=f"dec_isochrone_{cluster.name}_filtered", save_dir=figures_path)

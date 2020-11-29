import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

from .color_palette import color_palette

N_SAMPLES = 4000


def _resample_data(data: pd.DataFrame, n_samples: int) -> pd.DataFrame:
    if n_samples > 0 and data.shape[0] > n_samples:
        return data.sample(n_samples, random_state=0)
    return data


def _get_color_properties(data: pd.DataFrame, hue: str = None, **kwargs) -> dict:
    properties = dict()
    if hue is not None:
        hue_order = np.sort(pd.unique(data[hue]))
        palette = color_palette(n_colors=len(hue_order), **kwargs)

        properties.update({'hue': hue, 'hue_order': hue_order, 'palette': palette})
    else:
        properties['palette'] = color_palette(**kwargs)

    return properties


def _set_axis_properties(ax,
                         title: str = None,
                         xlabel: str = None,
                         ylabel: str = None,
                         xlim: tuple = None,
                         ylim: tuple = None,
                         invert_xaxis: bool = False,
                         invert_yaxis: bool = False):

    if title is not None:
        ax.set_title(title)

    if xlabel is not None:
        ax.set_xlabel(xlabel)

    if ylabel is not None:
        ax.set_ylabel(ylabel)

    if xlim is not None:
        ax.set_xlim(xlim)

    if ylim is not None:
        ax.set_ylim(ylim)

    if invert_xaxis:
        ax.invert_xaxis()

    if invert_yaxis:
        ax.invert_yaxis()


def plot_clusters_catalogue_distribution(data: pd.DataFrame,
                                         title: str = None,
                                         xlim: tuple = None,
                                         ylim: tuple = None,
                                         hue: str = 'diam'):

    fig, ax = plt.subplots(figsize=(12, 6), tight_layout=True)

    g = sns.scatterplot(data=data, x="ra", y="dec", hue=hue, size=hue, palette=color_palette(as_cmap=True), ax=ax)

    _set_axis_properties(ax,
                         title=title,
                         xlabel='Right Ascension (J2000 Degree)',
                         ylabel='Declination (J2000 Degree)',
                         xlim=xlim,
                         ylim=ylim)

    ax.legend().set_title("Diameter (arcmin)")

    return fig, ax, g


def plot_cluster_proper_motion(data: pd.DataFrame,
                               title: str = None,
                               xlim: tuple = None,
                               ylim: tuple = None,
                               hue: str = 'cluster_g',
                               legend: bool = True,
                               n_samples: int = N_SAMPLES):

    fig, ax = plt.subplots(figsize=(6, 6), tight_layout=True)

    data = _resample_data(data, n_samples)
    color_props = _get_color_properties(data, hue)

    g = sns.scatterplot(
        data=data,
        x="pmra",
        y="pmdec",
        s=12,
        ax=ax,
        legend=legend,
        **color_props,
    )

    _set_axis_properties(ax,
                         title=title,
                         xlabel=r'Proper Motion in Right Ascension Direction ($mas \cdot year^{-1}$)',
                         ylabel=r'Proper Motion in Declination Direction ($mas \cdot year^{-1}$)',
                         xlim=xlim,
                         ylim=ylim)

    return fig, ax, g


def plot_cluster_parallax_histogram(data,
                                    title: str = None,
                                    xlim: tuple = None,
                                    ylim: tuple = None,
                                    stat: str = 'count',
                                    bins='auto',
                                    hue: str = 'cluster_g',
                                    legend: bool = True,
                                    n_samples: int = N_SAMPLES):

    fig, ax = plt.subplots(figsize=(6, 6), tight_layout=True)

    data = _resample_data(data, n_samples)
    color_props = _get_color_properties(data, hue)

    g = sns.histplot(data=data, x='parallax', bins=bins, kde=True, stat=stat, ax=ax, legend=legend, **color_props)

    _set_axis_properties(ax, title=title, xlabel=r'Parallax ($mas$)', ylabel=stat.title(), xlim=xlim, ylim=ylim)

    return fig, ax, g


def plot_cluster_isochrone_curve(data: pd.DataFrame,
                                 title: str = None,
                                 xlim: tuple = None,
                                 ylim: tuple = None,
                                 hue: str = 'cluster_g',
                                 legend: bool = True,
                                 n_samples: int = N_SAMPLES):

    fig, ax = plt.subplots(figsize=(6, 6), tight_layout=True)

    data = _resample_data(data, n_samples)
    color_props = _get_color_properties(data, hue)

    g = sns.scatterplot(data=data, x="bp_rp", y="phot_g_mean_mag", s=12, ax=ax, legend=legend, **color_props)

    _set_axis_properties(ax,
                         title=title,
                         xlabel=r'$B_{mag} - R_{mag}$',
                         ylabel=r'$G_{mag}$',
                         xlim=xlim,
                         ylim=ylim,
                         invert_yaxis=True)

    return fig, ax, g

def pairplot(data: pd.DataFrame,
             kind: str = 'scatter',
             n_samples: int = N_SAMPLES):

    data = _resample_data(data, n_samples).copy()
    hue = 'cluster_g'
    data[hue] = 'g0'

    color_props = _get_color_properties(data, hue=hue)

    g = sns.pairplot(data=data, kind=kind, **color_props)
    g.legend.remove()
    g.tight_layout()

    return g


def save_figure(fig, name: str, img_ext: str = "pdf", save_dir='./'):
    name = name.replace(' ', '_').lower()
    fig.savefig(f"{save_dir}/{name}.{img_ext}")

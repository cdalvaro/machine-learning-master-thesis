import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .color_palette import color_palette


def plot_clusters_catalogue_distribution(data: pd.DataFrame,
                                         title: str = None,
                                         xlim: tuple = None,
                                         ylim: tuple = None,
                                         hue: str = 'diam'):
    fig, ax = plt.subplots(figsize=(12, 6))
    if title is not None:
        ax.set_title(title)

    ax.set_xlabel('Right Ascension (J2000 Degree)')
    ax.set_ylabel('Declination (J2000 Degree)')

    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)

    palette = None
    if hue is not None:
        n_colors = len(pd.unique(data[hue]))
        palette = color_palette(n_colors=n_colors)

    g = sns.scatterplot(data=data, x="ra", y="dec", hue=hue, size=hue, palette=palette, ax=ax)

    plt.legend().set_title("Diameter (arcmin)")

    return fig, ax, g


def plot_cluster_proper_motion(data: pd.DataFrame,
                               title: str = None,
                               xlim: tuple = None,
                               ylim: tuple = None,
                               hue: str = 'cluster_g',
                               legend: bool = True):
    fig, ax = plt.subplots(figsize=(6, 6))
    if title is not None:
        ax.set_title(title)

    ax.set_xlabel(r'Proper Motion in Right Ascension Direction ($mas \cdot year^{-1}$)')
    ax.set_ylabel(r'Proper Motion in Declination Direction ($mas \cdot year^{-1}$)')

    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)

    palette = None
    if hue is not None:
        n_colors = len(pd.unique(data[hue]))
        palette = color_palette(n_colors=n_colors)

    g = sns.scatterplot(data=data, x="pmra", y="pmdec", hue=hue, palette=palette, s=12, ax=ax, legend=legend)

    return fig, ax, g


def plot_cluster_parallax_histogram(df_cluster,
                                    title: str = None,
                                    xlim: tuple = None,
                                    ylim: tuple = None,
                                    stat: str = 'count',
                                    bins='auto',
                                    hue: str = 'cluster_g',
                                    legend: bool = True):
    fig, ax = plt.subplots(figsize=(6, 6), tight_layout=True)
    if title is not None:
        ax.set_title(title)

    ax.set_xlabel(r'Parallax ($mas$)')
    ax.set_ylabel(stat.title())

    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)

    palette = None
    if hue is not None:
        n_colors = len(pd.unique(df_cluster[hue]))
        palette = color_palette(n_colors=n_colors)

    g = sns.histplot(data=df_cluster,
                     x='parallax',
                     hue=hue,
                     palette=palette,
                     legend=legend,
                     bins=bins,
                     kde=True,
                     ax=ax,
                     stat=stat)

    return fig, ax, g


def plot_cluster_isochrone_curve(data: pd.DataFrame,
                                 title: str = None,
                                 xlim: tuple = None,
                                 ylim: tuple = None,
                                 hue: str = 'cluster_g',
                                 legend: bool = True):
    fig, ax = plt.subplots(figsize=(6, 6))
    if title is not None:
        ax.set_title(title)

    ax.set_xlabel(r'$B_{mag} - R_{mag}$')
    ax.set_ylabel(r'$G_{mag}$')

    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)

    palette = None
    if hue is not None:
        n_colors = len(pd.unique(data[hue]))
        palette = color_palette(n_colors=n_colors)

    g = sns.scatterplot(data=data,
                        x="bp_rp",
                        y="phot_g_mean_mag",
                        hue=hue,
                        size='parallax',
                        sizes=(2, 20),
                        palette=palette,
                        ax=ax,
                        legend=legend)

    ax.invert_yaxis()

    return fig, ax, g


def save_figure(fig, name: str, img_ext: str = "pdf", save_dir='./'):
    if save_dir is not None:
        name = name.replace(' ', '_').lower()
        fig.savefig(f"{save_dir}/{name}.{img_ext}")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .color_palette import color_palette, set_color_palette


class Plot:

    default_ext = 'pdf'

    def __init__(self, save_figs: bool = False, figs_path: str = '.'):
        self.save_figs = save_figs
        self.figs_path = figs_path
        set_color_palette()

    def plot_clusters_catalogue_distribution(self,
                                             df_catalogue,
                                             img_name: str,
                                             img_ext: str = default_ext,
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

        g = sns.scatterplot(data=df_catalogue,
                            x="ra",
                            y="dec",
                            hue=hue,
                            size=hue,
                            palette=color_palette(n_colors=len(pd.unique(df_catalogue[hue]))),
                            ax=ax)
        plt.legend().set_title("Diameter (arcmin)")

        if self.save_figs:
            self._save_figure(fig, name=img_name, img_ext=img_ext)

        return fig, ax, g

    def plot_cluster_proper_motion(self,
                                   df_cluster,
                                   img_name: str,
                                   img_ext: str = default_ext,
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

        g = sns.scatterplot(data=df_cluster,
                            x="pmra",
                            y="pmdec",
                            hue=hue,
                            palette=color_palette(n_colors=len(pd.unique(df_cluster[hue]))),
                            s=12,
                            ax=ax,
                            legend=legend)

        if self.save_figs:
            self._save_figure(fig, name=img_name, img_ext=img_ext)

        return fig, ax, g

    def plot_cluster_parallax_histogram(self,
                                        df_cluster,
                                        img_name: str,
                                        img_ext: str = default_ext,
                                        title: str = None,
                                        bins='auto',
                                        xlim: tuple = None,
                                        ylim: tuple = None,
                                        stat: str = 'count',
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

        g = sns.histplot(data=df_cluster,
                         x='parallax',
                         hue=hue,
                         palette=color_palette(n_colors=len(pd.unique(df_cluster[hue]))),
                         legend=legend,
                         bins=bins,
                         kde=True,
                         ax=ax,
                         stat=stat)

        if self.save_figs:
            self._save_figure(fig, name=img_name, img_ext=img_ext)

        return fig, ax, g

    def plot_cluster_isochrone_curve(self,
                                     df_cluster,
                                     img_name: str,
                                     img_ext: str = default_ext,
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

        g = sns.scatterplot(data=df_cluster,
                            x="bp_rp",
                            y="phot_g_mean_mag",
                            hue=hue,
                            palette=color_palette(n_colors=len(pd.unique(df_cluster[hue]))),
                            size='parallax',
                            sizes=(2, 20),
                            ax=ax,
                            legend=legend)

        ax.invert_yaxis()

        if self.save_figs:
            self._save_figure(fig, name=img_name, img_ext=img_ext)

        return fig, ax, g

    def _save_figure(self, fig, name: str, img_ext: str):
        name = name.replace(' ', '_').lower()
        fig.savefig(f"{self.figs_path}/{name}.{img_ext}")

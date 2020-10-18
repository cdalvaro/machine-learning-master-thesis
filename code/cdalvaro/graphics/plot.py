import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


class Plot:

    default_ext = 'pdf'

    def __init__(self, save_figs: bool = False, figs_path: str = '.'):
        self.save_figs = save_figs
        self.figs_path = figs_path

    def plot_clusters_catalogue_distribution(self,
                                             df_catalogue,
                                             img_name: str,
                                             img_ext: str = default_ext,
                                             title: str = None,
                                             xlim: tuple = None,
                                             ylim: tuple = None):
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
                            hue="diam",
                            size="diam",
                            palette="ch:r=-.5,l=.75",
                            ax=ax)
        plt.legend().set_title("Diameter (arcmin)")

        self._save_figure(fig, name=img_name, img_ext=img_ext)

    def plot_cluster_proper_motion(self,
                                   df_cluster,
                                   img_name: str,
                                   img_ext: str = default_ext,
                                   title: str = None,
                                   xlim: tuple = None,
                                   ylim: tuple = None):
        fig, ax = plt.subplots(figsize=(6, 6))
        if title is not None:
            ax.set_title(title)

        ax.set_xlabel(r'Proper Motion in Right Ascension Direction ($mas \cdot year^{-1}$)')
        ax.set_ylabel(r'Proper Motion in Declination Direction ($mas \cdot year^{-1}$)')

        if xlim is not None:
            ax.set_xlim(xlim)
        if ylim is not None:
            ax.set_ylim(ylim)

        g = sns.scatterplot(data=df_cluster, x="pmra", y="pmdec", hue="is_contained", s=12, ax=ax, legend=False)

        self._save_figure(fig, name=img_name, img_ext=img_ext)

    def plot_cluster_parallax_histogram(self,
                                        df_cluster,
                                        img_name: str,
                                        img_ext: str = default_ext,
                                        title: str = None,
                                        bins='auto',
                                        xlim: tuple = None,
                                        stat: str = 'count'):
        fig, ax = plt.subplots(figsize=(6, 6), tight_layout=True)
        if title is not None:
            ax.set_title(title)

        ax.set_xlabel(r'Parallax ($mas$)')
        ax.set_ylabel(stat.title())

        if xlim is not None:
            ax.set_xlim(xlim)

        g = sns.histplot(data=df_cluster,
                         x='parallax',
                         hue="is_contained",
                         legend=False,
                         bins=bins,
                         kde=True,
                         ax=ax,
                         stat=stat)

        self._save_figure(fig, name=img_name, img_ext=img_ext)

    def plot_cluster_isochrone_curve(self,
                                     df_cluster,
                                     img_name: str,
                                     img_ext: str = default_ext,
                                     title: str = None,
                                     xlim: tuple = None,
                                     ylim: tuple = None):
        fig, ax = plt.subplots(figsize=(6, 6))
        if title is not None:
            ax.set_title(title)

        ax.set_xlabel(r'$B_{mag} - R_{mag}$')
        ax.set_ylabel(r'G_{mag}')

        if xlim is not None:
            ax.set_xlim(xlim)
        if ylim is not None:
            ax.set_ylim(ylim)

        g = sns.scatterplot(data=df_cluster,
                            x="bp_rp",
                            y="phot_g_mean_mag",
                            hue="is_contained",
                            size='parallax',
                            sizes=(2, 20),
                            ax=ax,
                            legend=False)

        ax.invert_yaxis()

        self._save_figure(fig, name=img_name, img_ext=img_ext)

    def _save_figure(self, fig, name: str, img_ext: str):
        if self.save_figs:
            name = name.replace(' ', '_').lower()
            fig.savefig(f"{self.figs_path}/{name}.{img_ext}")

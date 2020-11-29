[![Python][python_badge]][python_link]
[![keras][keras_badge]][keras_link]
[![Jupyter][jupyter_badge]][notebooks_link]
[![Astropy][astropy_badge]][astropy_link]

[![gaia-downloader image][gaia_downloader_badge]][gaia_downlaoder_image]
[![latex-document][latex_document_badge]][latex_document_workflow]

# Open Clusters Characterization in Gaia DR2 Using ML Algorithms

<div align=center>
  <a href="https://www.unir.net"><img src="https://github.com/cdalvaro/machine-learning-master-thesis/raw/main/figures/unir-logo.png" alt="UNIR" title="UNIR" hspace="30" height="96px" /></a>
  <a href="https://sci.esa.int/gaia"><img src="https://github.com/cdalvaro/machine-learning-master-thesis/raw/main/figures/esa-gaia-logo.png" alt="ESA Gaia" title="ESA Gaia" hspace="30" height="96px" /></a>
</div>

<br/>

Author: [_Álvaro Yunta, Carlos D._][author_profile] ([@cdalvaro](https://github.com/cdalvaro))

Supervisor: [_Guzmán Álvarez, César A._][supervisor_profile] ([@cguz](https://github.com/cguz))

## Table of Contents

- [Abstract](#abstract)
- [Data](#data)
- [Code](#code)
- [Acknowledgement](#acknowledgement)
- [References](#references)

## Abstract

The characterization and knowledge of _Open Clusters_ allows us to better understand properties and mechanisms about the Universe
such as stellar formation and the regions where those events occur. They also provide information about stellar processes and the
evolution of the galactic disk.

In this work, we develope a method to characterize those clusters by using _artificial intelligence_ tools like clustering
by _K-Means_, or clustering based on _Artificial Neural Networks_ by implementing the _Deep Embedded Clustering_
model. We are using _Gaia DR2 database_ as data source for testing our models.

The developed method aims to improve the existing ones both in terms of _computational efficiency_, with lower computational requirements,
and _ease of use_, by reducing the number of hyperparameters to configure in order to obtain a good characterization of the analyzed clusters.

## Data

The data used in this project has been recovered from the [Gaia Mission][gaia_mission] <span id="a1">[[1]](#f1)</span> archive.
Exactly, from the [DR2][gaia_dr2] dataset <span id="a2">[[2]](#f2)</span>.

It is a catalogue that contains over 1.692 million registries of stars data.

In order to reduce the amount of data to be downloaded,
the [OPENCLUST][openclust] <span id="a3">[[3]](#f3)</span> catalogue has been used to restrict
the sky regions to those areas corresponding to the clusters inside the catalogue
giving an extra marging to take into account stars outside clusters.

<figure>
  <img src="https://github.com/cdalvaro/machine-learning-master-thesis/raw/main/figures/openclust_catalogue.svg" title="OpenClust Catalogue Distribution" heigh="256px">
  <figcaption align=center>OpenClust Catalogue Distribution</figcaption>
</figure>

## Code

All code used in this project is available inside [`src/`](src) directory.
It is written in Python and contains downloaders, data managers, and the ML algorithms described in the thesis.

For more information see: [src/README.md](src/README.md)

## Acknowledgement

This work has made use of data from the European Space Agency (ESA) mission _Gaia_ (https://www.cosmos.esa.int/gaia),
processed by the _Gaia_ Data Processing and Analysis Consortium
(DPAC, https://www.cosmos.esa.int/web/gaia/dpac/consortium).
Funding for the DPAC has been provided by national institutions, in particular the institutions participating in the
_Gaia_ Multilateral Agreement.

This publication makes use of VOSA, developed under the Spanish Virtual Observatory project
supported by the Spanish MINECO through grant AyA2017-84089.
VOSA has been partially updated by using funding from the European Union's Horizon 2020 Research
and Innovation Programme, under Grant Agreement nº 776403 (EXOPLANETS-A)

This research has made use of the VizieR catalogue access tool, CDS, Strasbourg, France (DOI : 10.26093/cds/vizier).
The original description of the VizieR service was published in 2000 (A&AS 143, 23, <span id="a4">[[4]](#f4)</span>).

## References

1. <span id="f1"></span> G. Collaboration et al. Description of the gaia mission (spacecraft, instruments, survey and measurement principles, and operations). _Gaia Collaboration et al.(2016a): Summary description of Gaia DR1_, 2016. [↩️](#a1)

2. <span id="f2"></span> C. Gaia, A. Brown, A. Vallenari, T. Prusti, J. de Bruijne, C. Babusiaux, Á. Juhász, G. Marschalkó, G. Marton, L. Molnár, et al. Gaia data release 2 summary of the contents and survey properties. _Astronomy & Astrophysics_, 616(1), 2018. [↩️](#a2)

3. <span id="f3"></span> W. Dias, B. Alessi, A. Moitinho, and J. Lépine. New catalogue of optically visible open clusters and candidates. _Astronomy & Astrophysics_, 389(3):871–873, 2002. URL https://heasarc.gsfc.nasa.gov/W3Browse/star-catalog/openclust.html. [↩️](#a3)

4. <span id="f4"></span> F. Ochsenbein, P. Bauer, and J. Marcout. The vizier database of astronomical catalogues. _Astronomy and Astrophysics Supplement Series_, 143(1):23–32, 2000. doi: [10.26093/cds/vizier](https://vizier.unistra.fr). [↩️](#a4)

[openclust]: https://heasarc.gsfc.nasa.gov/W3Browse/star-catalog/openclust.html
[author_profile]: https://cdalvaro.io
[supervisor_profile]: https://www.unir.net/profesores/cesar-augusto-guzman-alvarez/
[gaia_mission]: https://www.cosmos.esa.int/web/gaia/the-mission
[gaia_dr2]: https://www.cosmos.esa.int/web/gaia/data-release-2
[gaia_downloader_badge]: https://img.shields.io/github/workflow/status/cdalvaro/machine-learning-master-thesis/gaia-downloader%20image?style=flat-square&label=gaia-downloader&logo=Docker
[gaia_downlaoder_image]: https://github.com/users/cdalvaro/packages/container/package/gaia-downloader
[latex_document_badge]: https://img.shields.io/github/workflow/status/cdalvaro/machine-learning-master-thesis/Build%20LaTeX%20document?style=flat-square&label=LaTeX&logo=LaTeX&logoColor=008080
[latex_document_workflow]: https://github.com/cdalvaro/machine-learning-master-thesis/actions?query=workflow%3A%22Build+LaTeX+document%22
[python_badge]: https://img.shields.io/badge/Python-3.8-3776AB?style=flat-square&logo=Python
[python_link]: https://docs.python.org/3.8/contents.html "Python 3.8"
[keras_badge]: https://img.shields.io/badge/Keras-2.2-D00000?style=flat-square&logo=Keras&logoColor=D00000
[keras_link]: https://keras.io/api/ "Keras API"
[jupyter_badge]: https://img.shields.io/badge/Jupyter-Notebook-F37626?style=flat-square&logo=Jupyter
[notebooks_link]: src/notebooks "Jupyter Notebooks"
[astropy_badge]: https://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat-square
[astropy_link]: https://www.astropy.org/

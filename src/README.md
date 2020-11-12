[![Python][python_badge]][python_link]
[![keras][keras_badge]][keras_link]
[![Jupyter][jupyter_badge]][notebooks_link]
[![Astropy][astropy_badge]][astropy_link]

[![gaia-downloader image][gaia_downloader_badge]][gaia_downlaoder_image]
[![latex-document][latex_document_badge]][latex_document_workflow]

# Code

## Table of Contents

- [Python Package](#python-package)
- [Downloader](#downloader)
  - [Environment Variables](#environment-variables)
- [Notebooks](#notebooks)

## Python Package

The package developed for this project is available inside the [`cdalvaro/`](cdalvaro) directory.

It contains packages for:

- Downloading data from Gaia DR2 database.
- Retrieving data from the PostgreSQL database.
- Making plots and graphics.
- Modeling data structures.

## Downloader

Data download can be started by running the following command:

([Docker][docker] is required for this purpose)

```sh
cd src
docker-compose up --detach
```

A [PostgreSQL][postgresql] will be initiated and a container will start to download Gaia data.

```
gaia_downloader | INFO: Loading OpenClust catalogue ...
gaia_downloader | INFO: OpenClust catalogue loaded!
gaia_downloader | INFO: ⏱ Downloading Melotte 25 stars from Gaia DR2 ...
gaia_downloader | INFO: Query finished. [astroquery.utils.tap.core]
gaia_downloader | INFO: Downloaded 433996 stars for Melotte 25
```

### Environment Variables

The following environment variables can be established for tuning the downloader container:

| Parameter   | Description                                                                              |
| :---------- | :--------------------------------------------------------------------------------------- |
| `GAIA_USER` | Gaia DR2 username for login into https://gea.esac.esa.int/archive/. Disabled by default. |
| `GAIA_PASS` | Gaia DR2 password. Disabled by default.                                                  |

## Notebooks

[Jupyter Notebooks][jupyter] used for data analysing and model training are available inside the [`notebooks`](notebooks) directory.

[docker]: https://www.docker.com
[postgresql]: https://www.postgresql.org
[jupyter]: https://jupyter.org
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

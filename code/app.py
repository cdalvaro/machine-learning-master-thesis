#!/usr/bin/env python3

import argparse
from cdalvaro.data_base import DB
from cdalvaro.catalogues import OpenClust
from cdalvaro.downloaders.gaia import Gaia
from cdalvaro.logging import Logger
import logging
import os

parser = argparse.ArgumentParser(prog='Gaia DR2 Downloader', description='✨ Stars downloader from the GAIA DR2 dataset')
parser.add_argument('--cluster',
                    '-c',
                    nargs='+',
                    type=str,
                    default='ALL',
                    help="""
        Cluster name from http://cdsarc.u-strasbg.fr/ftp/cats/B/ocl/clusters.dat list.
        Type ALL to download all of them.
        """)
parser.add_argument('--verbose', '-v', action='count', default=0)

args = parser.parse_args()

# Logger settings
log_level = logging.WARNING
if args.verbose == 1:
    log_level = logging.INFO
elif args.verbose > 1:
    log_level = logging.DEBUG

logger = Logger.instance()
logger.setLevel(log_level)

# Select clusters
catalogue = OpenClust.load_catalogue()
if len(args.cluster) == 1 and 'ALL' in args.cluster:
    clusters = set(catalogue.values())
else:
    clusters = set()
    for cluster_name in args.cluster:
        if cluster_name in catalogue.keys():
            clusters.add(catalogue[cluster_name])
        else:
            logger.error(f"Cluster '{cluster_name}' is not avaiable at the OpenClust catalogue")
            exit(1)

db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', 5432)

gaia = Gaia(db=DB.instance(host=db_host, port=db_port))
gaia.download(regions=clusters, extra_size=1.5)

logger.info("🚀 Gaia downloader has finished downloading data")

#!/usr/bin/env python3

import argparse
from cdalvaro import DB, Logger
from cdalvaro.catalogues import OpenClust
from cdalvaro.downloaders import Gaia
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
parser.add_argument('--extra_size',
                    type=float,
                    default=1.5,
                    help="""
        Extra size to extend regions to be downloaded.
        Default to 1.5
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
catalogue = OpenClust.catalogue()
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
gaia.download_and_save(regions=clusters, extra_size=args.extra_size)

logger.info("🚀 Gaia downloader has finished retrieving and saving data")

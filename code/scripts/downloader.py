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
                    default={'ALL'},
                    help="""
        Cluster name from http://cdsarc.u-strasbg.fr/ftp/cats/B/ocl/clusters.dat list.
        Type ALL to download all of them.
        """)
parser.add_argument('--exclude',
                    '-e',
                    nargs='*',
                    type=str,
                    default={},
                    help="""
        Clusters to be ignored from the download. Default to empty.
        """)
parser.add_argument('--extra-size',
                    '-s',
                    dest='extra_size',
                    type=float,
                    default=1.5,
                    help="""
        Extra size to extend regions to be downloaded.
        Default to 1.5.
        """)

update_data_parser = parser.add_mutually_exclusive_group(required=False)
update_data_parser.add_argument('--update-data',
                                '-u',
                                dest='update_data',
                                action='store_true',
                                help="""
        Update existing clusters with new data. Default.
        """)
update_data_parser.add_argument('--no-update-data', dest='update_data', action='store_false')
update_data_parser.set_defaults(update_data=True)

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

if len(args.exclude) > 0:
    clusters = set(filter(lambda x: x not in args.exclude, clusters))

db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', 5432)
db = DB.instance(host=db_host, port=db_port)

if not args.update_data:
    logger.info("Existing regions won't be updated")
    existing_clusters = db.get_regions().keys()
    clusters = set(filter(lambda x: x not in existing_clusters, clusters))

if len(clusters) == 0:
    logger.info("🍻 All regions are already downloaded")
    exit(0)

gaia_username = os.getenv('GAIA_USER', None)
gaia_password = os.getenv('GAIA_PASS', None)

Gaia.partition_size = os.getenv('GAIA_PARTITION_SIZE', 500_000)

gaia = Gaia(db=db, username=gaia_username, password=gaia_password)
gaia.download_and_save(regions=clusters, extra_size=args.extra_size)

logger.info("🚀 Gaia downloader has finished retrieving and saving data")
exit(0)

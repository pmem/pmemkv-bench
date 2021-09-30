#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2020-2021, Intel Corporation

import logging
import os
import argparse
import json
import csv
from pymongo import MongoClient

logger = logging.getLogger(__name__)


def csv_load(file_handler):
    OutputReader = csv.DictReader(file_handler.read().split("\n"), delimiter=",")
    return [x for x in OutputReader]


def preprocess(d):
    """Mongodb uses '.' character as part of query syntax, so it needs to be replaced in keys"""
    if isinstance(d, dict):
        for k, v in d.items():
            return {
                ("metric" if "name" in k else k.replace(".", "_")): preprocess(v)
                for k, v in d.items()
            }
    elif isinstance(d, list):
        return [preprocess(x) for x in d]
    else:
        return d


def upload_to_mongodb(address, port, username, password, db_name, collection, data):

    logger = logging.getLogger("mongodb")
    client = MongoClient(address, int(port), username=username, password=password)
    with client:
        db = client[db_name]
        collection = db[collection]
        result = collection.insert_one(preprocess(data))
        logger.info(f"Inserted: {result} into {address}:{port}/{db_name}")


if __name__ == "__main__":
    help_msg = """
Custom uploader to mongodb.
Environment variables for MongoDB client configuration:
    MONGO_ADDRESS, MONGO_PORT, MONGO_USER, MONGO_PASSWORD, MONGO_DB_NAME and MONGO_DB_COLLECTION
 """
    # Parse arguments
    parser = argparse.ArgumentParser(
        description=help_msg, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("json_path")
    parser.add_argument("--csv_path", action="append", default=[])
    parser.add_argument("-v", help="verbose", action="store_true")
    args = parser.parse_args()

    logger = logging.getLogger("uploader")
    # Setup database
    db_passwd = None
    db_address = db_port = db_user = db_name = db_collection = None
    try:
        db_address = os.environ["MONGO_ADDRESS"]
        db_port = os.environ["MONGO_PORT"]
        db_user = os.environ["MONGO_USER"]
        db_passwd = os.environ["MONGO_PASSWORD"]
        db_name = os.environ["MONGO_DB_NAME"]
        db_collection = os.environ["MONGO_DB_COLLECTION"]
    except KeyError as e:
        logger.warning(
            f"Environment variable {e} was not specified, so results cannot be uploaded to the database"
        )
    data = None
    with open(args.json_path) as json_file:
        data = json.load(json_file)
    for csv_path in args.csv_path:
        with open(csv_path) as csv_file:
            data[os.path.basename(csv_path)] = csv_load(csv_file)
    if args.v:
        # Print json, which would be uploaded to the database.
        print(json.dumps(data, indent=4, sort_keys=True))

    upload_to_mongodb(
        db_address, db_port, db_user, db_passwd, db_name, db_collection, data
    )

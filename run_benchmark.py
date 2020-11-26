#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2020, Intel Corporation

import tempfile
import os
import json
import argparse
import subprocess
import csv
import glob
import logging
import sys

from pymongo import MongoClient
import pymongo.errors

logger = logging.getLogger(__name__)
sys.excepthook = lambda ex_type, ex, traceback: logger.error(
    f"{ex_type.__name__}: {ex}"
)


class Repository:
    def __init__(self, config: dict):
        self.logger = logging.getLogger(__name__)

        self.directory = tempfile.TemporaryDirectory()
        self.path = self.directory.name
        self.url = config["repo_url"]
        self.commit = config["commit"]
        self.clone()
        self.checkout()

    def __str__(self):
        return f"{self.url} in {self.path}"

    def checkout(self):
        self.logger.info(f"Checking out commit: {self.commit}")
        subprocess.run(
            "git checkout".split() + [self.commit], cwd=self.path, check=True
        )

    def clone(self):
        self.logger.info(f"Cloning repository: {self.url}")
        subprocess.run("git clone".split() + [self.url, self.path], check=True)


class CmakeProject:
    def __init__(self, config: dict, dependencies: list = []):
        self.logger = logging.getLogger(__name__)

        self.repo = Repository(config)
        self.path = self.repo.path
        self.install_dir = tempfile.TemporaryDirectory()
        self.install_path = self.install_dir.name
        self.deps = dependencies
        self.pkg_config_path = [self.path]
        for d in self.deps:
            self.pkg_config_path.extend(d.pkg_config_path)

        # Configure Build environment
        self.build_env = config["env"]
        self.build_env["PKG_CONFIG_PATH"] = self.format_pkg_config_path()
        self.build_env["PATH"] = os.environ["PATH"]
        self.cmake_params = [f"-DCMAKE_INSTALL_PREFIX={self.install_path}"] + config[
            "cmake_params"
        ]

    def format_pkg_config_path(self):
        return ":".join(path for path in self.pkg_config_path)

    def build(self):
        cpus = f"{os.cpu_count()}"
        self.logger.info(f"{self.build_env}=")
        self.logger.info(f"building {self.repo}")
        try:
            subprocess.run(
                "cmake .".split() + self.cmake_params,
                env=self.build_env,
                cwd=self.path,
                check=True,
            )
            subprocess.run(
                ["make", "-j", cpus, "install"],
                env=self.build_env,
                cwd=self.path,
                check=True,
            )
            self.logger.debug(f"install dir: {os.listdir(self.install_path)}")
        except subprocess.CalledProcessError as e:
            self.logger.info(f"Cannot build project: {e.output}")
            raise e


class DB_bench:
    def __init__(self, config: dict, pmemkv: CmakeProject):
        self.logger = logging.getLogger(__name__)

        self.repo = Repository(config)
        self.path = self.repo.path
        self.pmemkv = pmemkv
        self.run_output = None
        self.env = config["env"]
        self.benchmark_params = config["params"]

    def build(self):
        build_env = {
            "PATH": os.environ["PATH"],
            "PKG_CONFIG_PATH": self.pmemkv.format_pkg_config_path(),
        }
        self.logger.debug(f"{build_env=}")
        self.logger.info(f"building {self.repo}")

        try:
            subprocess.run(
                "make bench".split(), env=build_env, cwd=self.path, check=True
            )
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Cannot build benchmark: {e}")
            raise e

    def run(self):
        find_file_path = lambda root_dir, filename: ":".join(
            set(
                os.path.dirname(x)
                for x in glob.glob(root_dir + f"/**/{filename}", recursive=True)
            )
        )

        try:
            env = self.env
            env["PATH"] = self.path + ":" + os.environ["PATH"]
            env["LD_LIBRARY_PATH"] = find_file_path(self.pmemkv.install_path, "*.so.*")
            self.logger.debug(f"{env=}")
            self.run_output = subprocess.run(
                ["pmemkv_bench", "--csv_output"] + self.benchmark_params,
                cwd=self.path,
                env=env,
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            self.logger.error(f"benchmark process failed: {e.stdout} ")
            self.logger.error(self.run_output)
            self.logger.error(f"with error: {e.stderr} ")
            raise e

    def get_results(self):
        OutputReader = csv.DictReader(
            self.run_output.stdout.decode("UTF-8").split("\n"), delimiter=","
        )
        return [dict(x) for x in OutputReader]


def upload_to_mongodb(address, port, username, password, db_name, collection, data):
    client = MongoClient(address, int(port), username=username, password=password)
    with client:
        db = client[db_name]
        collection = db[collection]
        collection.insert_one(data)


def print_results(results_dict):
    print(json.dumps(results_dict, indent=4, sort_keys=True))


def main():
    help_msg = """
Runs pmemkv-bench for pmemkv and libpmemobjcpp defined in configuration json

+-------------------------------------+
|       run_benchmark.py              |
|                                     |       +-----------------------+
| +------------------------+          |       | libpmemobj-cpp        |
| | libpmemobjcpp          |          |       | git repository        |
| | +----------------------+ <----------------+                       |
| | Downloads and builds   |          |       |                       |
| | libpmemobj+cpp         |          |       +-----------------------+
| | project                |          |
| +------------------------+          |
|                                     |
|                                     |       +-----------------------+
| +------------------------+          |       | pmemkv                |
| | pmemkv                 |          |       | git repository        |
| | +----------------------+ <----------------+                       |
| | Downloads and builds   |          |       |                       |
| | pmemk^ project         |          |       +-----------------------+
| +------------------------+          |
|                                     |
|                                     |       +-----------------------+
| +------------------------+          |       | pmemkv+tools          |
| | pmemkv bench           |          |       | git repository        |
| | +----------------------+ <----------------+                       |
| | Runs benchmark and     |          |       |                       |
| | uploads results to     |          |       +-----------------------+
| | mongoDB                |          |
| |                        |          |       --------------------------+
| |                        +----------------->+ MongoDB instance        |
| +------------------------+          |       | +-----------------------+
|                                     |       | Collects benchmarks     |
|                                     |       | results                 |
|                                     |       +----------+--------------+
+-------------------------------------+                  |
                                                         v
                                              +----------+--------------+
                                              |  MongoDB Charts         |
                                              |  +----------------------+
                                              |  Displays collected data|
                                              +-------------------------+

Environment variables for MongoDB client configuration:
  MONGO_ADDRESS, MONGO_PORT, MONGO_USER, MONGO_PASSWORD, MONGO_DB_NAME and MONGO_DB_COLLECTION
"""
    # Setup loglevel
    LOGLEVEL = os.environ.get("LOGLEVEL") or "INFO"
    logging.basicConfig(level=LOGLEVEL)

    # Parse arguments
    parser = argparse.ArgumentParser(
        description=help_msg, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("config_path", help="Path to json config file")
    args = parser.parse_args()
    logger.info(f"{args.config_path=}")

    # Setup database
    db_address = db_port = db_user = db_passwd = db_name = None
    try:
        db_address = os.environ["MONGO_ADDRESS"]
        db_port = os.environ["MONGO_PORT"]
        db_user = os.environ["MONGO_USER"]
        db_passwd = os.environ["MONGO_PASSWORD"]
        db_name = os.environ["MONGO_DB_NAME"]
        db_collection = os.environ["MONGO_DB_COLLECTION"]
    except KeyError as e:
        logger.warning(
            f"Environmet variable {e} was not specified, so results cannot be uploaded to the database"
        )

    config = None
    with open(args.config_path) as config_path:
        config = json.loads(config_path.read())
    logger.info(config)

    libpmemobjcpp = CmakeProject(config["libpmemobjcpp"])
    libpmemobjcpp.build()

    pmemkv = CmakeProject(config["pmemkv"], dependencies=[libpmemobjcpp])
    pmemkv.build()

    benchmark = DB_bench(config["db_bench"], pmemkv)

    benchmark.build()
    benchmark.run()
    benchmark_results = benchmark.get_results()

    report = {key: config[key] for key in config}
    report["results"] = benchmark_results

    print_results(report)
    if db_address and db_port and db_user and db_passwd and db_name and db_collection:
        upload_to_mongodb(
            db_address, db_port, db_user, db_passwd, db_name, db_collection, report
        )
    else:
        logger.warning("Results not uploaded to database")


if __name__ == "__main__":
    main()

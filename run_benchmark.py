import tempfile
import os
import json
import argparse
import subprocess
import csv
import glob
import logging

from pymongo import MongoClient

logger = logging.getLogger(__name__)


class Repository:
    def __init__(self, config: dict):
        self.logger = logging.getLogger(__name__)

        self.dir = tempfile.mkdtemp()
        self.url = config["repo_url"]
        self.commit = config["commit"]
        self.clone()
        self.checkout()

    def checkout(self):
        self.logger.info(f"Checking out commit: {self.commit}")
        subprocess.run("git checkout".split() + [self.commit], cwd=self.dir, check=True)

    def clone(self):
        self.logger.info(f"Cloning repository: {self.url}")
        subprocess.run("git clone".split() + [self.url, self.dir], check=True)

    def get_path(self, filename):
        search_expression = self.dir + f"/**/{filename}"
        return os.path.dirname(glob.glob(search_expression, recursive=True)[0])


class DB_bench:
    def __init__(self, config: dict, repo: Repository, pmemkv_repo: Repository):
        self.logger = logging.getLogger(__name__)

        self.path = repo.dir
        self.pmemkv_path = pmemkv_repo.dir
        self.pmemkv = pmemkv_repo
        self.run_output = None
        self.env = config["env"]
        self.benchmark_params = config["params"]

    def build(self):
        library_path = self.pmemkv.get_path("libpmemkv.so.1")
        include_path = self.pmemkv.get_path("libpmemkv.hpp")
        build_env = {
            "LIBRARY_PATH": library_path,
            "CPLUS_INCLUDE_PATH": include_path,
            "PATH": os.environ["PATH"],
        }
        self.logger.debug(f"{build_env}=")
        try:
            subprocess.run(
                "make bench".split(), env=build_env, cwd=self.path, check=True
            )
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Cannot build benchmark: {e}")
            raise e

    def run(self):
        try:
            env = self.env
            env["PATH"] = self.path + ":" + os.environ["PATH"]
            env["LD_LIBRARY_PATH"] = self.pmemkv.get_path("libpmemkv.so.1")
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


class Pmemkv:
    def __init__(self, config: dict, repo: Repository):
        self.logger = logging.getLogger(__name__)

        self.repo = repo
        self.path = self.repo.dir
        self.build_env = config["env"]
        self.build_env["PATH"] = os.environ["PATH"]
        self.cmake_params = config["cmake_params"]

    def build(self):
        cpus = f"{os.cpu_count()}"
        self.logger.info(f"{self.build_env}=")
        try:
            subprocess.run(
                "cmake .".split() + self.cmake_params,
                env=self.build_env,
                cwd=self.path,
                check=True,
            )
            subprocess.run(
                ["make", "-j", cpus], env=self.build_env, cwd=self.path, check=True
            )
        except subprocess.CalledProcessError as e:
            self.logger.info(f"Cannot build pmemkv: {e.output}")
            raise e
        pass


def upload_to_mongodb(address, port, username, password, db_name, data):
    client = MongoClient(address, int(port), username=username, password=password)
    with client:
        db = client[db_name]
        column = db["test_data"]
        column.insert_one(data)


def print_results(results_dict):
    print(json.dumps(results_dict, indent=4, sort_keys=True))


if __name__ == "__main__":

    # Setup loglevel
    LOGLEVEL = os.environ.get("LOGLEVEL") or "INFO"
    lvl = {"DEBUG": logging.DEBUG, "INFO": logging.INFO}
    logging.basicConfig(level=lvl[LOGLEVEL])

    # Parse arguments
    parser = argparse.ArgumentParser(description="Runs pmemkv_bench")
    parser.add_argument("config_path", help="Path to json config file")
    args = parser.parse_args()
    logger.info(args.config_path)

    # Setup database
    try:
        db_address = os.environ["MONGO_ADDRESS"]
        db_port = os.environ["MONGO_PORT"]
        db_user = os.environ["MONGO_USER"]
        db_passwd = os.environ["MONGO_PASSWORD"]
        db_name = os.environ["MONGO_DB_NAME"]

    except KeyError as e:
        logger.warning(
            f"Environmet variable {e} was not specified, so results cannot be uploaded to the database"
        )

    config = None
    with open(args.config_path) as config_path:
        config = json.loads(config_path.read())
    logger.info(config)

    pmemkv_repo = Repository(config["pmemkv"])
    pmemkv = Pmemkv(config["pmemkv"], pmemkv_repo)
    pmemkv.build()

    db_bench_repo = Repository(config["db_bench"])
    benchmark = DB_bench(config["db_bench"], db_bench_repo, pmemkv_repo)

    benchmark.build()
    benchmark.run()
    benchmark_results = benchmark.get_results()

    raport = {key: config[key] for key in config}
    raport["results"] = benchmark_results

    print_results(raport)
    try:
        upload_to_mongodb(db_address, db_port, db_user, db_passwd, db_name, raport)
    except pymongo.errors as e:
        logger.error(f"Cannot upload results to database: {e}")
        exit(42)

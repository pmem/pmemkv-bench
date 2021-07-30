#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2020-2021, Intel Corporation

import tempfile
import os
import json
import argparse
import subprocess
import csv
import glob
import logging
import sys
from importlib import util as import_util
from jsonschema import validate
import tempfile
import datetime

logger = logging.getLogger(__name__)
sys.excepthook = lambda ex_type, ex, traceback: logger.error(
    f"{ex_type.__name__}: {ex}"
)

RESULTS_ROOT_DIRECTORY = os.environ.get("PMEMKV_BENCH_RESULTS_DIR", "results")


class CmdLine:
    """Wrapper for list, which may be passed to subprocess. It allows to construct POSIX style commands
    from parameters passed as the dictionary"""

    def __init__(self):
        self.cmdline = []

    def append(self, app, params: dict):
        params_list = []
        for key in params:
            if params[key] == "":
                params_list.append(key)
            else:
                params_list.append(f"{key}={params[key]}")
        print(f"{params_list=}")
        self.cmdline.extend([app] + params_list)

    def __str__(self):
        return " ".join(self)

    def __getitem__(self, item):
        return self.cmdline[item]


class Emon:
    def __init__(self):
        self.logger = logging.getLogger(type(self).__name__)
        self._emon_process = None
        self._log = tempfile.TemporaryFile()

    def start(self):
        logger.info("Start emon")
        cmd = "emon -collect-edp"
        self._emon_process = subprocess.Popen(cmd, stdout=self._log, shell=True)

    def stop(self, timeout=None):
        logger.info("Stop emon")
        subprocess.run("emon -stop", shell=True)
        self._emon_process.wait(timeout=timeout)

    def get_data(self):
        if self._emon_process:
            if self._emon_process.poll() != None:
                self._log.seek(0)
                return self._log.read().decode()
        return None

    def __del__(self):
        if self._emon_process != None:
            if self._emon_process.poll() == None:
                self.stop(60)


class Repository:
    def __init__(self, config: dict):
        self.logger = logging.getLogger(type(self).__name__)

        self.url = config["repo_url"]
        self.directory = tempfile.TemporaryDirectory(
            prefix=self.url.replace("/", ".").replace(":", ".")
        )
        self.path = self.directory.name
        self.commit = config["commit"]
        self.clone()
        self.checkout()
        config["commit"] = self._resolve_sha()

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

    def _resolve_sha(self):
        rev_parsed_commit = subprocess.run(
            ["git", "rev-parse", self.commit],
            cwd=self.path,
            capture_output=True,
            check=True,
            universal_newlines=True,
        ).stdout
        self.logger.info(f"Commit sha: {rev_parsed_commit}")
        return rev_parsed_commit


class CmakeProject:
    def __init__(self, config: dict, dependencies: list = []):
        self.logger = logging.getLogger(type(self).__name__)

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
        self.logger = logging.getLogger(type(self).__name__)

        self.repo = Repository(config)
        self.path = self.repo.path
        self.pmemkv = pmemkv
        self.run_output = None
        self.env = config["env"]

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

    def run(self, environ, benchmark_params, numactl_params=None):
        find_file_path = lambda root_dir, filename: ":".join(
            set(
                os.path.dirname(x)
                for x in glob.glob(root_dir + f"/**/{filename}", recursive=True)
            )
        )
        env = {}
        for d in (self.env, environ):
            env.update(d)
        env["PATH"] = self.path + ":" + os.environ["PATH"]
        env["LD_LIBRARY_PATH"] = find_file_path(self.pmemkv.install_path, "*.so.*")
        self.logger.debug(f"{env=}")
        cmd = CmdLine()
        if numactl_params:
            cmd.append("numactl", numactl_params)
        cmd.append("pmemkv_bench", benchmark_params)
        logger.info(cmd)

        try:
            self.run_output = subprocess.run(
                cmd,
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

    def cleanup(self, benchmark_params):
        db_path = benchmark_params["--db"]
        if os.path.isfile(db_path):
            subprocess.run(["pmempool", "rm", db_path], cwd=self.path, check=True)
        self.logger.info(f"{db_path} cleaned")

    def get_results(self):
        OutputReader = csv.DictReader(
            self.run_output.stdout.decode("UTF-8").split("\n"), delimiter=","
        )
        return [x for x in OutputReader]


def print_results(results_dict):
    print(json.dumps(results_dict, indent=4, sort_keys=True))


def save_results(results_dict, emon_output=None):
    basename = "pmemkv_bench_results"
    suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S_%f")
    dirname = "_".join([basename, suffix])
    results_path = os.path.join(RESULTS_ROOT_DIRECTORY, dirname)
    os.makedirs(results_path)
    output_file = os.path.join(results_path, "result.json")
    with open(output_file, "w") as outfile:
        json.dump(results_dict, outfile, indent=4, sort_keys=True)

    if emon_output:
        with open(os.path.join(results_path, "emon.dat"), "w") as emon_file:
            emon_file.write(emon_output)


def load_scenarios(path, schema_path=None):
    bench_params = None
    if path.endswith(".py"):
        spec = import_util.spec_from_file_location("cfg", path)
        cfg = import_util.module_from_spec(spec)
        spec.loader.exec_module(cfg)
        try:
            bench_params = cfg.generate()
        except AttributeError:
            raise AttributeError(
                f"Cannot execute 'generate' function from user provided generator script: {path} "
            )
    else:
        with open(path, "r") as config_path:
            bench_params = json.loads(config_path.read())
    if schema_path:
        with open(schema_path, "r") as schema_file:
            schema = json.loads(schema_file.read())
            validate(instance=bench_params, schema=schema)
    return bench_params


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
| | libpmemobj-cpp         |          |       +-----------------------+
| | project                |          |
| +------------------------+          |
|                                     |
|                                     |       +-----------------------+
| +------------------------+          |       | pmemkv                |
| | pmemkv                 |          |       | git repository        |
| | +----------------------+ <----------------+                       |
| | Downloads and builds   |          |       |                       |
| | pmemkv project         |          |       +-----------------------+
| +------------------------+          |
|                                     |
|                                     |       +-----------------------+
| +------------------------+          |       | pmemkv-bench          |
| | pmemkv bench           |          |       | git repository        |
| | +----------------------+ <----------------+                       |
| | Runs benchmark         |          |       |                       |
| +------------------------+          |       +-----------------------+
+-------------------------------------+
"""
    # Setup loglevel
    LOGLEVEL = os.environ.get("LOGLEVEL") or "INFO"
    logging.basicConfig(level=LOGLEVEL)

    # Parse arguments
    parser = argparse.ArgumentParser(
        description=help_msg, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "build_config_path",
        help="""Path to json config file or python script, which provides generate() method.
This parameter sets configuration of build process. Input structure is specified by bench_scenarios/build.schema.json""",
    )
    parser.add_argument(
        "benchmark_config_path",
        help="""Path to json config file or python script, which provides generate() method.
This parameter sets configuration of benchmarking process. Input structure is specified by bench_scenarios/bench.schema.json""",
    )
    args = parser.parse_args()
    logger.info(f"{args.build_config_path=}")

    schema_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "bench_scenarios"
    )

    config = load_scenarios(
        args.build_config_path, os.path.join(schema_dir, "build.schema.json")
    )
    logger.info(json.dumps(config, indent=4))

    bench_params = load_scenarios(
        args.benchmark_config_path, os.path.join(schema_dir, "bench.schema.json")
    )
    logger.info(json.dumps(bench_params, indent=4))

    libpmemobjcpp = CmakeProject(config["libpmemobjcpp"])
    libpmemobjcpp.build()

    pmemkv = CmakeProject(config["pmemkv"], dependencies=[libpmemobjcpp])
    pmemkv.build()

    benchmark = DB_bench(config["db_bench"], pmemkv)

    benchmark.build()

    reports = []
    for test_case in bench_params:
        emon = Emon()
        logger.info(f"Running: {test_case}")
        if test_case.get("emon") == "True":
            emon.start()
        benchmark.run(
            test_case["env"], test_case["pmemkv_bench"], test_case.get("numactl")
        )
        if test_case.get("emon") == "True":
            emon.stop()
        if test_case.get("cleanup", 0) != 0:
            benchmark.cleanup(test_case["pmemkv_bench"])
        benchmark_results = benchmark.get_results()

        report = {}
        report["build_configuration"] = config
        report["runtime_parameters"] = test_case
        report["results"] = benchmark_results
        reports.append(report)

        print_results(report)

        emon_data = None
        if test_case.get("emon") == "True":
            emon_data = emon.get_data()

        save_results(report, emon_data)

    return reports


if __name__ == "__main__":
    main()

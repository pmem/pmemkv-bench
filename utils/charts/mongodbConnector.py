#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021, Intel Corporation

from collections import defaultdict
from pymongo import MongoClient
import json
import pprint

# Shorten most used fields' names to ease grouping step
# and convert strings to actual data types.
DEFAULT_AGGR_ADD_FIELDS = {
    "$addFields": {
        "engine": "$runtime_parameters.params.--engine",
        "threads": {
            "$convert": {
                "input": "$runtime_parameters.params.--threads",
                "to": "int",
                "onError": "null",
            }
        },
        "num": {
            "$convert": {
                "input": "$runtime_parameters.params.--num",
                "to": "int",
                "onError": "null",
            }
        },
        "value_size": {
            "$convert": {
                "input": "$runtime_parameters.params.--value_size",
                "to": "int",
                "onError": "null",
            }
        },
        "key_size": {
            "$convert": {
                "input": "$runtime_parameters.params.--key_size",
                "to": "int",
                "onError": "null",
            }
        },
        "throughput": {
            "$convert": {
                "input": "$results.throughput [MB/s]",
                "to": "double",
                "onError": "null",
            }
        },
        "ops/sec": {
            "$convert": {"input": "$results.ops/sec", "to": "double", "onError": "null"}
        },
        "P9999": {
            "$convert": {
                "input": "$results.Percentilie P99_990000 [micros/op]",
                "to": "double",
                "onError": "null",
            }
        },
        "Date": {
            "$convert": {"input": "$results.Date:", "to": "date", "onError": "null"}
        },
    }
}
# Project grouped data into x, y and color (to simplify usage on plots)
DEFAULT_AGGR_PROJECT = {
    "$project": {
        "y": "$__alias_0",
        "x": "$_id.__alias_1",
        "color": "$_id.__alias_2",
        "_id": 0,
    }
}
# Sort for convenience of usage in plots creating process
DEFAULT_AGGR_SORT = {"$sort": {"color": 1, "x": 1}}


class MongodbConnector:
    """
    MongoDB connector class
    """

    @staticmethod
    def get_mongo_client(config):
        """
        Create MongoDB client

        @return: MongoDB client instance
        @rtype: MongoClient
        """
        mongo = MongoClient(
            host=config["address"],
            port=int(config["port"]),
            username=config["user"],
            password=config["password"],
        )
        return mongo

    @staticmethod
    def get_objects_aggregate(db_config, aggregation_params):
        """
        Get aggregated list of data objects from MongoDB
        @param config: Config with DB info
        @type config: dict
        XXX
        @return: List of objects imported from MongoDB
        @rtype: List
        """
        try:
            engines = aggregation_params["engines"]
            value_sizes = aggregation_params["value_sizes"]
            key_sizes = aggregation_params["key_sizes"]
            benchmark = aggregation_params["benchmark"]
            date_from = aggregation_params["date_from"]
            group_by_1 = aggregation_params["group_by_1"]
            group_by_2 = aggregation_params["group_by_2"]
            group_by_aggr = aggregation_params["group_by_aggr"]
        except KeyError as e:
            print(f"Aggregation param {e} is required")
            exit(1)

        emon_enabled = aggregation_params.get("emon_enabled", None)
        nums = aggregation_params.get("nums", None)
        threads = aggregation_params.get("threads", None)
        benchmarks_sets = aggregation_params.get("benchmarks_sets", None)

        ### Standard beginning of a pipeline ###
        # Make separate document for each result in "results" array
        aggregate_pipeline = [{"$unwind": "$results"}]
        # Define new fields (especially with data conversions, from strings)
        aggregate_pipeline.append(DEFAULT_AGGR_ADD_FIELDS)

        ### Match (filter) results ###
        # required filters
        match_pipeline = {
            "$match": {
                "engine": {"$in": engines},
                "results.Benchmark": {"$in": [benchmark]},
                "value_size": {"$in": value_sizes},
                "key_size": {"$in": key_sizes},
                "$expr": {
                    "$gte": [
                        "$Date",
                        {
                            "$dateFromString": {
                                "dateString": date_from,
                                "timezone": "Europe/Warsaw",
                            }
                        },
                    ]
                },
            }
        }
        # optional filters
        if not emon_enabled == None:
            emon = ["1"] if emon_enabled else ["0"]
            match_pipeline["$match"].update({"runtime_parameters.emon": {"$in": emon}})
        if not nums == None:
            match_pipeline["$match"].update({"num": {"$in": nums}})
        if not threads == None:
            match_pipeline["$match"].update({"threads": {"$in": threads}})
        if not benchmarks_sets == None:
            match_pipeline["$match"].update(
                {"runtime_parameters.params.--benchmarks": {"$in": benchmarks_sets}}
            )

        aggregate_pipeline.append(match_pipeline)

        ### Group by ###
        group_by_1 = "$" + group_by_1
        group_by_2 = "$" + group_by_2
        group_by_aggr = "$" + group_by_aggr
        grouping_pipeline = {
            "$group": {
                "_id": {"__alias_1": group_by_1, "__alias_2": group_by_2},
                "__alias_0": {"$avg": group_by_aggr},
            }
        }
        aggregate_pipeline.append(grouping_pipeline)

        ### Project and sort results ###
        aggregate_pipeline.append(DEFAULT_AGGR_PROJECT)
        aggregate_pipeline.append(DEFAULT_AGGR_SORT)

        results = defaultdict(list)
        # results = []
        mongo = MongodbConnector.get_mongo_client(db_config)
        db_name = db_config["db_name"]
        db_col = db_config["db_collection"]
        x = mongo[db_name][db_col].aggregate(aggregate_pipeline)
        for r in x:
            results[r["color"]].append((r["x"], r["y"]))
            # results.append(r)
        return results, aggregate_pipeline

    @staticmethod
    def get_objects_aggregate_pipeline(db_config, pipeline):
        results = []
        mongo = MongodbConnector.get_mongo_client(db_config)
        db_name = db_config["db_name"]
        db_col = db_config["db_collection"]
        x = mongo[db_name][db_col].aggregate(pipeline)
        for r in x:
            results.append(r)
        print("--- Results ---")
        pprint.pprint(results)
        print(f"--- END ({len(results)}) ---")

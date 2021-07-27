#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021, Intel Corporation

from collections import defaultdict
from pymongo import MongoClient

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
        "P999": {
            "$convert": {
                "input": "$results.Percentile P99_900000 [micros/op]",
                "to": "double",
                "onError": "null",
            }
        },
        "P9999": {
            "$convert": {
                "input": "$results.Percentile P99_990000 [micros/op]",
                "to": "double",
                "onError": "null",
            }
        },
        "Date": {
            "$convert": {"input": "$results.Date", "to": "date", "onError": "null"}
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
# Sort for convenience of usage in plots' creating process
DEFAULT_AGGR_SORT = {"$sort": {"color": 1, "x": 1}}


class MongodbConnector:
    """
    MongoDB connector class
    """

    @staticmethod
    def get_mongo_client(config):
        """
        Create MongoDB client
        @param config: DB connection info
        @type config: dict
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
    def parse_std_results(results, expected_res_count):
        """
        Parse resulted list of documents (returned from other function) into dict.
        It creates list of tuples (x, y) based on 'x', 'y' fields in all documents
        and stores it under key 'color' (based on document's field 'color').
        If documents don't have any of required fields they are not suitable
        for representing on chart - None is returned.
        @param results: documents, returned from MongoDB
        @type results: list
        @param expected_res_count: number of expected results - series of parsed data; number of keys
        @type expected_res_count: int
        @return: parsed data as dict in form of { 'color': list of { 'x', 'y'} } or None
        @rtype: dict
        """
        parsed_data = defaultdict(list)

        # If results should be parsed (for charts) they have to be
        # in the form of list with objects: {'color', 'x', 'y'}
        try:
            for obj in results:
                color = obj["color"]
                x = obj["x"]
                y = obj["y"]
                parsed_data[color].append((x, y))
        except KeyError as e:
            print(
                f"\nResults are not suitable for charts. They don't contain field: {e}"
            )
            return None

        if expected_res_count and not expected_res_count == len(parsed_data):
            print(
                f"WARNING: expected {expected_res_count} documents, got: {len(parsed_data)}!"
            )
        return parsed_data

    @staticmethod
    def get_std_aggr_pipeline(db_config, aggregation_params, get_raw_docs=False):
        """
        Get standard list of data objects from MongoDB's aggregate pipeline.
        It is predefined for retrieving specific pmemkv performance data.
        To get raw documents (before aggregation and projection) 'get_raw_docs'
        can be set, to run this query short and gather full documents - it's useful for debugging.
        @param db_config: Config with DB and collection info
        @type db_config: dict
        @param aggregation_params: Params to setup the pipeline for specific chart
        @type aggregation_params: dict
        @param get_raw_docs: If True, instead of running aggregated query it returns raw documents
        @type get_raw_docs: bool
        @return: list of objects imported from MongoDB AND generated pipeline used to query data (as a list of pipeline stages)
        @rtype: tuple(list, list)
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
        pipeline = [{"$unwind": "$results"}]
        # Define new fields (especially with data conversions, from strings)
        pipeline.append(DEFAULT_AGGR_ADD_FIELDS)

        ### Match (filter) results ###
        # required filters
        match_pipeline = {
            "$match": {
                "engine": {"$in": engines},
                "results.Benchmark": {"$in": benchmark},
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
            emon = ["1", 1, "True"] if emon_enabled else ["0", 0, "False"]
            match_pipeline["$match"].update({"runtime_parameters.emon": {"$in": emon}})
        if not nums == None:
            match_pipeline["$match"].update({"num": {"$in": nums}})
        if not threads == None:
            match_pipeline["$match"].update({"threads": {"$in": threads}})
        if not benchmarks_sets == None:
            match_pipeline["$match"].update(
                {"runtime_parameters.params.--benchmarks": {"$in": benchmarks_sets}}
            )

        pipeline.append(match_pipeline)

        # If we want to get raw documents for current query/chart,
        # we stop here before grouping/aggregation.
        if get_raw_docs:
            results = MongodbConnector.get_aggregate_objects(db_config, pipeline)
            return results, pipeline

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
        pipeline.append(grouping_pipeline)

        ### Project and sort results ###
        pipeline.append(DEFAULT_AGGR_PROJECT)
        pipeline.append(DEFAULT_AGGR_SORT)

        results = MongodbConnector.get_aggregate_objects(db_config, pipeline)
        return results, pipeline

    @staticmethod
    def get_aggregate_objects(db_config, pipeline):
        """
        Get list of documents from MongoDB's aggregate pipeline.
        @param db_config: Config with DB and collection info
        @type db_config: dict
        @param pipeline: list of pipeline stages, delivered as dicts
        @type pipeline: list
        @return: List of objects imported from MongoDB
        @rtype: List
        """
        objects = []
        mongo = MongodbConnector.get_mongo_client(db_config)
        db_name = db_config["db_name"]
        db_col = db_config["db_collection"]
        res = mongo[db_name][db_col].aggregate(pipeline)
        for r in res:
            objects.append(r)
        return objects

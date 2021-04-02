#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021, Intel Corporation

from mongodbConnector import MongodbConnector
from plotly.subplots import make_subplots
import argparse
import json
import os
import plotly.graph_objects as go
import pprint
import random

#
# TODO:
# 	- use logging (as in run_benchmark.py)
# 	- parse pipeline from file (to get rid of known issues)
# 	- add option to print documents (on which chart is based)
#

BAR_CHART_WIDTH = 1000
BAR_CHART_MARGIN_LEFT = 50
BAR_CHART_MARGIN_RIGHT = 50
BAR_CHART_MARGIN_TOP = 50
BAR_CHART_MARGIN_BOTTOM = 75

OUT_DIR = "./generated"
IMAGE_EXT = "png"


def rgb2hex(r, g, b):
    """
    @return: RGB color in HEX format
    @rtype: str
    """
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def random_color(engine):
    """
    @param engine: Engine name
    @type engine: str
    @return: random color based on the engine name (in hex)
    @rtype: str
    """
    random.seed(engine)
    color = rgb2hex(
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
    )
    return color


class Charts:
    """
    pmemkv performance charts
    """

    @staticmethod
    def bar_color(value_name):
        """
        Each bar (in most cases an engine) should have one color across all charts.
        If value name is not defined it should have random color assigned.
        @param engine: value name
        @type engine: str
        @return: color for selected value (an engine name, in most cases)
        @rtype: str
        """
        # Setup colors for 'engine' and 'value_size' values
        colors = {
            "cmap": "#16CC62",
            "csmap": "#196EE6",
            "robinhood": "#E6B219",
            "radix": "#E6196E",
            "dram_vcmap": "#E56EA9",
            "stree": "#19C3E6",
            "8": "#E6B010",
            "128": "#196DE0",
            "1024": "#16CB50",
        }
        if not value_name in colors:
            colors[value_name] = random_color(value_name)
        return colors[value_name]

    @staticmethod
    def generate_bar_chart(
        chart_data,
        chart_title,
        file_path,
        y_title,
        x_title,
        legend_title,
        width_data=BAR_CHART_WIDTH,
    ):
        """
        XXX
        Generate image with representation of data in form of a bar chart
        @param chart_title: Title of the chart
        @type chart_title: str
        @param chart_data: Data to create image for
        @type chart_data: dict
        @param width_data: Pixels of the image width
        @type width_data: int
        @param y_title: Title for y axis
        @type y_title: str
        @param x_title: Title for x axis
        @type x_title: str
        @param legend_title: Title of the legend
        @type legend_title: str
        """
        figure = make_subplots(rows=1, cols=1)
        x_data = None
        for bar, data in chart_data.items():
            x_data = [x[0] for x in data]
            y_data = [y[1] for y in data]
            figure.add_trace(
                go.Bar(x=x_data, y=y_data, name=bar, marker_color=Charts.bar_color(bar))
            )
        # update the look
        figure.update_layout(
            title={"text": chart_title, "x": 0.5},  # center
            legend_title=legend_title,
            xaxis={"title": x_title, "tickvals": x_data, "type": "category"},
            yaxis={"title": y_title, "tickformat": ","},  # separate thousands
            width=width_data,
        )
        figure.layout.margin.update(
            {
                "t": BAR_CHART_MARGIN_TOP,
                "b": BAR_CHART_MARGIN_BOTTOM,
                "l": BAR_CHART_MARGIN_LEFT,
                "r": BAR_CHART_MARGIN_RIGHT,
            }
        )

        image_name = f"{file_path}.{IMAGE_EXT}"
        figure.write_image(image_name)
        print(f"File written: {image_name}")

    @staticmethod
    def generate_standard_charts(db_config, save_pipelines=False):
        """
        Generate standard set of charts, defined for performance report.
        """
        # default params for all aggregations
        aggregation_params = {
            "value_sizes": [8],
            "key_sizes": [8],
            "date_from": "2021-04-01 00:00:00",
            "group_by_1": "threads",
            "group_by_2": "engine",
            "group_by_aggr": "ops/sec",
            "emon_enabled": True,
            "nums": [10000000],
        }

        def generate_chart(expected_res_count=None):
            """
            Helper function to generate charts for specified set of params.
            It has inner scope, so all variables are easily accessed.
            It verifies if expected count of results equals to produced data sets.
            """
            print(f"Processing chart: {chart_title}")
            aggr_res, pipeline = MongodbConnector.get_objects_aggregate(
                db_config, aggregation_params
            )

            # print("DEBUG results results DEBUG !!!")
            # pprint.pprint(aggr_res)
            # print("DEBUG END results results END! Results: " + str(len(aggr_res)))

            Charts.generate_bar_chart(
                aggr_res, chart_title, file_path, y_axis, x_axis, legend
            )
            if save_pipelines:
                with open(f"{file_path}.json", "w") as outfile:
                    json.dump(pipeline, outfile, indent=4)

            if expected_res_count and not expected_res_count == len(aggr_res):
                print(
                    f"WARNING: expected {expected_res_count} documents, got: {len(aggr_res)}!"
                )

        ## standard MT benchmarks with dram_vcmap ##
        aggregation_params["engines"] = ["csmap", "cmap", "dram_vcmap"]
        for bench in ["fillrandom", "fillseq", "readrandom", "readseq"]:
            aggregation_params["benchmark"] = bench
            y_axis = "ops/sec"
            x_axis = "Threads"
            legend = "Engines"
            chart_title = f"{y_axis} 8b {bench} (with dram_vcmap)"
            file_path = f"{OUT_DIR}/mt_dram_{bench}"

            generate_chart(3)

        ## all MT benchmarks ##
        aggregation_params["engines"] = ["csmap", "cmap", "robinhood"]
        for bench in [
            "fillrandom",
            "fillseq",
            "readrandom",
            "readseq",
            "readrandomwriterandom",
            "readwhilewriting",
        ]:
            aggregation_params["benchmark"] = bench
            y_axis = "ops/sec"
            x_axis = "Threads"
            legend = "Engines"
            chart_title = f"{y_axis} 8b {bench} MT engines"
            file_path = f"{OUT_DIR}/mt_{bench}"

            generate_chart(3)

        ## all benchmarks - ST results ##
        aggregation_params["engines"] = ["csmap", "cmap", "robinhood", "stree", "radix"]
        aggregation_params["threads"] = [1]
        aggregation_params["value_sizes"] = [8, 128, 1024]
        aggregation_params["group_by_1"] = "value_size"
        for bench in ["fillrandom", "fillseq", "readrandom", "readseq"]:
            aggregation_params["benchmark"] = bench
            y_axis = "ops/sec"
            x_axis = "Value sizes"
            legend = "Engines"
            # XXX what key size?
            chart_title = f"Xb {bench} single thread, value_size vs {y_axis}"
            file_path = f"{OUT_DIR}/st_{bench}"

            generate_chart(5)

        ## cmap with various value_sizes ##
        aggregation_params["engines"] = ["cmap"]
        aggregation_params["value_sizes"] = [8, 128, 1024]
        # aggregation_params["key_sizes"] = [8, 16]
        aggregation_params["group_by_2"] = "threads"
        aggregation_params["group_by_2"] = "value_size"
        aggregation_params["date_from"] = "2021-03-09 00:00:00"
        aggregation_params["emon_enabled"] = None
        aggregation_params["threads"] = None
        for bench in ["fillrandom", "fillseq", "readrandom", "readseq"]:
            aggregation_params["benchmark"] = bench
            y_axis = "ops/sec"
            x_axis = "Threads"
            legend = "Value size [bytes]"
            chart_title = f"{bench} 16b keys, value_size vs {y_axis}"
            file_path = f"{OUT_DIR}/cmap_{bench}"

            # XXX missing data in DB
            generate_chart(3)


if __name__ == "__main__":
    help_msg = """
	Connects to MongoDB's selected collection and retrives performance data
	to create charts. By defaults it produces standard set of charts,
	based on predefined parameters, with apropriate titles and data.

	Parameter "-s" allows to save generated pipelines (along with charts)
	for examination and potentially introducing some tweaks/changes.

	Parameter "-i" can re-use such pipeline and gather data and prepare custom chart.
	Using this option means, no standard set of charts are produced.

	Environment variables for MongoDB client configuration:
	MONGO_ADDRESS, MONGO_PORT, MONGO_USER, MONGO_PASSWORD, MONGO_DB_NAME and MONGO_DB_COLLECTION
	"""

    # Parse arguments
    parser = argparse.ArgumentParser(
        description=help_msg, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-s",
        "--save-pipeline",
        help="Saves generated pipeline(s) next to charts, before executing query",
        action="store_true",
    )
    parser.add_argument(
        "-i", "--input-pipeline", help="Path to a file with pipeline to run"
    )
    args = parser.parse_args()

    # Collect database info from env
    db_config = dict()
    db_config["db_name"] = os.environ.get("MONGO_DB_NAME", "pmemkv-performance")
    db_config["db_collection"] = os.environ.get(
        "MONGO_DB_COLLECTION", "performance_data"
    )
    try:
        db_config["address"] = os.environ["MONGO_ADDRESS"]
        db_config["port"] = os.environ["MONGO_PORT"]
        db_config["user"] = os.environ["MONGO_USER"]
        db_config["password"] = os.environ["MONGO_PASSWORD"]
    except KeyError as e:
        print(
            f"Environment variable {e} was not specified, so results cannot be accessed from the database"
        )
        exit(1)

    # Create output directory
    OUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), OUT_DIR)
    try:
        print("Output dir: " + OUT_DIR)
        os.mkdir(OUT_DIR)
    except FileExistsError:
        pass

    if args.input_pipeline:
        # read pipeline from a file and create basic chart
        pp = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), args.input_pipeline
        )
        with open(pp, "r") as pf:
            pipeline = json.loads(pf.read())
            pprint.pprint(pipeline)
            MongodbConnector.get_objects_aggregate_pipeline(db_config, pipeline)
            # XXX create chart
    else:
        # Generate standard charts
        Charts.generate_standard_charts(db_config, args.save_pipeline)

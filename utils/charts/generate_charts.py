#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021, Intel Corporation

from datetime import datetime
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
#   - use logging (as in run_benchmark.py)
#   - parse pipeline from file to get rid of known issues (see CAVEATS)
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


def random_color(value):
    """
    @param value: Value name
    @type value: str
    @return: random color (in hex) based on the value name
    @rtype: str
    """
    random.seed(value)
    color = rgb2hex(
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
    )
    return color


def print_results(results, file_path=None):
    """
    Prints documents returned from MongoDB to stdout or to a file (if path given)
    @param results: Data results (documents)
    @type results: list
    @param file_path: Path to a file, in which save the results
    @type file_path: str
    """
    if file_path:
        with open(file_path, "w") as outfile:
            pprint.pprint(results, outfile)
        print(f"--- Documents saved in: {file_path}")
        print(f"--- Documents count: {len(results)}")
    else:
        print("--- Returned results ---")
        pprint.pprint(results)
        print(f"--- Results end (count: {len(results)}) ---")


class Charts:
    """
    pmemkv performance charts
    """

    @staticmethod
    def bar_color(value_name):
        """
        Each bar (in most cases an engine) should have one color across all charts.
        If value name is not defined it should have random color assigned.
        @param value_name: value name (an engine name, in most cases)
        @type value_name: str
        @return: color for selected value
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
            8: "#E6B010",
            128: "#196DE0",
            1024: "#16CB50",
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
        Generate bar chart for data, delivered as dict with objects defined
        as { 'color', 'x', 'y' }, where color is a value of a bar.
        @param chart_data: Data to create image for
        @type chart_data: dict
        @param chart_title: Title of the chart
        @type chart_title: str
        @param file_path: File path, to save chart on disk
        @type file_path: str
        @param y_title: Title for y axis
        @type y_title: str
        @param x_title: Title for x axis
        @type x_title: str
        @param legend_title: Title of the legend
        @type legend_title: str
        @param width_data: Pixels of the image width
        @type width_data: int
        """
        # create chart figure, parse data per value (most likely per engine)
        # and add it as a separate trace (a set of bars)
        figure = make_subplots(rows=1, cols=1)
        x_data = None  # save input data to use as x values
        for bar, data in chart_data.items():
            x_data = [d[0] for d in data]
            y_data = [d[1] for d in data]
            figure.add_trace(
                go.Bar(x=x_data, y=y_data, name=bar, marker_color=Charts.bar_color(bar))
            )

        # update the look
        figure.update_layout(
            title={"text": chart_title, "x": 0.5},  # center
            legend_title=legend_title,
            showlegend=True,
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

        # prepare image and save on disk
        image_name = f"{file_path}.{IMAGE_EXT}"
        figure.write_image(image_name)
        print(f"File written: {image_name}")

    @staticmethod
    def generate_standard_charts(
        db_config, date_from, save_pipelines=False, print_raw_docs=False
    ):
        """
        Generate standard set of charts, defined for performance report.
        @param db_config: DB info, in specific db name and collection, used for retrieving data
        @type db_config: dict
        @param date_from: Sets the date_from value, to query only selected results
        @type date_from: str
        @param save_pipelines: If True stores the pipeline used for aggregation
        @type save_pipelines: bool
        @param print_raw_docs: If True it stores raw documents, before aggregating results
        @type print_raw_docs: bool
        """
        # default params for all aggregations
        aggregation_params = {
            "value_sizes": [8],
            "key_sizes": [8],
            "date_from": date_from,
            "group_by_1": "threads",
            "group_by_2": "engine",
            "group_by_aggr": "ops/sec",
            "emon_enabled": False,
            "nums": [10000000],
        }

        def generate_chart(expected_res_count=None):
            """
            Helper function to generate charts for specified set of params.
            It has inner scope, so all variables are easily accessed.
            It verifies if expected count of results equals to produced data sets.
            """
            print(f"\n### Processing chart: {chart_title} ###")
            if print_raw_docs:
                raw_res, _ = MongodbConnector.get_std_aggr_pipeline(
                    db_config, aggregation_params, get_raw_docs=True
                )
                print_results(raw_res, f"{file_path}_raw_docs.json")

            aggr_res, pipeline = MongodbConnector.get_std_aggr_pipeline(
                db_config, aggregation_params
            )

            aggr_res = MongodbConnector.parse_std_results(aggr_res, expected_res_count)

            Charts.generate_bar_chart(
                aggr_res, chart_title, file_path, y_axis, x_axis, legend
            )
            if save_pipelines:
                with open(f"{file_path}.json", "w") as outfile:
                    json.dump(pipeline, outfile, indent=4)

        ## standard MT benchmarks ##
        aggregation_params["engines"] = ["csmap", "cmap"]
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
            file_path = f"{OUT_DIR}/MT_8_10Mil-{bench}"

            generate_chart(2)

        ## standard MT benchmarks with robinhood ##
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
            chart_title = f"{y_axis} 8b {bench} MT engines (w/ robinhood)"
            file_path = f"{OUT_DIR}/MT_8_robinhood_10Mil-{bench}"

            generate_chart(3)

        ## standard MT benchmarks with dram_vcmap ##
        aggregation_params["engines"] = ["csmap", "cmap", "dram_vcmap"]
        for bench in ["fillrandom", "fillseq", "readrandom", "readseq"]:
            for nums_str, nums in [("10Mil", [10000000])]:  # , ("1Mil", [1000000])
                aggregation_params["benchmark"] = bench
                aggregation_params["nums"] = nums
                y_axis = "ops/sec"
                x_axis = "Threads"
                legend = "Engines"
                chart_title = f"{y_axis} 8b {bench} (w/ dram_vcmap)"
                file_path = f"{OUT_DIR}/MT_8_dram_{nums_str}-{bench}"

                generate_chart(3)

        # XXX added as a separate chart, with custom date_from, due to lack of new data
        ## dram_vcmap - 1Mil entries ##
        aggregation_params["engines"] = ["dram_vcmap"]
        for bench in ["fillrandom", "fillseq"]:  # XXX
            for nums_str, nums in [("1Mil", [1000000])]:
                aggregation_params["benchmark"] = bench
                aggregation_params["nums"] = nums
                aggregation_params["date_from"] = "2021-03-09"  # XXX
                aggregation_params["emon_enabled"] = None  # XXX
                y_axis = "ops/sec"
                x_axis = "Threads"
                legend = "Engines"
                chart_title = f"{y_axis} 8b {bench} (w/ dram_vcmap)"
                file_path = f"{OUT_DIR}/MT_8_dram_{nums_str}-{bench}"

                generate_chart(1)  # XXX

        ## all benchmarks - ST results - value sizes ##
        aggregation_params = {
            "engines": ["csmap", "cmap", "robinhood", "radix", "stree"],
            "threads": [1],
            "value_sizes": [8, 128, 1024],
            "key_sizes": [8],
            "date_from": date_from,
            "group_by_1": "value_size",
            "group_by_2": "engine",
            "group_by_aggr": "ops/sec",
            "emon_enabled": False,
            "nums": [10000000],
        }
        for bench in ["fillrandom", "fillseq", "readrandom", "readseq"]:
            aggregation_params["benchmark"] = bench
            y_axis = "ops/sec"
            x_axis = "Value sizes"
            legend = "Engines"
            chart_title = f"8b {bench} single thread, value_size vs {y_axis}"
            file_path = f"{OUT_DIR}/ST_8_10Mil_values-{bench}"

            generate_chart(5)

        ## standard MT benchmarks - latency (P99.9) ##
        aggregation_params = {
            "engines": ["csmap", "cmap"],
            "value_sizes": [8],
            "key_sizes": [8],
            "date_from": date_from,
            "group_by_1": "threads",
            "group_by_2": "engine",
            "group_by_aggr": "P999",
            "emon_enabled": False,
            "nums": [10000000],
        }
        for bench in ["fillrandom", "fillseq", "readrandom", "readseq"]:
            aggregation_params["benchmark"] = bench
            y_axis = "Latency P99.9 [us] (lower is better)"
            x_axis = "Threads"
            legend = "Engines"
            chart_title = f"{y_axis} 8b {bench} MT engines"
            file_path = f"{OUT_DIR}/lat_P999_8_10Mil-{bench}"

            generate_chart(2)

        ## standard MT benchmarks with robinhood - latency (P99.9) ##
        aggregation_params = {
            "engines": ["csmap", "cmap", "robinhood"],
            "value_sizes": [8],
            "key_sizes": [8],
            "date_from": date_from,
            "group_by_1": "threads",
            "group_by_2": "engine",
            "group_by_aggr": "P999",
            "emon_enabled": False,
            "nums": [10000000],
        }
        for bench in ["fillrandom", "fillseq", "readrandom", "readseq"]:
            aggregation_params["benchmark"] = bench
            y_axis = "Latency P99.9 [us] (lower is better)"
            x_axis = "Threads"
            legend = "Engines"
            chart_title = f"{y_axis} 8b {bench} MT engines (w/ robinhood)"
            file_path = f"{OUT_DIR}/lat_P999_8_robinhood_10Mil-{bench}"

            generate_chart(3)

        ## single engine with various value_sizes ##
        aggregation_params = {
            "value_sizes": [8, 128, 1024],
            "key_sizes": [8],
            "date_from": date_from,
            "group_by_1": "threads",
            "group_by_2": "value_size",
            "group_by_aggr": "ops/sec",
            "emon_enabled": False,
            "nums": [10000000],
        }
        for bench in ["fillrandom", "fillseq", "readrandom", "readseq"]:
            for engine in ["cmap", "csmap", "stree", "radix"]:
                aggregation_params["engines"] = [engine]
                aggregation_params["benchmark"] = bench
                y_axis = "ops/sec"
                x_axis = "Threads"
                legend = "Value size [bytes]"
                chart_title = (
                    f"{engine} engine, {bench} 8b keys, value_size vs {y_axis}"
                )
                file_path = f"{OUT_DIR}/engine_{engine}_8_10Mil_values-{bench}"

                generate_chart(3)


if __name__ == "__main__":
    help_msg = """
	Connects to MongoDB's selected collection and retrieves performance data
	to create charts. By default it produces standard set of charts,
	based on predefined parameters, with appropriate titles and data.

	Parameter "-d" allows to specify 'date-from' used in the queries for
	generating standard set of charts. By default today's date is used.

	Parameter "-s" allows to save generated pipelines (along with charts)
	for examination and potentially introducing some tweaks/changes.

	Parameter "-r" allows to save raw documents for examination
	(along with charts) before aggregating/grouping the results.

	---
	Parameter "-i" can re-use such saved pipeline and gather data and prepare custom chart.
	Using this option means: no standard set of charts are produced and
	results are printed to stdout.
	CAVEATS: If pipelines from other sources are used (e.g. from Mongo Charts),
	then all literals (e.g. null or true) has to be changed to strings
	and e.g. functions like "mean" has to be changed to "avg".

	---
	Environment variables for MongoDB client configuration:
	MONGO_ADDRESS, MONGO_PORT, MONGO_USER, MONGO_PASSWORD, MONGO_DB_NAME and MONGO_DB_COLLECTION
	"""

    # Parse arguments
    parser = argparse.ArgumentParser(
        description=help_msg, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-d",
        "--date-from",
        help="""Date-from to be used in query, to retrieve specific results.
        At best in format "YYYY-MM-DD [hh:mm:ss]". By default today's date will be used.""",
        default=datetime.now().strftime("%Y-%m-%d"),
    )
    parser.add_argument(
        "-s",
        "--save-pipeline",
        help="Saves generated pipelines next to charts, before executing query.",
        action="store_true",
    )
    parser.add_argument(
        "-r",
        "--raw-docs",
        help="Saves raw documents (for generated pipelines) before grouping/aggregating results.",
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

    if args.input_pipeline:
        # read pipeline from a file and create basic chart
        pp = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), args.input_pipeline
        )
        pipeline = None
        with open(pp, "r") as pf:
            pipeline = json.loads(pf.read())

        print(f"\nInput file: {pp}\nRead pipeline:")
        pprint.pprint(pipeline)

        results = MongodbConnector.get_aggregate_objects(db_config, pipeline)

        # print (to stdout) results returned by the pipeline
        print_results(results)

        # and try to parse it for chart creation
        aggr_res = MongodbConnector.parse_std_results(results, None)
        if aggr_res:
            Charts.generate_bar_chart(
                aggr_res, "Custom chart", f"{OUT_DIR}/custom", "", "", ""
            )
    else:
        # Create output directory (including sub-dir for 'date_from')
        OUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), OUT_DIR)
        OUT_DIR = os.path.join(OUT_DIR, args.date_from)
        OUT_DIR = os.path.normpath(OUT_DIR)
        try:
            print("Output dir: " + OUT_DIR)
            os.makedirs(OUT_DIR)
        except FileExistsError:
            pass

        # Generate standard charts
        Charts.generate_standard_charts(
            db_config, args.date_from, args.save_pipeline, args.raw_docs
        )

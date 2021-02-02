# SPDX-License-Identifier: Apache-2.0
# Copyright 2016-2021, Intel Corporation

#
# Dockerfile for lightweight Docker-based Continuous Integration process of pmemkv-bench.
# This image is based on pmemkv build docker image, to simplify process of tracking pmemkv dependencies.

FROM ghcr.io/pmem/pmemkv:ubuntu-20.10-latest
MAINTAINER igor.chorazewicz@intel.com

USER root

RUN apt update && \
	DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends \
	clang-format-10 \
	python3-pymongo \
	python3-pytest \
	python3-pip \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 install black

COPY . /pmemkv-bench

ENTRYPOINT ["/pmemkv-bench/entrypoint.sh"]

# SPDX-License-Identifier: Apache-2.0
# Copyright 2016-2021, Intel Corporation

FROM ghcr.io/pmem/pmemkv:ubuntu-20.10-latest
MAINTAINER igor.chorazewicz@intel.com

USER root

RUN apt update && \
	DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends \
	clang-format-10 \
	python3-pymongo \
 && rm -rf /var/lib/apt/lists/*

COPY . /pmemkv-bench

ENTRYPOINT ["/pmemkv-bench/entrypoint.sh"]

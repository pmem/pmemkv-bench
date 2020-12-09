# SPDX-License-Identifier: Apache-2.0
# Copyright 2016-2020, Intel Corporation

FROM ubuntu:20.04
MAINTAINER szymon.romik@intel.com

RUN apt update && \
	DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends \
	libpmemkv-dev \
	make \
	g++ \
	pkg-config \
 && rm -rf /var/lib/apt/lists/*

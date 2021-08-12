#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2021, Intel Corporation

import os, sys
import pytest
import time

tests_path = os.path.dirname(os.path.realpath(__file__))
project_path = os.path.dirname(tests_path)
sys.path.append(project_path)
import run_benchmark as rb


def test_emon():
    """This test is intedned to be run only in the environment with
    installed emon
    """
    emon = rb.Emon()
    emon.start()
    time.sleep(10)
    emon.stop()
    assert emon._emon_process.poll() is not None
    assert emon.get_data() is not None

import os, sys
import pytest
import json
import tempfile

project_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(project_path)
import run_benchmark as rb


def test_help():
    sys.argv = ["dummy.py", "-h"]
    with pytest.raises(SystemExit) as e:
        result = rb.main()
    assert e.type == SystemExit
    assert e.value.code == 0


def test_json():
    test_configuration = {
        "db_bench": {
            "repo_url": f"{project_path}",
            "commit": "HEAD",
            "env": {"PMEM_IS_PMEM_FORCE": "1"},
            "params": [
                f"--db={os.getenv('TEST_PATH', '/dev/shm')}",
                "--db_size_in_gb=1",
                "--num=100",
            ],
        },
        "pmemkv": {
            "repo_url": "https://github.com/pmem/pmemkv.git",
            "commit": "HEAD",
            "cmake_params": [
                "-DCMAKE_BUILD_TYPE=Release",
                "-DENGINE_RADIX=1",
                "-DBUILD_JSON_CONFIG=1",
                "-DCXX_STANDARD=20",
                "-DBUILD_TESTS=OFF",
                "-DBUILD_DOC=OFF",
                "-DBUILD_EXAMPLES=OFF",
            ],
            "env": {"CC": "gcc", "CXX": "g++"},
        },
        "libpmemobjcpp": {
            "repo_url": "https://github.com/pmem/libpmemobj-cpp.git",
            "commit": "HEAD",
            "cmake_params": [
                "-DBUILD_EXAMPLES=OFF",
                "-DBUILD_TESTS=OFF",
                "-DBUILD_DOC=OFF",
                "-DBUILD_BENCHMARKS=OFF",
                "-DCMAKE_BUILD_TYPE=Release",
            ],
            "env": {"CC": "gcc", "CXX": "g++"},
        },
    }
    tf = tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False)
    json.dump(test_configuration, tf)
    print(tf.name)
    sys.argv = ["dummy.py", tf.name]
    tf.close()
    try:
        result = rb.main()
    except Exception as e:
        assert False, f"run-bench raised exception: {e}"

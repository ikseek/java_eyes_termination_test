import sys
from pathlib import Path
from subprocess import Popen, PIPE
from time import sleep

import psutil
import pytest

platform2dir = {
    "win32": "win",
    "linux": "linux",
    "darwin": "mac"
}
BINARIES_DIR = Path(__file__).parent / "bindings"

TEST_VARIANTS = [
    # Java
    {"type": "java", "os": "win", "binary": BINARIES_DIR / "java" / "single-server-sdk.jar"},
    {"type": "java", "os": "mac", "binary": BINARIES_DIR / "java" / "single-server-sdk.jar"},
    {"type": "java", "os": "linux", "binary": BINARIES_DIR / "java" / "single-server-sdk.jar"},
    # Other SDK's
]

PLATFORM_SPECIFIC_VARIANT = [v for v in TEST_VARIANTS if v['os'] == platform2dir[sys.platform]]


def show_type(variant):
    return variant['type']


@pytest.mark.parametrize("variant", PLATFORM_SPECIFIC_VARIANT, ids=show_type)
@pytest.mark.parametrize("reason", ["normal"])
def test_automatic_eyes_universal_termination_on_python_termination(reason,variant):
    binding_process = Popen([variant['binary']], stdin=PIPE, stdout=PIPE)
    output_line = binding_process.stdout.readline()
    assert output_line.startswith(b"Runner Started")
    (eyes_universal,) = psutil.Process(binding_process.pid).children()
    assert eyes_universal.is_running()
    termination_type = b"1\n" if reason == "normal" else b"2\n"
    binding_process.stdin.write(termination_type)
    binding_process.stdin.flush()
    binding_process.wait()
    sleep(1)  # eyes-universal receives EOF on stdin and terminates, might take time

    assert not eyes_universal.is_running()


@pytest.mark.parametrize("variant", PLATFORM_SPECIFIC_VARIANT,ids=show_type)
@pytest.mark.parametrize("reason", ["normal"])
def test_parallel_eyes_universal_termination_on_python_termination(reason,variant):
    processes = []
    for _ in range(2):
        binding_process = Popen([variant['binary']], stdin=PIPE, stdout=PIPE)
        output_line = binding_process.stdout.readline()
        assert output_line.startswith(b"Runner Started")
        (eyes_universal,) = psutil.Process(binding_process.pid).children()
        assert eyes_universal.is_running()
        processes.append((binding_process, eyes_universal))

    for binding_process, eyes_universal in processes:
        termination_type = b"1\n" if reason == "normal" else b"2\n"
        binding_process.stdin.write(termination_type)
        binding_process.stdin.flush()
        binding_process.wait()
        sleep(1)  # eyes-universal receives EOF on stdin and terminates, might take time
        assert not eyes_universal.is_running()

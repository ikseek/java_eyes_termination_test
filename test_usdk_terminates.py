import sys
from subprocess import Popen, PIPE
from time import sleep

import psutil
import pytest


@pytest.mark.parametrize("reason", ["normal"])
def test_automatic_eyes_universal_termination_on_python_termination(reason):
    java_process = Popen(["java", "-jar", "single-server-sdk.jar"], stdin=PIPE, stdout=PIPE)
    output_line = java_process.stdout.readline()
    assert output_line.startswith(b"Runner Started")
    (eyes_universal,) = psutil.Process(java_process.pid).children()
    assert eyes_universal.is_running()
    termination_type = b"1\n" if reason == "normal" else b"2\n"
    java_process.stdin.write(termination_type)
    java_process.stdin.flush()
    java_process.wait()
    sleep(1)  # eyes-universal receives EOF on stdin and terminates, might take time

    assert not eyes_universal.is_running()


@pytest.mark.parametrize("reason", ["normal"])
def test_parallel_eyes_universal_termination_on_python_termination(reason):
    processes = []
    for _ in range(2):
        java_process = Popen(["java", "-jar", "single-server-sdk.jar"], stdin=PIPE, stdout=PIPE)
        output_line = java_process.stdout.readline()
        assert output_line.startswith(b"Runner Started")
        (eyes_universal,) = psutil.Process(java_process.pid).children()
        assert eyes_universal.is_running()
        processes.append((java_process, eyes_universal))

    for java_process, eyes_universal in processes:
        termination_type = b"1\n" if reason == "normal" else b"2\n"
        java_process.stdin.write(termination_type)
        java_process.stdin.flush()
        java_process.wait()
        sleep(1)  # eyes-universal receives EOF on stdin and terminates, might take time
        assert not eyes_universal.is_running()

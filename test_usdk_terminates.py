import sys
from subprocess import Popen, PIPE
from time import sleep

import psutil
import pytest


@pytest.mark.parametrize("reason", ["normal"])
def test_automatic_eyes_universal_termination_on_python_termination(reason):
    # A simple python program that executes eyes-universal and waits on stdin
    python_process = Popen(["java", "-jar", "single-server-sdk.jar"], stdin=PIPE, stdout=PIPE)
    output_line = python_process.stdout.readline()
    assert output_line.startswith(b"Runner Started")
    (eyes_universal,) = psutil.Process(python_process.pid).children()
    assert eyes_universal.is_running()
    termination_type = b"1\n" if reason == "normal" else b"2\n"
    python_process.stdin.write(termination_type)
    python_process.stdin.flush()
    python_process.wait()
    sleep(1)  # eyes-universal receives EOF on stdin and terminates, might take time

    assert not eyes_universal.is_running()

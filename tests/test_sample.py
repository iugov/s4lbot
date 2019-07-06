from src import sample
import pytest


def test_say_hello():
    assert "hello!" == sample.say_hello()

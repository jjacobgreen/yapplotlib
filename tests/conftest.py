"""
Shared fixtures for yapplotlib tests.
"""

import pytest
import matplotlib
matplotlib.use('Agg')  # headless; must be set before pyplot import

import matplotlib.pyplot as plt


@pytest.fixture
def simple_messages():
    return [
        {'role': 'user',      'content': 'What is 2 + 2?'},
        {'role': 'assistant', 'content': 'It is 4.'},
    ]


@pytest.fixture
def full_messages():
    return [
        {'role': 'system',    'content': 'You are a helpful assistant.'},
        {'role': 'user',      'content': 'What is the capital of France?'},
        {'role': 'assistant', 'content': 'The capital of France is Paris.'},
        {'role': 'user',      'content': 'And Germany?'},
        {'role': 'assistant', 'content': 'The capital of Germany is Berlin.'},
    ]


@pytest.fixture(autouse=True)
def close_figures():
    """Close all figures after each test to avoid resource leaks."""
    yield
    plt.close('all')

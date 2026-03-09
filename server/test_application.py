import pytest

# импортируем наше приложение
from application import TestMe


def test_server():
    '''
    тест метода TestMe
    '''
    assert TestMe().take_five() == 5


def test_port():
    '''
    тест метода TestMe
    '''
    assert TestMe().port() == 8000

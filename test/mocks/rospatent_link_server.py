"""Тесты для test.mocks.

Демонстрационная заглушка: набор тестов проекта составляет внутреннюю
инженерную практику и поставляется отдельно.

Проверяемый модуль: `test.mocks`
"""

import pytest


@pytest.mark.skip(reason="internal test suite not published")
def test_placeholder():
    assert True

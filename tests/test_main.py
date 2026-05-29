"""Тесты для проверки функций фильтрации и сортировки самолетов."""
import sys
sys.path.append(".")
import pytest
from main import filter_aeroplanes, get_aeroplanes_by_altitude, get_top_aeroplanes
from src.api import Aeroplane


@pytest.fixture
def sample_planes():
    """Создает минимальный список настоящих объектов Aeroplane для тестов."""
    return [
        Aeroplane(callsign="UAL1621", origin_country="United States", velocity=250.0, altitude=1000.0),
        Aeroplane(callsign="IBE3120", origin_country="Spain", velocity=210.0, altitude=3000.0),
    ]


def test_filter_aeroplanes(sample_planes):
    """Проверка фильтрации по стране."""
    # Фильтруем по Испании
    filtered = filter_aeroplanes(sample_planes, ["Spain"])
    assert len(filtered) == 1
    assert filtered[0].callsign == "IBE3120"

    # Если фильтр пустой — должен вернуть всё обратно
    assert len(filter_aeroplanes(sample_planes, [])) == 2


def test_get_aeroplanes_by_altitude(sample_planes):
    """Проверка фильтрации по высоте."""
    # Самолет с высотой 1000м попадает в диапазон 500-1500
    filtered = get_aeroplanes_by_altitude(sample_planes, "500-1500")
    assert len(filtered) == 1
    assert filtered[0].callsign == "UAL1621"


def test_get_top_aeroplanes(sample_planes):
    """Проверка получения среза Топ-N."""
    top = get_top_aeroplanes(sample_planes, 1)
    assert len(top) == 1

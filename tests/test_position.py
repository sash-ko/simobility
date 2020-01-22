import pytest
from simobility.core import Position


def test_position():
    p1 = Position(-0.39276123046875, 39.444147324430396)
    p2 = Position(-0.3577423095703125, 39.50404070558415)

    assert pytest.approx(p1.distance(p2), 0.2) == 7.31
    assert p1.distance(p2) == p2.distance(p1)
    assert p1.distance(p1) == 0

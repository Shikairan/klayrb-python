"""Tests for RDB geometry conversion."""

import klayout.db as db

from klayrb.marker.geometry import (
    dbox_to_box,
    dedge_pair_to_shapes,
    um_to_dbu,
)


def test_um_to_dbu():
    assert um_to_dbu(1.0, 0.001) == 1000


def test_dbox_to_box():
    box = db.DBox(0.0, 0.0, 1.0, 2.0)
    out = dbox_to_box(box, 0.001)
    assert out.left == 0
    assert out.right == 1000
    assert out.top == 2000


def test_dedge_pair_produces_two_shapes():
    ep = db.DEdgePair(db.DEdge(0, 0, 1, 0), db.DEdge(0, 1, 1, 1))
    shapes = dedge_pair_to_shapes(ep, 0.001)
    assert len(shapes) == 2
    assert isinstance(shapes[0], db.Edge)

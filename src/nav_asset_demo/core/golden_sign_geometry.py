"""Replaceable normalized geometry templates extracted from approved golden SVGs.

Company-side calibration should replace this module as one self-contained file while
preserving the public function signatures below.
"""

from __future__ import annotations


def straight_arrow_path(x: float, y: float, width: float, height: float) -> str:
    return f"M{x+width*.5},{y} L{x+width},{y+height*.32} L{x+width*.68},{y+height*.32} L{x+width*.68},{y+height} L{x+width*.32},{y+height} L{x+width*.32},{y+height*.32} L{x},{y+height*.32} Z"


def turn_arrow_path(direction: str, x: float, y: float, width: float, height: float) -> str:
    if direction == "left":
        return f"M{x},{y+height*.5} L{x+width*.34},{y} L{x+width*.34},{y+height*.30} L{x+width},{y+height*.30} L{x+width},{y+height*.70} L{x+width*.34},{y+height*.70} L{x+width*.34},{y+height} Z"
    return f"M{x+width},{y+height*.5} L{x+width*.66},{y} L{x+width*.66},{y+height*.30} L{x},{y+height*.30} L{x},{y+height*.70} L{x+width*.66},{y+height*.70} L{x+width*.66},{y+height} Z"


def diagonal_arrow_path(direction: str, x: float, y: float, width: float, height: float) -> str:
    if direction == "diagonal_left":
        return f"M{x},{y} L{x+width*.62},{y+height*.08} L{x+width*.45},{y+height*.26} L{x+width},{y+height*.82} L{x+width*.78},{y+height} L{x+width*.23},{y+height*.44} L{x+width*.06},{y+height*.61} Z"
    return f"M{x+width},{y} L{x+width*.38},{y+height*.08} L{x+width*.55},{y+height*.26} L{x},{y+height*.82} L{x+width*.22},{y+height} L{x+width*.77},{y+height*.44} L{x+width*.94},{y+height*.61} Z"


def national_route_shield_path(x: float, y: float, width: float, height: float) -> str:
    # PROVISIONAL: Replace with the exact normalized golden-sample Bezier path.
    return f"M{x+width*.5},{y} C{x+width*.75},{y} {x+width},{y+height*.25} {x+width*.91},{y+height*.52} C{x+width*.82},{y+height*.80} {x+width*.68},{y+height} {x+width*.5},{y+height} C{x+width*.32},{y+height} {x+width*.18},{y+height*.80} {x+width*.09},{y+height*.52} C{x},{y+height*.25} {x+width*.25},{y} {x+width*.5},{y} Z"


def prefectural_route_shield_path(x: float, y: float, width: float, height: float) -> str:
    # PROVISIONAL: Replace with the exact normalized golden-sample path.
    return f"M{x+width*.25},{y} L{x+width*.75},{y} L{x+width},{y+height*.5} L{x+width*.75},{y+height} L{x+width*.25},{y+height} L{x},{y+height*.5} Z"


def shield_knockout_path(
    shield_type: str,
    x: float,
    y: float,
    width: float,
    height: float,
    clearance: float,
) -> str:
    x -= clearance
    y -= clearance
    width += clearance * 2
    height += clearance * 2
    if shield_type == "national_route":
        return national_route_shield_path(x, y, width, height)
    if shield_type == "prefectural_route":
        return prefectural_route_shield_path(x, y, width, height)
    return f"M{x},{y} H{x+width} V{y+height} H{x} Z"

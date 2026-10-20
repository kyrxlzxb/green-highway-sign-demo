"""Small, provider-neutral blue-sign reconstruction tools for the visual demo."""

from __future__ import annotations

import html
import json
import math
from dataclasses import dataclass
from typing import Annotated, Any, Literal

import cv2
import numpy as np
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from nav_asset_demo.core import golden_sign_geometry as golden_geometry


CommonColor = Literal["white", "black", "blue", "yellow", "orange", "red", "green", "gray", "unknown"]


class Point(BaseModel):
    model_config = ConfigDict(extra="forbid")
    x: float
    y: float


class SignDetection(BaseModel):
    model_config = ConfigDict(extra="forbid")
    corners: list[Point] = Field(min_length=4, max_length=4)
    confidence: float = Field(ge=0, le=1)
    readable_text: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @field_validator("readable_text", mode="before")
    @classmethod
    def accept_single_text_summary(cls, value: Any) -> Any:
        if isinstance(value, str):
            return [value]
        return value


class Box(BaseModel):
    model_config = ConfigDict(extra="forbid")
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(gt=0, le=1)
    height: float = Field(gt=0, le=1)

    @model_validator(mode="after")
    def within_canvas(self) -> "Box":
        if self.x + self.width > 1.0001 or self.y + self.height > 1.0001:
            raise ValueError("Box exceeds the normalized canvas")
        return self


class TextElement(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    type: Literal["text"]
    text: str
    bbox: Box
    language: Literal["ja", "latin", "number", "unknown"] = "unknown"
    confidence: float = Field(ge=0, le=1)
    color: CommonColor = "white"

    @field_validator("language", mode="before")
    @classmethod
    def normalize_language_alias(cls, value: Any) -> Any:
        if isinstance(value, str):
            return {"en": "latin", "english": "latin", "jp": "ja", "japanese": "ja"}.get(value.lower(), value)
        return value


class ArrowElement(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    type: Literal["arrow"]
    direction: Literal["straight", "left", "right", "diagonal_left", "diagonal_right"]
    bbox: Box
    confidence: float = Field(ge=0, le=1)
    occluded_by: list[str] = Field(default_factory=list)
    color: CommonColor = "white"

    @field_validator("direction", mode="before")
    @classmethod
    def normalize_direction_alias(cls, value: Any) -> Any:
        if isinstance(value, str):
            return {"up": "straight", "forward": "straight"}.get(value.lower(), value)
        return value

    @field_validator("occluded_by", mode="before")
    @classmethod
    def accept_single_occluder(cls, value: Any) -> Any:
        if isinstance(value, str):
            return [value]
        return value


class ShieldElement(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    type: Literal["route_shield"]
    shield_type: Literal["national_route", "prefectural_route", "expressway", "unknown"]
    route_number: str
    bbox: Box
    confidence: float = Field(ge=0, le=1)
    fill_color: CommonColor = "blue"
    border_color: CommonColor = "white"
    text_color: CommonColor = "white"

    @field_validator("shield_type", mode="before")
    @classmethod
    def normalize_shield_alias(cls, value: Any) -> Any:
        if isinstance(value, str):
            return {
                "hexagon": "prefectural_route",
                "prefectural": "prefectural_route",
                "national": "national_route",
                "onigiri": "national_route",
                "rounded_triangle": "national_route",
            }.get(value.lower(), value)
        return value


class PhysicalArtifact(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["replacement_patch", "fading", "stain", "glare", "damage", "unknown"]
    bbox: Box | None = None
    note: str = ""
    confidence: float | None = Field(default=None, ge=0, le=1)

    @field_validator("type", mode="before")
    @classmethod
    def normalize_unrecognized_artifact_type(cls, value: Any) -> Any:
        allowed = {"replacement_patch", "fading", "stain", "glare", "damage", "unknown"}
        if isinstance(value, str):
            normalized = value.lower()
            return normalized if normalized in allowed else "unknown"
        return value


class PanelElement(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    type: Literal["panel"]
    bbox: Box
    confidence: float = Field(ge=0, le=1)
    fill_color: CommonColor = "yellow"
    border_color: CommonColor = "unknown"


Element = Annotated[TextElement | ArrowElement | ShieldElement | PanelElement, Field(discriminator="type")]


class SignLayout(BaseModel):
    model_config = ConfigDict(extra="forbid")
    elements: list[Element] = Field(default_factory=list)
    physical_artifacts: list[PhysicalArtifact] = Field(default_factory=list)
    background_color: str = "#1676b8"
    foreground_color: str = "#ffffff"
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_ids_and_references(self) -> "SignLayout":
        ids = [element.id for element in self.elements]
        if len(ids) != len(set(ids)):
            raise ValueError("Element IDs must be unique")
        shield_ids = {element.id for element in self.elements if isinstance(element, ShieldElement)}
        for element in self.elements:
            if isinstance(element, ArrowElement):
                unknown = [shield_id for shield_id in element.occluded_by if shield_id not in shield_ids]
                if unknown:
                    # Model references are untrusted. Drop dangling references instead
                    # of guessing a replacement shield, and preserve a visible warning.
                    element.occluded_by = [shield_id for shield_id in element.occluded_by if shield_id in shield_ids]
                    self.warnings.append(
                        f"Arrow {element.id} referenced unknown shield IDs: {', '.join(unknown)}"
                    )
        return self


@dataclass(frozen=True)
class QuickRenderResult:
    sign_svg: str
    highlight_svgs: dict[str, str]


def rectify_from_detection(
    image_bgr: np.ndarray,
    detection: SignDetection,
    *,
    boundary_padding_ratio: float = 0.0,
) -> np.ndarray:
    if not 0 <= boundary_padding_ratio <= 0.20:
        raise ValueError("Boundary padding ratio must be between 0 and 0.20")
    points = np.asarray([[point.x, point.y] for point in detection.corners], dtype=np.float32)
    if not np.isfinite(points).all():
        raise ValueError("Detection contains non-finite coordinates")
    height, width = image_bgr.shape[:2]
    if np.any(points[:, 0] < 0) or np.any(points[:, 0] >= width) or np.any(points[:, 1] < 0) or np.any(points[:, 1] >= height):
        raise ValueError("Detected corners exceed the source image")
    sums = points.sum(axis=1)
    differences = np.diff(points, axis=1).reshape(-1)
    source = np.asarray([
        points[np.argmin(sums)], points[np.argmin(differences)],
        points[np.argmax(sums)], points[np.argmax(differences)],
    ], dtype=np.float32)
    if boundary_padding_ratio:
        center = source.mean(axis=0)
        source = center + (source - center) * (1 + boundary_padding_ratio * 2)
        source[:, 0] = np.clip(source[:, 0], 0, width - 1)
        source[:, 1] = np.clip(source[:, 1], 0, height - 1)
    tl, tr, br, bl = source
    target_width = max(2, round(max(np.linalg.norm(tr - tl), np.linalg.norm(br - bl))))
    target_height = max(2, round(max(np.linalg.norm(bl - tl), np.linalg.norm(br - tr))))
    target = np.asarray([[0, 0], [target_width - 1, 0], [target_width - 1, target_height - 1], [0, target_height - 1]], dtype=np.float32)
    matrix = cv2.getPerspectiveTransform(source, target)
    return cv2.warpPerspective(image_bgr, matrix, (target_width, target_height))


def _pixel_box(box: Box, width: int, height: int) -> tuple[float, float, float, float]:
    return box.x * width, box.y * height, box.width * width, box.height * height


def _arrow_path(element: ArrowElement, width: int, height: int) -> str:
    x, y, w, h = _pixel_box(element.bbox, width, height)
    if element.direction == "straight":
        return golden_geometry.straight_arrow_path(x, y, w, h)
    if element.direction in {"left", "right"}:
        return golden_geometry.turn_arrow_path(element.direction, x, y, w, h)
    return golden_geometry.diagonal_arrow_path(element.direction, x, y, w, h)


def _shield_shape(element: ShieldElement, width: int, height: int, *, expand: float = 0) -> str:
    # CALIBRATION POINT: These are intentionally provisional silhouettes.
    # Replace national-route and prefectural-route paths with normalized golden
    # sample geometry while preserving this scaling and positioning interface.
    x, y, w, h = _pixel_box(element.bbox, width, height)
    x -= expand
    y -= expand
    w += expand * 2
    h += expand * 2
    if element.shield_type == "prefectural_route":
        return golden_geometry.prefectural_route_shield_path(x, y, w, h)
    if element.shield_type == "national_route":
        return golden_geometry.national_route_shield_path(x, y, w, h)
    return f"M{x},{y} H{x+w} V{y+h} H{x} Z"


def render_quick_svg(
    layout: SignLayout,
    *,
    width: int,
    height: int,
    font_family: str = "Noto Sans JP",
    palette: dict[str, str] | None = None,
    text_scale: float = 1.0,
) -> QuickRenderResult:
    if not 0.5 <= text_scale <= 1.5:
        raise ValueError("Text scale must be between 0.5 and 1.5")
    # CALIBRATION POINT: Set approved production HEX values through this palette.
    colors = {"white": "#ffffff", "black": "#000000", "blue": "#1676b8", "yellow": "#ffd400", "orange": "#f59e0b", "red": "#d71920", "green": "#17823b", "gray": "#808080", "unknown": "#ffffff"}
    colors.update(palette or {})
    background = html.escape(colors.get("blue", layout.background_color), quote=True)
    foreground = html.escape(colors.get("white", layout.foreground_color), quote=True)
    definitions: list[str] = []
    body: list[str] = [f'<rect id="sign-background" width="{width}" height="{height}" fill="{background}"/>']
    shields = {element.id: element for element in layout.elements if isinstance(element, ShieldElement)}
    for element in layout.elements:
        element_id = html.escape(element.id, quote=True)
        if isinstance(element, TextElement):
            x, y, w, h = _pixel_box(element.bbox, width, height)
            # CALIBRATION POINT: The model supplies a tight visual bbox. Fit live
            # SVG text to that box; later replace this with approved font metrics.
            size = max(8, h * .92 * text_scale)
            target_text_width = max(1, w * .98 * text_scale)
            body.append(
                f'<g id="{element_id}" data-type="text"><text x="{x+w/2:.2f}" y="{y+h*.88:.2f}" '
                f'text-anchor="middle" font-family="{html.escape(font_family, quote=True)}" font-size="{size:.2f}" '
                f'textLength="{target_text_width:.2f}" lengthAdjust="spacingAndGlyphs" '
                f'fill="{html.escape(colors[element.color], quote=True)}">{html.escape(element.text)}</text></g>'
            )
        elif isinstance(element, ArrowElement):
            path = _arrow_path(element, width, height)
            mask_id = f"mask-{element_id}"
            holes = "".join(f'<path d="{_shield_shape(shields[shield_id], width, height, expand=max(width, height)*.012)}" fill="black"/>' for shield_id in element.occluded_by)
            if holes:
                definitions.append(f'<mask id="{mask_id}"><rect width="100%" height="100%" fill="white"/>{holes}</mask>')
            mask = f' mask="url(#{mask_id})"' if holes else ""
            body.append(f'<g id="{element_id}" data-type="arrow"{mask}><path d="{path}" fill="{html.escape(colors[element.color], quote=True)}"/></g>')
        elif isinstance(element, ShieldElement):
            path = _shield_shape(element, width, height)
            x, y, w, h = _pixel_box(element.bbox, width, height)
            # CALIBRATION POINT: Shield border width and route-number typography
            # must use the approved golden values after geometry extraction.
            body.append(
                f'<g id="{element_id}" data-type="route-shield"><path d="{path}" fill="{html.escape(colors[element.fill_color], quote=True)}" stroke="{html.escape(colors[element.border_color], quote=True)}" stroke-width="{max(2, min(width,height)*.008):.2f}"/>'
                f'<text x="{x+w/2:.2f}" y="{y+h*.68:.2f}" text-anchor="middle" font-family="{html.escape(font_family, quote=True)}" '
                f'font-size="{h*.42:.2f}" font-weight="bold" fill="{html.escape(colors[element.text_color], quote=True)}">{html.escape(element.route_number)}</text></g>'
            )
        elif isinstance(element, PanelElement):
            x, y, w, h = _pixel_box(element.bbox, width, height)
            body.append(f'<g id="{element_id}" data-type="panel"><rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{html.escape(colors[element.fill_color], quote=True)}" stroke="{html.escape(colors[element.border_color], quote=True)}"/></g>')
    defs = f"<defs>{''.join(definitions)}</defs>" if definitions else ""
    sign_svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">{defs}{"".join(body)}</svg>'
    highlights: dict[str, str] = {}
    for element in layout.elements:
        if not isinstance(element, ArrowElement):
            continue
        path = _arrow_path(element, width, height)
        holes = "".join(f'<path d="{_shield_shape(shields[shield_id], width, height, expand=max(width, height)*.012)}" fill="black"/>' for shield_id in element.occluded_by)
        defs = f'<defs><mask id="route-cutout"><rect width="100%" height="100%" fill="white"/>{holes}</mask></defs>' if holes else ""
        mask = ' mask="url(#route-cutout)"' if holes else ""
        highlights[element.id] = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">{defs}'
            f'<g id="highlight-{html.escape(element.id, quote=True)}"{mask}><path d="{path}" fill="{html.escape(colors["orange"], quote=True)}"/></g></svg>'
        )
    return QuickRenderResult(sign_svg=sign_svg, highlight_svgs=highlights)


def example_layout_json() -> str:
    example: dict[str, Any] = {
        "background_color": "#1676b8", "foreground_color": "#ffffff",
        "elements": [
            {"id": "text-hikone", "type": "text", "text": "Hikone", "language": "latin", "bbox": {"x": .12, "y": .08, "width": .28, "height": .13}, "confidence": .98},
            {"id": "arrow-straight", "type": "arrow", "direction": "straight", "bbox": {"x": .42, "y": .28, "width": .16, "height": .66}, "confidence": .96, "occluded_by": ["route-307"]},
            {"id": "route-307", "type": "route_shield", "shield_type": "national_route", "route_number": "307", "bbox": {"x": .43, "y": .43, "width": .14, "height": .20}, "confidence": .99}
        ],
        "physical_artifacts": [], "warnings": []
    }
    return json.dumps(example, ensure_ascii=False, indent=2)

"""Green-panel prototype: measured contours and constrained SVG geometry.

This experimental model is separate from the sealed-run production contracts.
All boxes use normalized coordinates on an already rectified, tightly cropped PNG.
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass
from typing import Literal

import cv2
import numpy as np
from PIL import ImageFont
from pydantic import BaseModel, ConfigDict, Field, model_validator

from nav_asset_demo.core.quick_blue_sign import Box


class GreenElement(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_-]*$", max_length=80)
    kind: Literal["text", "arrow", "panel", "shield", "icon"]
    bbox: Box
    color: Literal["green", "white", "blue"] = "white"
    text: str = Field(default="", max_length=300)
    # Only approved library identifiers may be resolved, never model-supplied URLs.
    icon_id: str = Field(default="", pattern=r"^[a-z0-9_-]*$")
    direction: str = Field(default="", max_length=80)
    points: list[tuple[float, float]] = Field(default_factory=list, max_length=2000)
    font_scale: float = Field(default=1, ge=.5, le=2)
    tracking: float = Field(default=0, ge=-10, le=30)

    @model_validator(mode="after")
    def valid_geometry(self):
        if any(not np.isfinite([x, y]).all() or not (0 <= x <= 1 and 0 <= y <= 1)
               for x, y in self.points):
            raise ValueError("Contour coordinates must be finite normalized points")
        if self.points and len(self.points) < 3:
            raise ValueError("A contour requires at least three points")
        return self


class Footer(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    top: float = Field(ge=.05, le=.95)
    white_width: float = Field(gt=0, lt=1)
    line_height: float = Field(default=.008, gt=0, le=.05)

    @model_validator(mode="after")
    def within_panel(self):
        if self.top + self.line_height >= 1:
            raise ValueError("Divider extends beyond panel")
        return self


class GreenLayout(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    corner_radius: float = Field(default=0, ge=0, le=.15)
    footer: Footer | None = None
    elements: list[GreenElement] = Field(default_factory=list, max_length=100)
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_ids(self):
        ids = [e.id for e in self.elements]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate element IDs")
        return self


def decode_image(data: bytes) -> np.ndarray:
    image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Cannot decode input image")
    if max(image.shape[:2]) > 4096:
        scale = 4096 / max(image.shape[:2])
        image = cv2.resize(image, None, fx=scale, fy=scale)
    return image


def color_mask(image: np.ndarray, color: str) -> np.ndarray:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    limits = {
        "white": ((0, 0, 140), (179, 85, 255)),
        "green": ((32, 65, 35), (93, 255, 255)),
        "blue": ((94, 65, 35), (140, 255, 255)),
    }
    lo, hi = limits[color]
    return cv2.inRange(hsv, np.array(lo), np.array(hi))


def pixel_box(box: Box, w: int, h: int):
    return (max(0, int(box.x*w)), max(0, int(box.y*h)),
            min(w, int(np.ceil((box.x+box.width)*w))),
            min(h, int(np.ceil((box.y+box.height)*h))))


def measure_layout(image: np.ndarray, layout: GreenLayout):
    """Refine coarse semantic ROIs; never invent a missing arrow."""
    result = layout.model_copy(deep=True)
    h, w = image.shape[:2]
    diagnostics = []
    for e in result.elements:
        if e.kind not in {"text", "arrow", "shield"}:
            continue
        if e.kind != "text":
            # A failed measurement must not fall back to unverified model geometry.
            e.points = []
        x0, y0, x1, y1 = pixel_box(e.bbox, w, h)
        mask = color_mask(image[y0:y1, x0:x1], e.color)
        count, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
        components = [i for i in range(1, count) if stats[i, cv2.CC_STAT_AREA] >= max(3, mask.size*.00008)]
        if not components:
            result.warnings.append(f"{e.id}: no foreground found; review ROI")
            continue
        if e.kind == "text":
            # Preserve all characters; ignore isolated compression specks.
            selected = np.isin(labels, components).astype(np.uint8)*255
            xx, yy, ww, hh = cv2.boundingRect(selected)
            e.bbox = Box(x=(x0+xx)/w, y=(y0+yy)/h, width=ww/w, height=hh/h)
        else:
            components.sort(key=lambda i: stats[i, cv2.CC_STAT_AREA], reverse=True)
            selected = (labels == components[0]).astype(np.uint8)*255
            contours, _ = cv2.findContours(selected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(contour) < 3:
                result.warnings.append(f"{e.id}: foreground too small for a usable contour")
                continue
            # Pixel-scale simplification preserves turns instead of replacing direction.
            poly = cv2.approxPolyDP(contour, max(.75, min(w, h)*.001), True)
            xx, yy, ww, hh = cv2.boundingRect(contour)
            if xx == 0 or yy == 0 or xx+ww == mask.shape[1] or yy+hh == mask.shape[0]:
                result.warnings.append(f"{e.id}: contour touches ROI; enlarge search box and remeasure")
            if len(components) > 1 and stats[components[1], cv2.CC_STAT_AREA] > stats[components[0], cv2.CC_STAT_AREA]*.15:
                result.warnings.append(f"{e.id}: multiple substantial components; review selection")
            e.points = [((float(p[0][0])-xx)/max(1, ww-1), (float(p[0][1])-yy)/max(1, hh-1)) for p in poly]
            e.bbox = Box(x=(x0+xx)/w, y=(y0+yy)/h, width=(ww-1)/w, height=(hh-1)/h)
            reconstructed = np.zeros_like(selected)
            cv2.fillPoly(reconstructed, [poly], 255)
            # Compare the outer silhouette, excluding interior text holes in shields.
            silhouette = np.zeros_like(selected)
            cv2.drawContours(silhouette, [contour], -1, 255, cv2.FILLED)
            union = np.count_nonzero(silhouette | reconstructed)
            diagnostics.append({"id": e.id, "vertices": len(poly),
                                "contour_iou": round(np.count_nonzero(silhouette & reconstructed)/max(1, union), 5),
                                "note": "Local contour fidelity, NOT semantic direction accuracy"})
    return result, diagnostics


def rounded_path(w: float, h: float, r: float) -> str:
    return f"M{r},0 H{w-r} Q{w},0 {w},{r} V{h-r} Q{w},{h} {w-r},{h} H{r} Q0,{h} 0,{h-r} V{r} Q0,0 {r},0 Z"


def footer_path(w: float, h: float, radius: float, footer: Footer) -> str:
    y, split = footer.top*h, footer.white_width*w
    line_bottom = min(h, y+footer.line_height*h)
    # ONE connected path. Horizontal divider and white block cannot separate.
    r = min(radius, split, h-line_bottom)
    return f"M0,{y} H{w} V{line_bottom} H{split} V{h} H{r} Q0,{h} 0,{h-r} Z"


@dataclass
class GreenRender:
    svg: str
    warnings: list[str]


def render_green(layout: GreenLayout, width: int, height: int, *,
                 font_family: str = "Meiryo", font_path: str | None = None,
                 font_weight: Literal["normal", "bold"] = "bold",
                 palette: dict | None = None, icon_library: dict | None = None) -> GreenRender:
    colors = {"green": "#087738", "white": "#ffffff", "blue": "#1769aa"}
    colors.update(palette or {})
    if any(not re.fullmatch(r"#[0-9a-fA-F]{6}", c) for c in colors.values()):
        raise ValueError("Palette entries must be six-digit HEX colors")
    warnings = list(layout.warnings)
    w, h = width, height
    r = layout.corner_radius*min(w, h)
    background_path = rounded_path(w,h,r)
    if layout.footer:
        split, y = layout.footer.white_width*w, layout.footer.top*h
        # Do not paint green under the white rounded corner: antialiasing two
        # identical overlapping curves can otherwise leave a green fringe.
        background_path = (f"M{r},0 H{w-r} Q{w},0 {w},{r} V{h-r} Q{w},{h} {w-r},{h} "
                           f"H{split} V{y} H0 V{r} Q0,0 {r},0 Z")
    body = [f'<path id="sign-background" d="{background_path}" fill="{colors["green"]}"/>']
    if layout.footer:
        body.append(f'<path id="footer-white" d="{footer_path(w,h,r,layout.footer)}" fill="{colors["white"]}"/>')
    font = ImageFont.truetype(font_path, 1000) if font_path else None
    if not font:
        warnings.append("Font metrics unavailable: approximate text height; select a local font file for fitting")
    for e in layout.elements:
        x, y, ew, eh = e.bbox.x*w, e.bbox.y*h, e.bbox.width*w, e.bbox.height*h
        attrs = f'id="el-{e.id}" fill="{colors[e.color]}"'
        if e.kind == "text":
            if not e.text:
                continue
            if font:
                left, top, right, bottom = font.getbbox(e.text, anchor="ls")
                size = eh*1000/max(1, bottom-top)*e.font_scale
                baseline = y-top*size/1000
            else:
                size, baseline = eh*1.15*e.font_scale, y+eh
            body.append(f'<text {attrs} x="{x+ew/2}" y="{baseline}" text-anchor="middle" '
                        f'font-family="{html.escape(font_family, quote=True)}" font-size="{size}" '
                        f'font-weight="{font_weight}" '
                        f'letter-spacing="{e.tracking}" textLength="{ew}" lengthAdjust="spacingAndGlyphs">'
                        f'{html.escape(e.text)}</text>')
        elif e.kind == "panel":
            body.append(f'<path {attrs} d="M{x},{y} h{ew} v{eh} h{-ew} Z"/>')
        elif e.kind in {"arrow", "shield"}:
            if not e.points:
                warnings.append(f"{e.id}: missing measured contour; omitted, not guessed")
                continue
            d = "M"+" L".join(f"{x+px*ew:.3f},{y+py*eh:.3f}" for px, py in e.points)+" Z"
            stroke = f' stroke="{colors["white"]}" stroke-width="{min(w,h)*.006}" stroke-linejoin="round"' if e.kind == "shield" else ""
            body.append(f'<path {attrs} d="{d}"{stroke}/>')
        elif e.kind == "icon":
            # Local approved JSON catalog: {id: {viewBox: [x,y,w,h], paths: [d,...]}}.
            asset = (icon_library or {}).get(e.icon_id)
            if not asset:
                warnings.append(f"{e.id}: new_icon_required ({e.icon_id}); no substitute inserted")
                continue
            vx, vy, vw, vh = map(float, asset["viewBox"])
            if min(vw, vh) <= 0 or not np.isfinite([vx,vy,vw,vh]).all():
                raise ValueError("Invalid approved icon viewBox")
            scale = min(ew/vw, eh/vh)
            paths = "".join(f'<path d="{html.escape(d, quote=True)}"/>' for d in asset["paths"])
            body.append(f'<g {attrs} transform="translate({x+(ew-vw*scale)/2},{y+(eh-vh*scale)/2}) scale({scale}) translate({-vx},{-vy})">{paths}</g>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{"".join(body)}</svg>'
    return GreenRender(svg, warnings)

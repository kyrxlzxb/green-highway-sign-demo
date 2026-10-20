"""Public facade for the explicitly scoped green-sign prototype."""
import json
from pathlib import Path

import cv2

from nav_asset_demo.core.quick_green_sign import GreenLayout, decode_image, measure_layout, render_green
from nav_asset_demo.core.openai_compatible_vision import VisionSignAnalyzer


class QuickGreenSignPipeline:
    def prepare(self, image_bytes: bytes, document: dict, *, refine: bool = True):
        image = decode_image(image_bytes)
        layout = GreenLayout.model_validate(document)
        diagnostics = []
        if refine:
            layout, diagnostics = measure_layout(image, layout)
        return layout.model_dump(), diagnostics

    def analyze(self, image_bytes: bytes, analyzer: VisionSignAnalyzer, prompt: str):
        # One explicitly requested invocation. Disable SDK automatic retries.
        analyzer.client = analyzer.client.with_options(max_retries=0, timeout=90)
        document = analyzer._call("green_layout", prompt, image_bytes, "image/png", 6000)
        return self.prepare(image_bytes, document)

    def render(self, image_bytes: bytes, document: dict, **options):
        image = decode_image(image_bytes)
        return render_green(GreenLayout.model_validate(document), image.shape[1], image.shape[0], **options)

    def overlay(self, image_bytes: bytes, document: dict) -> bytes:
        image = decode_image(image_bytes)
        h, w = image.shape[:2]
        for e in GreenLayout.model_validate(document).elements:
            b = e.bbox
            cv2.rectangle(image, (int(b.x*w), int(b.y*h)), (int((b.x+b.width)*w), int((b.y+b.height)*h)), (0,0,255), 2)
            cv2.putText(image, e.id, (int(b.x*w), max(14,int(b.y*h))), cv2.FONT_HERSHEY_SIMPLEX, .45, (0,0,255), 1)
        return cv2.imencode(".png", image)[1].tobytes()

    def export_sample(self, image_bytes: bytes, document: dict, destination: Path, **options):
        destination.mkdir(parents=True, exist_ok=False)
        layout, diagnostics = self.prepare(image_bytes, document)
        rendered = self.render(image_bytes, layout, **options)
        (destination/"sign.svg").write_text(rendered.svg, encoding="utf-8")
        (destination/"layout.json").write_text(json.dumps(layout, ensure_ascii=False, indent=2), encoding="utf-8")
        (destination/"report.json").write_text(json.dumps({"diagnostics":diagnostics,"warnings":rendered.warnings}, indent=2), encoding="utf-8")
        (destination/"boxes.png").write_bytes(self.overlay(image_bytes, layout))
        return rendered

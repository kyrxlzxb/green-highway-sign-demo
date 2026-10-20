"""OpenAI-compatible vision client for Bedrock, Azure, or OpenAI endpoints."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI

from nav_asset_demo.core.inference import normalize_json_candidate
from nav_asset_demo.core.quick_blue_sign import SignDetection, SignLayout


@dataclass(frozen=True)
class VisionApiConfig:
    base_url: str
    api_key: str
    model: str

    def __post_init__(self) -> None:
        if not self.base_url or not self.api_key or not self.model:
            raise ValueError("Vision API base URL, API key, and model are required")


@dataclass(frozen=True)
class VisionCallTrace:
    stage: str
    prompt: str
    raw_response_text: str
    parsed_response: dict


class VisionSignAnalyzer:
    def __init__(self, config: VisionApiConfig, *, detection_prompt: str, layout_prompt: str) -> None:
        self.config = config
        self.client = OpenAI(base_url=config.base_url.rstrip("/") + "/", api_key=config.api_key)
        self.detection_prompt = detection_prompt
        self.layout_prompt = layout_prompt
        self.traces: list[VisionCallTrace] = []

    @staticmethod
    def _data_url(image_bytes: bytes, media_type: str) -> str:
        return f"data:{media_type};base64,{base64.b64encode(image_bytes).decode('ascii')}"

    def _call(self, stage: str, prompt: str, image_bytes: bytes, media_type: str, max_tokens: int) -> dict:
        if "api.openai.com" in self.config.base_url.lower():
            response = self.client.responses.create(
                model=self.config.model,
                max_output_tokens=max_tokens,
                input=[{
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": self._data_url(image_bytes, media_type)},
                    ],
                }],
            )
            raw_text = response.output_text or ""
            parsed = normalize_json_candidate(raw_text).document
            self.traces.append(VisionCallTrace(stage, prompt, raw_text, parsed))
            return parsed
        response = self.client.chat.completions.create(
            model=self.config.model,
            temperature=0,
            max_tokens=max_tokens,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": self._data_url(image_bytes, media_type)}},
                ],
            }],
        )
        text = response.choices[0].message.content or ""
        parsed = normalize_json_candidate(text).document
        self.traces.append(VisionCallTrace(stage, prompt, text, parsed))
        return parsed

    def detect(self, image_bytes: bytes, media_type: str, width: int, height: int) -> SignDetection:
        # Replace only the documented image-size tokens. Using str.format here
        # would incorrectly treat JSON examples such as {"x": 10} as fields.
        prompt = self.detection_prompt.replace("{width}", str(width)).replace("{height}", str(height))
        return SignDetection.model_validate(self._call("sign_detection", prompt, image_bytes, media_type, 900))

    def analyze_layout(self, image_bytes: bytes, media_type: str) -> SignLayout:
        return SignLayout.model_validate(self._call("layout_analysis", self.layout_prompt, image_bytes, media_type, 4000))

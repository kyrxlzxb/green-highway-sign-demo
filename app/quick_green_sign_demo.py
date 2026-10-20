"""Small green-sign workbench; processing stays in the public facade."""
import base64
import hashlib
import json
import os
from pathlib import Path

import streamlit as st

from nav_asset_demo.core.openai_compatible_vision import VisionApiConfig, VisionSignAnalyzer
from nav_asset_demo.pipelines.quick_green_sign import QuickGreenSignPipeline

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "data/local/green_sign"
pipeline = QuickGreenSignPipeline()
st.set_page_config(page_title="Green Sign Demo", layout="wide")
st.title("Green Sign Demo")
st.caption("Clean PNG → semantic boxes → measured paths + editable text. Local edits make no API calls.")
mode = st.radio("Input", ["Saved development samples", "Upload clean panel PNG"], horizontal=True)
data, seed = None, None
if mode == "Saved development samples":
    samples = sorted(SAMPLES.glob("*.layout.json"))
    if samples:
        selected = st.selectbox("Development sample", samples, format_func=lambda p: p.name.replace(".layout.json", ""))
        path = selected.with_name(selected.name.replace(".layout.json", ".png"))
        if path.exists():
            data = path.read_bytes()
            seed = json.loads(selected.read_text(encoding="utf-8"))
            st.info("Sample semantics and rough search boxes were annotated in this session. This is an offline replay, not an API benchmark.")
    else:
        st.info("Prepare the local samples with scripts/try_green_sign.py, or upload a clean PNG.")
else:
    uploaded = st.file_uploader("Tightly cropped, front-facing panel", type=["png"])
    if uploaded:
        data = uploaded.getvalue()
    layout_file = st.file_uploader("Optional layout JSON (skip the API)", type=["json"])
    if layout_file:
        seed = json.loads(layout_file.getvalue())

with st.sidebar:
    st.header("Rendering")
    preview_width = st.slider("Preview width", 320, 1000, 640, 20)
    font_family = st.text_input("Font family", "Meiryo")
    font_path = st.text_input("Local font file for height fitting", "C:/Windows/Fonts/meiryob.ttc")
    font_weight = st.selectbox("Font weight (match metric file)", ["bold", "normal"])
    palette = {name: st.color_picker(name.title(), value) for name, value in
               {"green":"#087738", "white":"#ffffff", "blue":"#1769aa"}.items()}
    catalog_file = st.file_uploader("Approved icon catalog JSON", type=["json"])
    catalog = json.loads(catalog_file.getvalue()) if catalog_file else {}

with st.expander("Optional vision API — one call per click"):
    base_url = st.text_input("API base URL", os.getenv("NAV_ASSET_API_BASE_URL", ""))
    model = st.text_input("Vision model / deployment", os.getenv("NAV_ASSET_VISION_MODEL", ""))
    key = os.getenv("NAV_ASSET_API_KEY", "")
    st.caption("Key comes from NAV_ASSET_API_KEY. No automatic retries. No model call occurs during editing.")
    prompt = st.text_area("Prompt", (ROOT/"prompts/quick_green_sign/layout_v001.md").read_text(encoding="utf-8"), height=240)
    analyze = st.button("Analyze PNG (one API call)", disabled=not(data and base_url and model and key))

if data:
    token = hashlib.sha256(data).hexdigest()
    if st.session_state.get("green_token") != token:
        for name in ("green_doc", "green_report", "green_trace"):
            st.session_state.pop(name, None)
        st.session_state["green_token"] = token
        st.session_state["green_revision"] = st.session_state.get("green_revision", 0)+1
        if seed is not None and mode == "Saved development samples":
            document, diagnostics = pipeline.prepare(data, seed)
            st.session_state["green_doc"] = document
            st.session_state["green_report"] = diagnostics
    refine = st.checkbox("Measure text bounds and trace arrow / shield pixels", True)
    if st.button("Build from sample / JSON", disabled=seed is None) or analyze:
        try:
            if analyze:
                analyzer = VisionSignAnalyzer(VisionApiConfig(base_url, key, model), detection_prompt="", layout_prompt=prompt)
                doc, report = pipeline.analyze(data, analyzer, prompt)
                st.session_state["green_trace"] = [vars(t) for t in analyzer.traces]
            else:
                doc, report = pipeline.prepare(data, seed, refine=refine)
            st.session_state["green_doc"], st.session_state["green_report"] = doc, report
            st.session_state["green_revision"] += 1
        except Exception as exc:
            st.error(f"Could not process input ({type(exc).__name__}). Check the image, JSON and endpoint settings.")
    if "green_doc" in st.session_state:
        doc = st.session_state["green_doc"]
        revision = st.session_state["green_revision"]
        with st.expander("Panel geometry", expanded=bool(doc.get("footer"))):
            doc["corner_radius"] = st.slider("Corner radius / short edge", 0., .15, float(doc["corner_radius"]), .001, key=f"radius-{revision}")
            if doc.get("footer"):
                f = doc["footer"]
                f["top"] = st.slider("Divider height position", .05, .94, float(f["top"]), .001, key=f"top-{revision}")
                f["white_width"] = st.slider("Left white block width", .01, .99, float(f["white_width"]), .001, key=f"split-{revision}")
                f["line_height"] = st.slider("Divider thickness", .001, .05, float(f["line_height"]), .001, key=f"line-{revision}")
                st.caption("The divider always spans the panel; the white block stays attached to the left and bottom.")
        with st.expander("Element editor"):
            elements = doc["elements"]
            if elements:
                eid = st.selectbox("Element", [e["id"] for e in elements], key=f"select-{revision}")
                e = next(e for e in elements if e["id"] == eid)
                b = e["bbox"]
                cols = st.columns(4)
                for col, field in zip(cols, ("x", "y", "width", "height")):
                    b[field] = col.number_input(field, min_value=0. if field in ("x","y") else .001,
                        max_value=1., value=float(b[field]), step=.001, format="%.3f", key=f"{revision}-{eid}-{field}")
                if e["kind"] == "text":
                    e["text"] = st.text_input("Text", e["text"], key=f"{revision}-{eid}-text")
                    e["font_scale"] = st.slider("Font height", .5, 2., float(e["font_scale"]), .01, key=f"{revision}-{eid}-scale")
                    e["tracking"] = st.slider("Letter spacing (px)", -10., 30., float(e["tracking"]), .5, key=f"{revision}-{eid}-tracking")
                if e["kind"] == "icon":
                    e["icon_id"] = st.text_input("Approved icon ID", e["icon_id"], key=f"{revision}-{eid}-icon")
        try:
            rendered = pipeline.render(data, doc, font_family=font_family,
                                       font_path=font_path or None, font_weight=font_weight, palette=palette, icon_library=catalog)
            left, right = st.columns(2)
            left.image(data, caption="Generated PNG input", width=preview_width)
            encoded = base64.b64encode(rendered.svg.encode()).decode()
            right.markdown(f'<img alt="Editable SVG preview" style="width:{preview_width}px;max-width:100%" src="data:image/svg+xml;base64,{encoded}">', unsafe_allow_html=True)
            for warning in rendered.warnings:
                st.warning(warning)
            st.download_button("Download editable SVG", rendered.svg, "sign.svg", "image/svg+xml")
            st.download_button("Download layout JSON", json.dumps(doc, ensure_ascii=False, indent=2), "layout.json", "application/json")
            with st.expander("Measured boxes / diagnostics"):
                st.image(pipeline.overlay(data, doc), width=preview_width)
                st.json(st.session_state.get("green_report", []))
            with st.expander("Prompt and response"):
                st.json(st.session_state.get("green_trace", {"mode":"offline annotated sample; zero API calls"}))
        except (ValueError, OSError, KeyError) as exc:
            st.error(f"Cannot render: {exc}")
        with st.expander("Advanced layout JSON"):
            edited = st.text_area("Document", json.dumps(doc, ensure_ascii=False, indent=2), height=350, key=f"json-{revision}")
            if st.button("Apply JSON"):
                try:
                    candidate, _ = pipeline.prepare(data, json.loads(edited), refine=False)
                    st.session_state["green_doc"] = candidate
                    st.session_state["green_revision"] += 1
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))

"""Prepare two explicitly annotated development cases and export measured SVGs.

Usage: python scripts/try_green_sign.py --first generated1.png --second generated2.png
Source annotations were made by the assistant from generated images, not an API.
Image generation is an external preparation step, not silently repeated here.
"""
import argparse
import base64
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from nav_asset_demo.pipelines.quick_green_sign import QuickGreenSignPipeline


def box(x, y, w, h):
    return dict(x=x,y=y,width=w,height=h)


def element(id, kind, bounds, color="white", **extra):
    return dict(id=id,kind=kind,bbox=box(*bounds),color=color,**extra)


def sample_documents():
    return [
        {"corner_radius":0, "footer":None, "elements":[
            element("title-panel","panel",(.299,.063,.442,.308)),
            element("e1a-panel","panel",(.311,.135,.132,.175),"green"),
            element("e1a","text",(.317,.15,.119,.121), text="E1A"),
            element("shin-meishin","text",(.455,.089,.266,.162),"green",text="新 名 神"),
            element("expressway","text",(.45,.278,.281,.07),"green",text="SHIN-MEISHIN EXP"),
            element("arrow","arrow",(.05,.155,.083,.66),direction="up"),
            element("kyoto-ja","text",(.228,.43,.247,.24),text="京 都"),
            element("osaka-ja","text",(.6,.43,.25,.24),text="大 阪"),
            element("kyoto-en","text",(.245,.71,.213,.18),text="Kyoto"),
            element("osaka-en","text",(.61,.71,.226,.15),text="Osaka"),
        ],"warnings":[]},
        {"corner_radius":.075, "footer":{"top":.667,"white_width":.307,"line_height":.013},"elements":[
            element("route-176","shield",(.075,.04,.204,.202),"blue"),
            element("route-text","text",(.105,.075,.145,.105),text="176"),
            element("takarazuka-ja","text",(.07,.25,.395,.22),text="宝 塚"),
            element("amagasaki-ja","text",(.545,.25,.39,.22),text="尼 崎"),
            element("takarazuka-en","text",(.045,.49,.44,.14),text="Takarazuka"),
            element("amagasaki-en","text",(.525,.49,.428,.165),text="Amagasaki"),
            element("exit-number","text",(.095,.705,.13,.224),"green",text="3"),
            element("exit-ja","text",(.335,.70,.212,.13),text="出口"),
            element("exit-en","text",(.342,.845,.199,.096),text="EXIT"),
            element("distance","text",(.56,.73,.396,.18),text="500m"),
        ],"warnings":["Generated PNG has small exterior margins; this case approximates the panel as the full canvas."]}
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--first", type=Path, required=True)
    parser.add_argument("--second", type=Path, required=True)
    parser.add_argument("--font", default="C:/Windows/Fonts/meiryob.ttc")
    args = parser.parse_args()
    samples = ROOT/"data/local/green_sign"
    samples.mkdir(parents=True, exist_ok=True)
    output = ROOT/"runs"/("green-preview-"+datetime.now().strftime("%Y%m%d-%H%M%S"))
    pipeline = QuickGreenSignPipeline()
    sections = []
    for name, source, document in zip(("shin_meishin","takarazuka"),(args.first,args.second),sample_documents()):
        target = samples/f"{name}.png"
        if target.exists() and target.read_bytes() != source.read_bytes():
            raise FileExistsError(f"Refusing to overwrite a different sample: {target}")
        if not target.exists():
            shutil.copy2(source,target)
        (samples/f"{name}.layout.json").write_text(json.dumps(document, ensure_ascii=False, indent=2),encoding="utf-8")
        rendered = pipeline.export_sample(target.read_bytes(),document,output/name,font_path=args.font)
        png = base64.b64encode(target.read_bytes()).decode()
        svg = base64.b64encode(rendered.svg.encode()).decode()
        sections.append(f'<section><h2>{name}</h2><div class="pair"><figure><figcaption>Generated PNG input</figcaption><img src="data:image/png;base64,{png}"></figure>'
                        f'<figure><figcaption>Rebuilt SVG (live text)</figcaption><img src="data:image/svg+xml;base64,{svg}"></figure></div>'
                        f'<details><summary>Overlay comparison</summary><input type="range" min="0" max="100" value="50" '
                        f'oninput="this.nextElementSibling.lastElementChild.style.opacity=this.value/100">'
                        f'<div class="overlay"><img src="data:image/png;base64,{png}"><img style="opacity:.5" src="data:image/svg+xml;base64,{svg}"></div></details></section>')
        print(name, "warnings:", rendered.warnings)
    (output/"index.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>Green sign prototype</title>'
        '<style>body{font:16px Segoe UI;margin:24px;background:#f2f4f5}h1{font-size:24px}.pair{display:flex;gap:20px}'
        'figure{margin:0;flex:1;min-width:0}img{width:100%;display:block}figcaption{padding:8px 0}'
        'section{background:white;padding:18px;margin:20px 0}.overlay{position:relative;max-width:900px}'
        '.overlay img:last-child{position:absolute;inset:0}details{margin-top:16px}</style>'
        '<h1>Green sign reconstruction — development preview</h1><p>Generated inputs. Assistant-annotated semantic boxes; deterministic contour extraction. No API recognition benchmark.</p>'
        + "".join(sections), encoding="utf-8")
    print("OUTPUT:", output)


if __name__ == "__main__":
    main()

# Green highway sign demo

Small local PNG-to-SVG workbench: live text, measured arrow contours, configurable
three-color palette, and a connected white footer path that stays flush to panel edges.

## Windows setup (Python 3.11 or 3.12)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app/quick_green_sign_demo.py
```

Upload a clean, front-facing, tightly cropped PNG. Supply layout JSON to avoid an
API call, or set NAV_ASSET_API_BASE_URL, NAV_ASSET_API_KEY, NAV_ASSET_VISION_MODEL in
your process environment and click Analyze. `.env.example` documents variable
names; the app does not automatically read `.env` files.

Choose the local font file and matching SVG font family/weight in the sidebar.
Windows Meiryo Bold is the initial preview choice; company fonts are not bundled.
No model ID or service URL is assumed. Each Analyze click makes one request,
with SDK retries disabled. Local editing does not call a model.

Two previously generated development PNGs are intentionally not in this source
package. If you have them, `scripts/try_green_sign.py --first first.png --second
second.png` imports them locally, uses the explicitly annotated sample layouts,
and exports SVG/JSON/overlay/HTML into a new ignored runs directory.
Those annotations are development fixtures, not a general recognizer.

This is a standalone package. Do not replace an existing project's full
pyproject.toml or package initializers with these minimal ones.

## How the conversion works

1. **Start with a clean panel PNG.** The app expects a front-facing, tightly
   cropped sign. Image generation and perspective correction happen outside
   this prototype. The two development PNGs were generated separately.

2. **Describe the elements with JSON.** A vision model supplies text content,
   element types, approximate bounding boxes, icon IDs and panel structure.
   Coordinates are normalized to 0..1 relative to the full image. Pydantic
   checks the schema, box bounds and unique IDs before processing. The supplied
   development cases use assistant-annotated JSON instead of a live API call.
   The editable prompt is `prompts/quick_green_sign/layout_v001.md`.

3. **Measure pixels inside each search box.** OpenCV converts the image to HSV
   and thresholds white, green or blue. Connected-component analysis removes
   tiny specks. For text, the retained components define a tighter bounding box;
   this step measures visible pixels, it does not recognize characters. For an
   arrow or shield, the largest component supplies the external contour.
   `approxPolyDP` simplifies that contour to a polygon, which becomes an SVG
   path. Its orientation and bends come from the pixels, not a direction label.
   These are fixed heuristic color thresholds; dirty or ambiguous inputs can fail.

4. **Construct the panel from constraints.** Background and rectangular insets
   are paths. The footer's horizontal divider and left white block form one
   connected path, controlled by divider position, block width and line
   thickness. The block reaches the left and bottom edges; the divider reaches
   the right edge. Green is not painted underneath the white lower-left corner,
   preventing a green antialiasing fringe. Panel parameters come from the JSON
   or editor; they are not automatically measured by the contour routine.

5. **Typeset editable text.** Pillow reads the selected local font's glyph
   bounds to calculate font size and baseline from the measured text box.
   SVG `textLength` and `lengthAdjust="spacingAndGlyphs"` fit its width.
   The output retains actual `<text>` nodes. The local metric font and SVG
   font family/weight must match; width fitting can stretch glyphs, so this
   is an initial layout fit rather than exact reproduction of the source font.

6. **Resolve approved icons.** An icon ID selects paths from a local JSON
   catalog. The renderer scales them uniformly and centers them within the
   requested box. Missing icons produce a review warning. Shield outlines
   currently use measured contours rather than this catalog.

7. **Preview, inspect and edit locally.** Streamlit regenerates the SVG when
   a control changes. Text, position, size, colors and footer geometry can be
   adjusted without another model call. SVG and layout JSON are downloadable;
   the sample runner also creates box overlays and an HTML comparison.
   Contour IoU compares the simplified polygon with the extracted silhouette.
   It does not verify text, semantic arrow direction or whole-sign accuracy.
   Border-touching contours and competing components generate warnings.

The API path makes one request per Analyze click, with automatic SDK retries
disabled. There is no automatic model-review loop. API recognition on unseen
images has not yet been benchmarked.

### Code map

| File | Responsibility |
| --- | --- |
| `app/quick_green_sign_demo.py` | Uploads, preview, local controls and downloads |
| `src/nav_asset_demo/pipelines/quick_green_sign.py` | Validation/measurement/rendering facade and one-call analysis |
| `src/nav_asset_demo/core/quick_green_sign.py` | Data models, color masks, contours, text metrics and SVG paths |
| `src/nav_asset_demo/core/openai_compatible_vision.py` | Existing vision API transport |
| `prompts/quick_green_sign/layout_v001.md` | Editable recognition instructions and JSON example |
| `scripts/try_green_sign.py` | Replay of the two annotated development cases |

## Geometry

- Arrow search ROIs must contain the complete foreground silhouette. OpenCV
  traces the largest component and simplifies at pixel scale. It does not
  replace the arrow with a direction template.
- Touching ROI edges or competing components produce review warnings.
- Contour IoU measures tracing fidelity only, not semantic correctness.
- Footer is one connected path parameterized by top, split and line thickness.
  Its white block always reaches left and bottom; the divider reaches right.
- Text remains text. Pillow font metrics fit the height; SVG textLength fits
  the width. Font family and selected local metric font must match.
- Green, white and blue are configurable provisional HEX values.
- No raster image is embedded in the SVG.

## Approved icon integration

Export company Illustrator assets as SVG paths first, then create a local JSON
catalog keyed by stable identifiers:

```json
{"parking": {"viewBox": [0, 0, 100, 100], "paths": ["M10,10 H90 V90 H10 Z"]}}
```

The example path is only a schema illustration, not an approved parking icon.
Flatten transforms in Illustrator before extracting path data. This first
catalog supports monochrome path icons; upload it via the sidebar. Missing
IDs yield `new_icon_required`, never a guessed substitute. Route shield outlines
are currently traced from pixels and can later be replaced by catalog geometry.

## Known limits

Inputs must already be tightly cropped and rectified. Photo detection and
generative cleaning are not performed inside the app. General photographs,
occluded/fragmented arrows and complex multi-color icons need further work.
Text refinement assumes clean, isolated ROIs; a neighboring border inside the
ROI can contaminate measurements. The UI shows boxes for inspection.
Changing footer geometry does not automatically reposition its text.
Source-to-generated-image fidelity is separate from PNG-to-SVG fidelity.

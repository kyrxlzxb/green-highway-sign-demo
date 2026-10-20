import xml.etree.ElementTree as ET

import cv2
import numpy as np
import pytest
from pydantic import ValidationError

from nav_asset_demo.core.quick_green_sign import GreenLayout, measure_layout, render_green


@pytest.mark.parametrize("points", [
    [[100,20],[140,75],[115,75],[115,170],[85,170],[85,75],[60,75]],
    [[170,45],[120,15],[120,35],[70,35],[70,170],[95,170],[95,60],[120,60],[120,80]],
])
def test_actual_contours_preserve_four_arrow_orientations(points):
    # Geometry comes from pixels, not the intentionally wrong direction label.
    source = np.zeros((200,200,3),np.uint8)
    source[:] = (40,110,10)
    points = np.array(points)
    cv2.fillPoly(source,[points],(255,255,255))
    for rotation in range(4):
        image = np.rot90(source,rotation).copy()
        layout = GreenLayout.model_validate({"elements":[{"id":"arrow","kind":"arrow","direction":"wrong",
            "bbox":{"x":.05,"y":.05,"width":.9,"height":.9}}]})
        result, diagnostics = measure_layout(image,layout)
        e = result.elements[0]
        reconstructed = np.zeros((200,200),np.uint8)
        contour = np.array([[(e.bbox.x+x*e.bbox.width)*200,(e.bbox.y+y*e.bbox.height)*200] for x,y in e.points]).round().astype(np.int32)
        cv2.fillPoly(reconstructed,[contour],255)
        expected = cv2.inRange(image,(230,230,230),(255,255,255))
        assert np.count_nonzero(expected & reconstructed)/np.count_nonzero(expected | reconstructed) > .98
        assert diagnostics[0]["contour_iou"] > .98


def test_footer_one_path_attached_and_text_escaped():
    layout = GreenLayout.model_validate({"corner_radius":.05,"footer":{"top":.7,"white_width":.3},
        "elements":[{"id":"word","kind":"text","text":"A&B <exit>","bbox":{"x":.1,"y":.2,"width":.5,"height":.1}}]})
    root = ET.fromstring(render_green(layout,1000,700).svg)
    ns = {"s":"http://www.w3.org/2000/svg"}
    paths = root.findall("s:path",ns)
    assert len(paths) == 2
    assert 'H1000' in paths[1].attrib["d"]
    assert 'H300.0 V700' in paths[1].attrib["d"]
    assert root.find("s:text",ns).text == "A&B <exit>"
    layout.footer.white_width = .4
    assert 'H400.0 V700' in render_green(layout,1000,700).svg


def test_missing_arrow_and_icon_are_not_invented():
    layout = GreenLayout.model_validate({"elements":[
        {"id":"arrow","kind":"arrow","bbox":{"x":.1,"y":.1,"width":.1,"height":.3}},
        {"id":"service","kind":"icon","icon_id":"parking","bbox":{"x":.5,"y":.1,"width":.1,"height":.1}}
    ]})
    result = render_green(layout,1000,700)
    assert len(result.warnings) == 3  # font + missing contour + missing icon
    assert 'id="el-arrow"' not in result.svg
    assert "new_icon_required" in result.warnings[-1]


def test_invalid_model_coordinates_rejected():
    with pytest.raises(ValidationError):
        GreenLayout.model_validate({"elements":[{"id":"bad","kind":"arrow",
            "bbox":{"x":.9,"y":.1,"width":.3,"height":.2}}]})


def test_unknown_text_retained_as_text_and_icon_catalog_used():
    layout = GreenLayout.model_validate({"elements":[{"id":"service","kind":"icon","icon_id":"parking",
        "bbox":{"x":.1,"y":.1,"width":.1,"height":.2}}]})
    svg = render_green(layout,100,100,icon_library={"parking":{"viewBox":[0,0,10,10],"paths":["M0,0 H10 V10 H0 Z"]}}).svg
    assert 'id="el-service"' in svg
    assert "<image" not in svg

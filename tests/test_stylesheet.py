from makeweb import CSS
from makeweb.html import Doc, style


def test_css():
    css = CSS()
    css("body", background_color="black", color="green")
    assert str(css) == "body{background-color:black;color:green}"
    css(".main li", __webkit__filter="blur(1px)")
    assert (
        str(css)
        == "body{background-color:black;color:green}\
.main li{--webkit--filter:blur(1px)}"
    )


def test_css_embed():
    css = CSS()
    css("body", background_color="black", color="green")
    doc = Doc()
    with style():
        css.embed()
    assert str(doc) == "<style>body{background-color:black;color:green}</style>"

from makeweb import CSS, defaults
from makeweb.html import Doc, style


def test_css():
    css = CSS()
    css("body", background_color="black", color="green")
    assert str(css) == "body{background-color:black;color:green}"
    css(".main li", _webkit_filter="blur(1px)")
    assert (
        str(css)
        == "body{background-color:black;color:green}\
.main li{-webkit-filter:blur(1px)}"
    )


def test_css_embed():
    css = CSS()
    css("body", background_color="black", color="green")
    doc = Doc()
    with style():
        css.embed()
    assert str(doc) == "<style>body{background-color:black;color:green}</style>"


def test_css_keyframes():
    css = CSS()
    css("@keyframes fadeIn", **{"0%": {"opacity": "0"}, "100%": {"opacity": "1"}})
    assert str(css) == "@keyframes fadeIn{0%{opacity:0};100%{opacity:1}}"


def test_css_media_query():
    css = CSS()
    css(
        "@media screen and (max-width: 600px)",
        **{"body": {"font-size": "14px"}, ".header": {"padding": "10px"}},
    )
    assert (
        str(css)
        == "@media screen and (max-width: 600px){body{font-size:14px};.header{padding:10px}}"
    )


def test_combined_css_rules():
    css = CSS()
    css("body", color="white")
    css("@media (max-width: 600px)", **{"body": {"color": "black"}})
    assert str(css) == "body{color:white}@media (max-width: 600px){body{color:black}}"


def test_css_media_query_with_string_value():
    css = CSS()
    css("@media print", body="display: none")
    assert str(css) == "@media print{}"

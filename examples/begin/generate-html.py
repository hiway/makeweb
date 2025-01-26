from makeweb import Doc
from makeweb.html import *


def generate_html():
    doc = Doc("html")
    with body():
        h1("Ha!")
    return str(doc)


print(generate_html())

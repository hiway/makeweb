from makeweb import Doc, body, h1


def generate_html():
    doc = Doc("html")
    with body():
        h1("Ha!")
    return str(doc)


print(generate_html())

from makeweb.javascript import JS, document

js = JS()


@js.function
def say_hello():
    hello_box = document.getElementById("hello_box")
    hello_box.innerHTML = "Hello, World Wide Web!"


print(str(js))

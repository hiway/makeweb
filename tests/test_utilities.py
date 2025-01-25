import pytest
from makeweb import defaults, fix_attribute, get_local_variable_from_caller
from makeweb.html import Doc


def test_fix_attribute():
    defaults.replace_single_underscore = True
    defaults.replace_double_underscore = False
    defaults.remove_first_underscore = True
    defaults.replace_className = True
    defaults.replace_cls = True

    assert fix_attribute("cls") == "class"
    assert fix_attribute("className") == "class"
    assert fix_attribute("_class") == "class"
    assert fix_attribute("_input") == "input"
    assert fix_attribute("left_align") == "left-align"
    assert fix_attribute("__moz_column_count") == "-moz-column-count"
    assert fix_attribute("snake_case") == "snake-case"

    defaults.replace_double_underscore = False
    assert fix_attribute("__keep_one") == "-keep-one"

    defaults.replace_double_underscore = True  # reset
    defaults.replace_single_underscore = True
    assert fix_attribute("__example_attr") == "-example-attr"

    defaults.replace_double_underscore = False
    defaults.replace_single_underscore = True
    assert fix_attribute("__example_attr") == "-example-attr"

    defaults.remove_first_underscore = False
    defaults.replace_double_underscore = False
    defaults.replace_single_underscore = True
    assert fix_attribute("__example_attr") == "--example-attr"

    with pytest.raises(TypeError):
        fix_attribute(808)

    # Test single underscore replacement
    defaults.replace_single_underscore = True
    assert fix_attribute("data_type") == "data-type"
    assert fix_attribute("aria_label") == "aria-label"

    defaults.replace_single_underscore = False
    assert fix_attribute("data_type") == "data_type"
    assert fix_attribute("aria_label") == "aria_label"

    # Reset to default
    defaults.replace_single_underscore = True
    defaults.replace_double_underscore = False
    defaults.remove_first_underscore = True
    defaults.replace_className = True
    defaults.replace_cls = True


def test_get_local_variable_from_caller_level_1():
    def caller_func():
        doc = Doc(doctype="html")
        test_magic()

    def test_magic():
        doc = get_local_variable_from_caller("doc", Doc)
        assert "html" in str(doc)
        with pytest.raises(LookupError):
            get_local_variable_from_caller("zoop", Doc)
        with pytest.raises(TypeError):
            get_local_variable_from_caller("doc", float)

    caller_func()


def test_get_local_variable_from_caller_level_2():
    def caller_func():
        doc = Doc(doctype="html")
        second_caller()

    def second_caller():
        test_magic()

    def test_magic():
        doc = get_local_variable_from_caller("doc", Doc)
        assert "html" in str(doc)
        with pytest.raises(LookupError):
            get_local_variable_from_caller("zoop", Doc)
        with pytest.raises(TypeError):
            get_local_variable_from_caller("doc", float)

    caller_func()


def test_get_local_variable_from_caller_level_3():
    def caller_func():
        doc = Doc(doctype="html")
        second_caller()

    def second_caller():
        [test_magic() for x in [0, 1]]

    def test_magic():
        doc = get_local_variable_from_caller("doc", Doc)
        assert "html" in str(doc)

    caller_func()


def test_get_local_variable_from_caller_level_4():
    def caller_func():
        second_caller()  # Note: doc is not defined here

    def second_caller():
        third_caller()

    def third_caller():
        test_magic()

    def test_magic():
        with pytest.raises(LookupError):
            # This should fail because doc is not defined in any parent frame
            doc = get_local_variable_from_caller("doc", Doc)

    caller_func()

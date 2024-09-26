from pytest import mark, fixture
from src.xml_element import XMLElement


@fixture(scope="function")
def root_element():
    return XMLElement(root=True)


class Test__init__:
    @mark.it(
        "XMLElement is initialised with attribute, value, root, children and parent by default"
    )
    def test_default_vals(self, root_element):
        assert "attribute" in dir(root_element)
        assert "value" in dir(root_element)
        assert "root" in dir(root_element)
        assert "children" in dir(root_element)
        assert "parent" in dir(root_element)


class Testadd_child:
    @mark.it("add_child adds an instance of XMLElement to children")
    def test_add_child_instance(self, root_element):
        root_element.add_child()
        for child in root_element.children:
            assert isinstance(child, XMLElement)

    @mark.it("add_child sets correct attribute")
    def test_add_child_attribute(self, root_element):
        root_element.add_child(("category", "cooking"))
        assert root_element.children[0].attribute == ("category", "cooking")

    @mark.it("add_child sets correct value")
    def test_add_child_value(self, root_element):
        root_element.add_child(value="Matthew")
        assert root_element.children[0].value == "Matthew"


class Testadd_sibling:
    @mark.it("add_sibling adds an instance of XMLElement to parent's children")
    def test_add_child_instance(self, root_element):
        root_element.add_child()
        root_element.children[0].add_sibling(value="Carrots")
        assert len(root_element.children) == 2
        assert root_element.children[1].value == "Carrots"

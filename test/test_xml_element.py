from pytest import mark, fixture
from src.xml_element import XMLElement


@fixture(scope="function")
def root_element():
    return XMLElement('bookstore',root=True)


class Test__init__:
    @mark.it(
        "XMLElement is initialised with tag, attribute, value, root, children and parent by default"
    )
    def test_default_vals(self, root_element):
        assert "tag" in dir(root_element)
        assert "attribute" in dir(root_element)
        assert "value" in dir(root_element)
        assert "root" in dir(root_element)
        assert "children" in dir(root_element)
        assert "parent" in dir(root_element)


class Testmake_child:
    @mark.it("make_child adds an instance of XMLElement to children")
    def test_add_child_instance(self, root_element):
        root_element.make_child('book')
        for child in root_element.children:
            assert isinstance(child, XMLElement)

    @mark.it("make_child sets correct attribute")
    def test_add_child_attribute(self, root_element):
        root_element.make_child('book', ("category", "cooking"))
        assert root_element.children[0].attribute == ("category", "cooking")

    @mark.it("make_child sets correct value")
    def test_add_child_value(self, root_element):
        root_element.make_child('book',value="Matthew")
        assert root_element.children[0].value == "Matthew"


class Testadd_sibling:
    @mark.it("add_sibling adds an instance of XMLElement to parent's children")
    def test_add_sibline(self, root_element):
        root_element.make_child('book')
        root_element.children[0].make_sibling(value="Carrots")
        assert len(root_element.children) == 2
        assert root_element.children[1].value == "Carrots"

    @mark.it("add_sibling sets new sibling's tag to own value by default")
    def test_add_subling_tag(self, root_element):
        root_element.make_child('book')
        root_element.last_child.make_sibling()
        for child in root_element.children:
            assert child.tag == 'book'

class Testlast_child:
    @mark.it('last_child returns only child')
    def test_last_child_one_child(self, root_element):
        test_child = XMLElement('book')
        root_element.add_child(test_child)
        assert root_element.last_child is test_child

    @mark.it('last_child returns None if children is empty')
    def test_last_child_no_child(self, root_element):
        assert not root_element.last_child

    @mark.it('last_child returns last child of many')
    def test_last_child_one_child(self, root_element):
        test_child1 = XMLElement('book')
        test_child2 = XMLElement('book')
        test_child3 = XMLElement('book')
        root_element.add_child(test_child1)
        root_element.add_child(test_child2)
        root_element.add_child(test_child3)
        assert root_element.last_child is test_child3

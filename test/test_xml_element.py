from pytest import mark, fixture, raises
from src.xml_element import XMLElement
from pickle import load


@fixture(scope="function")
def root_element():
    return XMLElement("bookstore", is_root=True)


class Test__init__:
    @mark.it(
        "XMLElement is initialised with tag, attribute, value, root, children, parent and root by default"
    )
    def test_default_vals(self, root_element):
        assert "tag" in dir(root_element)
        assert "attribute" in dir(root_element)
        assert "value" in dir(root_element)
        assert "is_root" in dir(root_element)
        assert "children" in dir(root_element)
        assert "parent" in dir(root_element)
        assert "root" in dir(root_element)

    @mark.it("Root element root value is self")
    def test_root_element_root(self, root_element):
        assert root_element.root is root_element


class Testadd_child:
    @mark.it("Added child has the correct parent")
    def test_correct_parent(self, root_element):
        test_child = XMLElement("book")
        root_element.add_child(test_child)
        assert root_element.last_child.parent is root_element

    @mark.it("Added child's is_root is false")
    def test_correct_root(self, root_element):
        test_child = XMLElement("book", is_root=True)
        root_element.add_child(test_child)
        assert not root_element.last_child.is_root

    @mark.it("Raises ValueError if calling add_child on self")
    def test_index_error_self_add(self, root_element):
        with raises(ValueError) as err:
            root_element.add_child(root_element)
        assert str(err.value) == "cannot add self as child"

    @mark.it("Added child's descendants' roots match its parent's")
    def test_correct_root_deep(self, root_element):
        test_parent = XMLElement("book", is_root=True)
        test_child = XMLElement("title")
        test_parent.add_child(test_child)
        root_element.add_child(test_parent)
        assert root_element.last_child.root is root_element
        assert root_element.last_child.last_child.root is root_element


class Testmake_child:
    @mark.it("make_child adds an instance of XMLElement to children")
    def test_add_child_instance(self, root_element):
        root_element.make_child("book")
        for child in root_element.children:
            assert isinstance(child, XMLElement)

    @mark.it("make_child sets correct attribute")
    def test_add_child_attribute(self, root_element):
        root_element.make_child("book", ("category", "cooking"))
        assert root_element.children[0].attribute == ("category", "cooking")

    @mark.it("make_child sets correct value")
    def test_add_child_value(self, root_element):
        root_element.make_child("book", value="Matthew")
        assert root_element.children[0].value == "Matthew"


class Testadd_sibling:
    @mark.it("add_sibling adds an instance of XMLElement to parent's children")
    def test_add_sibline(self, root_element):
        root_element.make_child("book")
        root_element.children[0].make_sibling(value="Carrots")
        assert len(root_element.children) == 2
        assert root_element.children[1].value == "Carrots"

    @mark.it("add_sibling sets new sibling's tag to own value by default")
    def test_add_subling_tag(self, root_element):
        root_element.make_child("book")
        root_element.last_child.make_sibling()
        for child in root_element.children:
            assert child.tag == "book"


class Testlast_child:
    @mark.it("last_child returns only child")
    def test_last_child_one_child(self, root_element):
        test_child = XMLElement("book")
        root_element.add_child(test_child)
        assert root_element.last_child is test_child

    @mark.it("last_child returns None if children is empty")
    def test_last_child_no_child(self, root_element):
        assert not root_element.last_child

    @mark.it("last_child returns last child of many")
    def test_last_child_one_child(self, root_element):
        test_child1 = XMLElement("book")
        test_child2 = XMLElement("book")
        test_child3 = XMLElement("book")
        root_element.add_child(test_child1)
        root_element.add_child(test_child2)
        root_element.add_child(test_child3)
        assert root_element.last_child is test_child3


class Testdepth:
    @mark.it("root element returns depth 0")
    def test_depth_0(self, root_element):
        result = root_element.depth
        assert result == 0

    @mark.it("child of root element returns depth 1")
    def test_depth_1(self, root_element):
        root_element.make_child("book")
        result = root_element.last_child.depth
        assert result == 1

    @mark.it("grandchild of root element returns depth 2")
    def test_depth_2(self, root_element):
        root_element.make_child("book")
        root_element.last_child.make_child("title")
        result = root_element.last_child.last_child.depth
        assert result == 2

    @mark.it("great grandchild of root element returns depth 3")
    def test_depth_3(self, root_element):
        root_element.make_child("book")
        root_element.last_child.make_child("title")
        root_element.last_child.last_child.make_child("colour")
        result = root_element.last_child.last_child.last_child.depth
        assert result == 3


class Testno_children:
    @mark.it("Element with no children added has 0 children")
    def test_no_children(self, root_element):
        assert root_element.no_children == 0

    @mark.it("Correctly returns number of direct children of an element")
    def test_many_children(self, root_element):
        root_element.make_child("book")
        root_element.last_child.make_sibling()
        root_element.last_child.make_child("title")
        assert root_element.no_children == 2


class Testsize:
    @mark.it("Element with nothing added has size 1")
    def test_size(self, root_element):
        assert root_element.size == 1

    @mark.it("Returns size of element whose children are all 'leaves'")
    def test_no_deep_descendants(self, root_element):
        root_element.make_child("book")
        root_element.last_child.make_sibling()
        assert root_element.size == 3

    @mark.it("Correcrtly returns size of nested tree")
    def test_deep_size(self):
        with open("test_data/bookstore.pkl", "rb") as f:
            loaded_tree = load(f)
        assert loaded_tree.size == 16


class Testdescendants:
    @mark.it("Root element's descendants are only itself")
    def test_root_descendants(self, root_element):
        assert len(root_element.descendants) == 1
        for descendant in root_element.descendants:
            assert descendant is root_element

    @mark.it(
        "Correctly returns descendants for element whose children are all 'leaves'"
    )
    def test_root_1_gen(self, root_element):
        root_element.make_child("book")
        root_element.last_child.make_sibling()
        root_element.last_child.make_sibling()
        root_element.last_child.make_sibling()
        expected = [root_element] + root_element.children
        result = root_element.descendants
        assert result == expected

    @mark.it("Correctly returns descendants for deep tree")
    def test_deep_descendants(self, root_element):
        test_child1 = XMLElement("book")
        root_element.add_child(test_child1)
        test_child11 = XMLElement("title", value="Harry Potter")
        root_element.last_child.add_child(test_child11)
        test_child2 = XMLElement("book")
        root_element.add_child(test_child2)
        test_child21 = XMLElement("title", value="Normal People")
        root_element.last_child.add_child(test_child21)
        test_child3 = XMLElement("book")
        root_element.add_child(test_child3)
        test_child31 = XMLElement("title", value="To Kill a Mockingbird")
        root_element.last_child.add_child(test_child31)
        test_child32 = XMLElement("price", value=9.99)
        root_element.last_child.add_child(test_child32)
        assert root_element.size == 8
        descendants = root_element.descendants
        for xmlelt in [
            test_child1,
            test_child2,
            test_child3,
            test_child11,
            test_child21,
            test_child31,
            test_child32,
            root_element,
        ]:
            assert xmlelt in descendants

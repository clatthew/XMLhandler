from pytest import mark, fixture, raises
from src.xml_element import XMLElement
from pickle import load
from src.xml_load import load_xml_from_file
from test_data.book_store.book_store import build_bookstore_file
import os


@fixture(scope="function")
def root_element():
    return XMLElement("bookstore")


class Test__init__:
    @mark.it(
        "XMLElement is initialised with tag, attributes, value, children, parent and root by default"
    )
    def test_default_vals(self, root_element):
        assert "tag" in dir(root_element)
        assert "attributes" in dir(root_element)
        assert "value" in dir(root_element)
        assert "children" in dir(root_element)
        assert "parent" in dir(root_element)
        assert "root" in dir(root_element)

    @mark.it("Root element root value is self")
    def test_root_element_root(self, root_element):
        assert root_element.root is root_element

    @mark.it("Raises ValueError if using & in tag_name")
    def test_ampersand_in_tag_name(self, root_element):
        with raises(ValueError) as err:
            root_element.make_child("Matt&Kim")
        assert str(err.value) == "Tag name may not contain &"

    @mark.it("Raises ValueError if using ' in tag_name")
    def test_apos_in_tag_name(self, root_element):
        with raises(ValueError) as err:
            root_element.make_child("Matt'Kim")
        assert str(err.value) == "Tag name may not contain '"

    @mark.it('Raises ValueError if using " in tag_name')
    def test_quote_in_tag_name(self, root_element):
        with raises(ValueError) as err:
            root_element.make_child('Matt"Kim')
        assert str(err.value) == 'Tag name may not contain "'

    @mark.it("Raises ValueError if using < in tag_name")
    def test_lt_in_tag_name(self, root_element):
        with raises(ValueError) as err:
            root_element.make_child("Matt<Kim")
        assert str(err.value) == "Tag name may not contain <"

    @mark.it("Raises ValueError if using > in tag_name")
    def test_gt_in_tag_name(self, root_element):
        with raises(ValueError) as err:
            root_element.make_child("Matt>Kim")
        assert str(err.value) == "Tag name may not contain >"

    @mark.it("Raises ValueError if using & in an attribute key")
    def test_ampersand_in_attr_key(self, root_element):
        with raises(ValueError) as err:
            root_element.make_child("Matthew", {"Matt and Kim": 0, "Matt&Kim": "yes"})
        assert str(err.value) == "Attribute key may not contain &"

    @mark.it("Raises ValueError if using ' in an attribute key")
    def test_apos_in_attr_key(self, root_element):
        with raises(ValueError) as err:
            root_element.make_child("Matthew", {"Matt and Kim": 0, "Matt'Kim": "yes"})
        assert str(err.value) == "Attribute key may not contain '"

    @mark.it('Raises ValueError if using " in an attribute key')
    def test_quote_in_attr_key(self, root_element):
        with raises(ValueError) as err:
            root_element.make_child("Matthew", {"Matt and Kim": 0, 'Matt"Kim': "yes"})
        assert str(err.value) == 'Attribute key may not contain "'

    @mark.it("Raises ValueError if using < in an attribute key")
    def test_lt_in_attr_key(self, root_element):
        with raises(ValueError) as err:
            root_element.make_child("Matthew", {"Matt and Kim": 0, "Matt<Kim": "yes"})
        assert str(err.value) == "Attribute key may not contain <"

    @mark.it("Raises ValueError if using > in an attribute key")
    def test_gt_in_attr_key(self, root_element):
        with raises(ValueError) as err:
            root_element.make_child("Matthew", {"Matt and Kim": 0, "Matt>Kim": "yes"})
        assert str(err.value) == "Attribute key may not contain >"


class Testadd_child:
    @mark.it("Added child has the correct parent")
    def test_correct_parent(self, root_element):
        test_child = XMLElement("book")
        root_element.add_child(test_child)
        assert root_element.last_child.parent is root_element

    @mark.it("Added child's is_root is false")
    def test_correct_root(self, root_element):
        test_child = XMLElement("book")
        root_element.add_child(test_child)
        assert not root_element.last_child.is_root

    @mark.it("Raises ValueError if calling add_child on self")
    def test_index_error_self_add(self, root_element):
        with raises(ValueError) as err:
            root_element.add_child(root_element)
        assert str(err.value) == "cannot add descendant as child"

    @mark.it("Added child's descendants' roots match its parent's")
    def test_correct_root_deep(self, root_element):
        test_parent = XMLElement("book")
        test_child = XMLElement("title")
        test_parent.add_child(test_child)
        root_element.add_child(test_parent)
        assert root_element.last_child.root is root_element
        assert root_element.last_child.last_child.root is root_element


class Testpath:
    @mark.it("Root element has path []")
    def test_root_path(self, root_element):
        assert root_element.path == []

    @mark.it("First child added to root element has path [0]")
    def test_first_child_path(self, root_element):
        test_child = XMLElement("book")
        root_element.add_child(test_child)
        assert test_child.path == [0]

    @mark.it(
        "Third child added to first child added to root element has path [0, 2]. Path is correct, irrelevant of what order elements were added."
    )
    def test_first_child_third_child_path(self, root_element):
        test_child1 = XMLElement("book")
        test_child2 = XMLElement("title")
        test_child3 = XMLElement("length")
        test_child4 = XMLElement("price")
        test_child1.add_child(test_child2)
        test_child1.add_child(test_child3)
        test_child1.add_child(test_child4)
        root_element.add_child(test_child1)
        assert test_child4.path == [0, 2]

    @mark.it("That child's second child has path [0, 2, 1]")
    def test_first_child_third_child_child_path(self, root_element):
        test_child1 = XMLElement("book")
        test_child2 = XMLElement("title")
        test_child3 = XMLElement("length")
        test_child4 = XMLElement("price")
        root_element.add_child(test_child1)
        root_element.last_child.add_child(test_child2)
        root_element.last_child.add_child(test_child3)
        root_element.last_child.add_child(test_child4)
        test_child4.make_child("euro", value=20)
        test_child4.make_child("pound", value=18)
        assert test_child4.last_child.path == [0, 2, 1]


class Testmake_child:
    @mark.it("make_child adds an instance of XMLElement to children")
    def test_add_child_instance(self, root_element):
        root_element.make_child("book")
        for child in root_element.children:
            assert isinstance(child, XMLElement)

    @mark.it("make_child sets correct attribute")
    def test_add_child_attribute(self, root_element):
        root_element.make_child("book", {"category": "cooking"})
        assert root_element.children[0].attributes == {"category": "cooking"}

    @mark.it("make_child sets correct value")
    def test_add_child_value(self, root_element):
        root_element.make_child("book", value="Matthew")
        assert root_element.children[0].value == "Matthew"


class Testmake_sibling:
    @mark.it("make_sibling adds an instance of XMLElement to parent's children")
    def test_make_sibling(self, root_element):
        root_element.make_child("book")
        root_element.children[0].make_sibling(value="Carrots")
        assert len(root_element.children) == 2
        assert root_element.children[1].value == "Carrots"

    @mark.it("make_sibling sets new sibling's tag to own value by default")
    def test_make_sibling_tag(self, root_element):
        root_element.make_child("book")
        root_element.last_child.make_sibling()
        for child in root_element.children:
            assert child.tag == "book"


class Testadd_sibling:
    @mark.it("add_sibling adds the passed object to its parent's children")
    def test_add_sibling_list(self, root_element):
        test_child1 = XMLElement("book")
        test_child2 = XMLElement("book")
        root_element.add_child(test_child1)
        test_child1.add_sibling(test_child2)
        assert test_child2 in root_element.children

    @mark.it("add_sibling changes the new sibling's root")
    def test_add_sibling_root(self, root_element):
        test_child1 = XMLElement("book")
        test_child2 = XMLElement("book")
        root_element.add_child(test_child1)
        test_child1.add_sibling(test_child2)
        assert test_child2.root is root_element

    @mark.it("add_sibling changes the new sibling's parent")
    def test_add_sibling_parent(self, root_element):
        test_child1 = XMLElement("book")
        test_child2 = XMLElement("book")
        root_element.add_child(test_child1)
        test_child1.add_sibling(test_child2)
        assert test_child2.parent is root_element


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
        test_tree = build_bookstore_file()
        assert test_tree.size == 16


# This should be made into a true interator
class Test__iter__:
    @mark.it("Root element's descendants are only itself")
    def test_root_descendants(self, root_element):
        assert len(root_element.descendants) == 1
        for descendant in list(root_element):
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
        result = list(root_element)
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
        descendants = list(root_element)
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


class Test_make_xml_tags:
    @mark.it("Root element has correct XML tags")
    def test_root_tags(self, root_element):
        tag = root_element.tag
        expected = ["", f"<{tag}>", None, f"</{tag}>"]
        assert root_element.make_xml_tags(2, self_closing=False) == expected

    @mark.it("Element with attribute has correct XML tags")
    def test_attribute_tags(self, root_element):
        test_parent = XMLElement("book", attributes={"category": "children"})
        root_element.add_child(test_parent)
        tag = root_element.last_child.tag
        expected = ["  ", f'<{tag} category="children">', None, f"</{tag}>"]
        assert root_element.last_child.make_xml_tags(2, self_closing=False) == expected

    @mark.it("Leaf element with value has correct XML tags")
    def test_value_tags(self, root_element):
        test_parent = XMLElement("book", attributes={"category": "children"})
        test_child = XMLElement("title", value="Harry Potter")
        test_parent.add_child(test_child)
        root_element.add_child(test_parent)
        tag = root_element.last_child.last_child.tag
        expected = ["    ", f"<{tag}>", "Harry Potter", f"</{tag}>"]
        assert (
            root_element.last_child.last_child.make_xml_tags(2, self_closing=False)
            == expected
        )

    @mark.it("Leaf element with value and attribute has correct XML tags")
    def test_value_attribute_tags(self, root_element):
        test_parent = XMLElement("book", attributes={"category": "children"})
        test_child = XMLElement(
            "title", attributes={"quality": "terrible"}, value="Harry Potter"
        )
        test_parent.add_child(test_child)
        root_element.add_child(test_parent)
        tag = root_element.last_child.last_child.tag
        expected = ["    ", f'<{tag} quality="terrible">', "Harry Potter", f"</{tag}>"]
        assert (
            root_element.last_child.last_child.make_xml_tags(2, self_closing=False)
            == expected
        )

    @mark.it("Leaf element with numerical value has correct XML tags")
    def test_value_tags_int(self, root_element):
        test_parent = XMLElement("book", attributes={"category": "children"})
        test_child = XMLElement("price", value=555)
        test_parent.add_child(test_child)
        root_element.add_child(test_parent)
        tag = root_element.last_child.last_child.tag
        expected = ["    ", f"<{tag}>", "555", f"</{tag}>"]
        assert (
            root_element.last_child.last_child.make_xml_tags(2, self_closing=False)
            == expected
        )

    @mark.it("Tags with multiple attributes have correct XML tags")
    def test_multiple_attributes_make_tags(self, root_element):
        root_element.make_child(
            "book", {"category": "children", "rating": "good", "level": "hard"}
        )
        expected = [
            "  ",
            '<book category="children" rating="good" level="hard">',
            None,
            "</book>",
        ]
        result = root_element.last_child.make_xml_tags(2, self_closing=False)
        assert result == expected


class Testto_xml:
    @mark.it("Forms the correct XML file for the bookstore data")
    def test_correct_xml_output(self):
        # get bookstore object structure
        test_tree = build_bookstore_file()
        # dump it to XML
        test_tree.to_xml("test_data/book_store/test_xml.xml", self_closing=False)
        # read the resulting xml file
        with open("test_data/book_store/test_xml.xml") as f:
            test_data = f.readlines()
        # read the sample bookstore xml
        with open("test_data/book_store/bookstore.xml") as f:
            bookstore_data = f.readlines()
        # delete the created test file
        os.remove("test_data/book_store/test_xml.xml")
        # compare the generated xml to the original
        assert bookstore_data == test_data

    @mark.it(
        "Handles int and float values in tag_name, attribute key and val, and value"
    )
    def test_integer_in_val(self):
        test_tree = load_xml_from_file("test_data/book_store/bookstore.xml")
        # print(test_tree)
        test_child = XMLElement("66.6", {"amount": 56})
        test_child.make_child("title", {"lang": 72}, 5555)
        test_child.make_child("price", {56: 23.2}, 39.99)
        test_tree.add_child(test_child)
        test_tree.to_xml("test_data/numeric/test_xml.xml", self_closing=False)
        with open("test_data/numeric/test_xml.xml") as f:
            test_data = f.readlines()
        os.remove("test_data/numeric/test_xml.xml")
        with open("test_data/numeric/numeric.xml") as f:
            original_data = f.readlines()
        assert test_data == original_data

    @mark.it("Correctly substitutes user-defined entity references into value")
    def test_entity_refs(self, root_element):
        root_element.add_entity({"l": "j"})
        root_element.add_attribute({"company": "Waterstones"})
        test_child = XMLElement("book", value="hello!")
        test_child.add_entity({"Waterstones": "company"})
        root_element.add_child(test_child)
        test_child.make_sibling("book", value="Waterstones")
        root_element.to_xml(
            "test_data/def_entity_refs/test_xml.xml", self_closing=False
        )
        with open("test_data/def_entity_refs/test_xml.xml") as f:
            test_data = f.readlines()
        os.remove("test_data/def_entity_refs/test_xml.xml")
        with open("test_data/def_entity_refs/def_entity_refs.xml") as f:
            original_data = f.readlines()
        assert test_data == original_data

    @mark.it("Indents xml document with the specified tab size of 5")
    def test_variable_tab_size5(self):
        test_tree = build_bookstore_file()
        test_tree.to_xml(
            "test_data/book_store/test_xml.xml", tab_size=5, self_closing=False
        )
        with open("test_data/book_store/test_xml.xml", "r") as f:
            test_data = f.readlines()
        os.remove("test_data/book_store/test_xml.xml")
        with open("test_data/book_store/bookstore5.xml", "r") as f:
            original_data = f.readlines()
        assert test_data == original_data

    @mark.it("Indents xml document with the specified tab size of 0")
    def test_variable_tab_size0(self):
        test_tree = build_bookstore_file()
        test_tree.to_xml(
            "test_data/book_store/test_xml.xml", tab_size=0, self_closing=False
        )
        with open("test_data/book_store/test_xml.xml", "r") as f:
            test_data = f.readlines()
        os.remove("test_data/book_store/test_xml.xml")
        with open("test_data/book_store/bookstore0.xml", "r") as f:
            original_data = f.readlines()
        assert test_data == original_data

    @mark.it('Writes encoding="UTF-8" by default when encoding not set')
    def test_default_encoding(self):
        expected_path = "test_data/weird_metadata/default_encoding.xml"
        result_path = "test_data/weird_metadata/test_xml.xml"
        test_tree = XMLElement("matthew", xml_version="22")
        test_tree.to_xml(result_path)
        with open(expected_path, "r") as f:
            result = f.readlines()
        with open(expected_path, "r") as f:
            expected = f.readlines()
        os.remove(result_path)
        assert result == expected

    @mark.it('Writes xml version="1.0" when xml_version not set')
    def test_default_version(self):
        expected_path = "test_data/weird_metadata/default_xml_version.xml"
        result_path = "test_data/weird_metadata/test_xml.xml"
        test_tree = XMLElement("matthew", encoding="happy birthDa9y")
        test_tree.to_xml(result_path)
        with open(expected_path, "r") as f:
            result = f.readlines()
        with open(expected_path, "r") as f:
            expected = f.readlines()
        os.remove(result_path)
        assert result == expected

    @mark.it("Correctly writes custom metadata to a file")
    def test_write_custom_metadata(self):
        expected_path = "test_data/weird_metadata/weird_metadata.xml"
        result_path = "test_data/weird_metadata/test_xml.xml"
        test_tree = XMLElement(
            "matthew", encoding="happy birthDa9y", xml_version="22.5"
        )
        test_tree.to_xml(result_path)
        with open(expected_path, "r") as f:
            result = f.readlines()
        with open(expected_path, "r") as f:
            expected = f.readlines()
        os.remove(result_path)
        assert result == expected


class Testadd_attribute:
    @mark.it("Add first attribute")
    def test_first(self, root_element):
        root_element.add_attribute({"name": "Waterstones"})
        assert root_element.attributes == {"name": "Waterstones"}

    @mark.it("Add attribute to existing attributes")
    def test_existing(self, root_element):
        root_element.add_attribute({"name": "Waterstones"})
        root_element.add_attribute({"location": "Peckham"})
        assert root_element.attributes == {"name": "Waterstones", "location": "Peckham"}

    @mark.it("Add multiple attributes simultaneously")
    def test_multi(self, root_element):
        root_element.add_attribute({"name": "Waterstones", "location": "Peckham"})
        root_element.add_attribute({"street": "high street", "business": "high"})
        assert root_element.attributes == {
            "name": "Waterstones",
            "location": "Peckham",
            "street": "high street",
            "business": "high",
        }

    @mark.it("Raises TypeError if added attribute is not a dict")
    def test_not_dict(self, root_element):
        with raises(TypeError) as err:
            root_element.add_attribute(["hello"])
        assert str(err.value) == "Attribute must be of type dict"


class Testadd_entity:
    @mark.it("Add first entity")
    def test_first(self, root_element):
        root_element.add_entity({"name": "Waterstones"})
        assert root_element.entities == {"name": "Waterstones"}

    @mark.it("Add entity to existing entities")
    def test_existing(self, root_element):
        root_element.add_entity({"name": "Waterstones"})
        root_element.add_entity({"location": "Peckham"})
        assert root_element.entities == {"name": "Waterstones", "location": "Peckham"}

    @mark.it("Add multiple entities simultaneously")
    def test_multi(self, root_element):
        root_element.add_entity({"name": "Waterstones", "location": "Peckham"})
        root_element.add_entity({"street": "high street", "business": "high"})
        assert root_element.entities == {
            "name": "Waterstones",
            "location": "Peckham",
            "street": "high street",
            "business": "high",
        }

    @mark.it("Raises TypeError if added entity is not a dict")
    def test_not_dict(self, root_element):
        with raises(TypeError) as err:
            root_element.add_entity(["hello"])
        assert str(err.value) == "Entity must be of type dict"


class Testremove_attribute:
    @mark.it("Successfully remove existing attribute from element using attribute key")
    def test_remove_attr(self, root_element):
        root_element.add_attribute({"name": "Waterstones"})
        root_element.remove_attribute("name")
        assert not root_element.attributes
        root_element.add_attribute({"name": "Waterstones"})
        root_element.add_attribute({"location": "Peckham"})
        root_element.remove_attribute("name")
        assert root_element.attributes == {"location": "Peckham"}

    @mark.it("Raises KeyError if attribute key doesn't exist")
    def test_remove_attr_keyerror(self, root_element):
        root_element.add_attribute({"name": "Waterstones"})
        test_key = "ame"
        with raises(KeyError) as err:
            root_element.remove_attribute(test_key)
        assert str(err.value) == f"'{test_key}'"


class Testremove_entity:
    @mark.it("Successfully remove existing entity from element using entity key")
    def test_remove_ent(self, root_element):
        root_element.add_entity({"name": "Waterstones"})
        root_element.remove_entity("name")
        assert not root_element.entities
        root_element.add_entity({"name": "Waterstones"})
        root_element.add_entity({"location": "Peckham"})
        root_element.remove_entity("name")
        assert root_element.entities == {"location": "Peckham"}

    @mark.it("Raises KeyError if entity key doesn't exist")
    def test_remove_ent_keyerror(self, root_element):
        root_element.add_entity({"name": "Waterstones"})
        test_key = "ame"
        with raises(KeyError) as err:
            root_element.remove_entity(test_key)
        assert str(err.value) == f"'{test_key}'"


class Testget_from_path:
    @mark.it("Retrieves root element when passed path []")
    def test_root(self, root_element):
        result = root_element.get_from_path([])
        assert result is root_element

    @mark.it("Retrieves root element's second child when passed path [1]")
    def test_child(self, root_element):
        test_child1 = XMLElement("book")
        test_child2 = XMLElement("book")
        root_element.add_child(test_child1)
        root_element.add_child(test_child2)
        result = root_element.get_from_path([1])
        assert result is test_child2

    @mark.it(
        "Retrieves the third child added to first child added to root element when passed path [0, 2]."
    )
    def test_grandchild(self, root_element):
        test_child1 = XMLElement("book")
        test_child2 = XMLElement("title")
        test_child3 = XMLElement("length")
        test_child4 = XMLElement("price")
        test_child1.add_child(test_child2)
        test_child1.add_child(test_child3)
        test_child1.add_child(test_child4)
        root_element.add_child(test_child1)
        result = root_element.get_from_path([0, 2])
        assert result is test_child4

    @mark.it("Retrieves that child's second child when passed path [0, 2, 1]")
    def test_first_child_third_child_child_path(self, root_element):
        test_child1 = XMLElement("book")
        test_child2 = XMLElement("title")
        test_child3 = XMLElement("length")
        test_child4 = XMLElement("price")
        root_element.add_child(test_child1)
        root_element.last_child.add_child(test_child2)
        root_element.last_child.add_child(test_child3)
        root_element.last_child.add_child(test_child4)
        test_child4.make_child("euro", value=20)
        test_child4.make_child("pound", value=18)
        result = root_element.get_from_path([0, 2, 1])
        assert result is test_child4.last_child

    @mark.it("Raises IndexError if requested path is not in the tree")
    def test_index_error(self, root_element):
        with raises(IndexError) as err:
            root_element.get_from_path([0])
        assert str(err.value) == "no element found at path [0]"
        root_element.make_child("book")
        with raises(IndexError) as err:
            root_element.get_from_path([0, 0])
        assert str(err.value) == "no element found at path [0, 0]"


class Testremove_from_path:
    @mark.it("Does not allow removal of the root element")
    def test_remove_root(self, root_element):
        with raises(IndexError) as err:
            root_element.remove_from_path([])
        assert str(err.value) == "cannot remove root element"

    @mark.it(
        "Raises IndexError when attempting to remove element from path not in tree"
    )
    def test_remove_non_existent(self, root_element):
        with raises(IndexError) as err:
            root_element.remove_from_path([0])
        assert str(err.value) == "no element found at path [0]"

    @mark.it("Successfully removes 'leaf' element and updates size accordingly")
    def test_remove_leaf(self, root_element):
        test_child1 = XMLElement("book")
        test_child2 = XMLElement("book")
        root_element.add_child(test_child1)
        root_element.add_child(test_child2)
        root_element.remove_from_path([1])
        assert root_element.size == 2
        assert test_child2 not in list(root_element)

    @mark.it("Successfully removes element with children and updates size accordingly")
    def test_remove_element_with_kids(self, root_element):
        test_child1 = XMLElement("book")
        test_child2 = XMLElement("title")
        test_child3 = XMLElement("length")
        test_child4 = XMLElement("price")
        root_element.add_child(test_child1)
        root_element.last_child.add_child(test_child2)
        root_element.last_child.add_child(test_child3)
        root_element.last_child.add_child(test_child4)
        test_child4.make_child("euro", value=20)
        test_child5 = XMLElement("pound", value=18)
        test_child4.add_child(test_child5)
        root_element.remove_from_path([0, 2])
        assert root_element.size == 4
        assert test_child4 not in list(root_element)
        assert test_child5 not in list(root_element)


class Testvalue:
    @mark.it("Value cannot be added to an element with children")
    def test_value_children(self, root_element):
        root_element.make_child("book")
        with raises(ValueError) as err:
            root_element.value = "hello"
        assert str(err.value) == "Cannot add value to an element with children"

    @mark.it("Children cannot be added to an element with a value")
    def test_children_value(self, root_element):
        root_element.value = "hello"
        with raises(ValueError) as err:
            root_element.make_child("hello")
        assert (
            str(err.value)
            == "Cannot add children to an element with a value. Please set value to None."
        )

    @mark.it("Value can be updated")
    def test_value_update(self, root_element):
        root_element.make_child("book", value="the wasp factory")
        root_element.last_child.value = "The Wasp Factory"
        assert root_element.last_child.value == "The Wasp Factory"


class Testprint_line:
    @mark.it("Returns correct string for root tag")
    def test_root_string(self, root_element):
        result = root_element.print_line()
        assert "bookstore" in result
        assert "[]" in result
        assert result.index("b") == 4

    @mark.it("Returns correct string for child tag")
    def test_root_child_string(self, root_element):
        root_element.make_child("book")
        result = root_element.last_child.print_line()
        assert "book" in result
        assert "[0]" in result
        assert result.index("∟") == 0
        assert result.index("b") == 5

    @mark.it("Returns correct string for root's grandchild tag with attributes")
    def test_root_grandchild_attr(self, root_element):
        root_element.make_child("book")
        root_element.last_child.make_child("title", {"lang": "en"})
        result = root_element.last_child.last_child.print_line()
        assert "title" in result
        assert "[0, 0]" in result
        assert result.index("∟") == 3
        assert result.index("t") == 8

    @mark.it(
        'Returns correct string for root\'s great grandchild ("leaf") tag with value'
    )
    def test_root_greatgrandchild_val(self, root_element):
        root_element.make_child("book")
        root_element.last_child.make_child("title", {"lang": "en"})
        root_element.last_child.last_child.make_child(
            "page", value="Once upon a time..."
        )
        result = root_element.get_from_path([0, 0, 0]).print_line()
        assert "page" in result
        assert "Once upon a time..." in result
        assert "[0, 0, 0]" in result
        assert result.index("∟") == 6
        assert result.index("p") == 11

    @mark.it(
        'Returns correct string for root\'s great grandchild ("leaf") tag with value and attributes'
    )
    def test_root_greatgrandchild_val_attr(self, root_element):
        root_element.make_child("book")
        root_element.last_child.make_child("title", {"lang": "en"})
        root_element.last_child.last_child.make_child(
            "page",
            value="Once upon a time...",
            attributes={"number": 24, "side": "left"},
        )
        result = root_element.get_from_path([0, 0, 0]).print_line()
        assert "page" in result
        assert "Once upon a time..." in result
        assert "[0, 0, 0]" in result
        assert result.index("∟") == 6
        assert result.index("p") == 11
        assert 'number="24" side="left"' in result

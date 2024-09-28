from src.xml_load import load_xml_from_file
from pytest import mark
import os


@mark.it(
    "Loading from bookstore.xml file to object structure, then dumping to XML results in an XML file identical to bookstore.xml"
)
def test_load_and_dump_bookstore():
    test_tree = load_xml_from_file("test_data/book_store/bookstore.xml")
    test_tree.to_xml("test_data/book_store/test_xml.xml")
    with open("test_data/book_store/test_xml.xml") as f:
        test_data = f.readlines()
    with open("test_data/book_store/bookstore.xml") as f:
        bookstore_data = f.readlines()
    os.remove("test_data/book_store/test_xml.xml")
    assert bookstore_data == test_data


@mark.it(
    "Loading from leaf_without_value.xml to object structure, then dumping to XML results in an XML file identical to leaf_without_value.xml"
)
def test_pathological():
    test_tree = load_xml_from_file(
        "test_data/leaf_without_value/leaf_without_value.xml"
    )
    test_tree.to_xml("test_data/leaf_without_value/test_xml.xml")
    with open("test_data/leaf_without_value/test_xml.xml") as f:
        test_data = f.readlines()
    with open("test_data/leaf_without_value/leaf_without_value.xml") as f:
        original_data = f.readlines()
    os.remove("test_data/leaf_without_value/test_xml.xml")
    assert original_data == test_data


@mark.it(
    "Loading from predef_entity_refs.xml to object structure, then dumping to XML results in an XML file identical to predef_entity_refs.xml"
)
def test_prefef_refs():
    test_tree = load_xml_from_file("test_data/entity_refs/predef_entity_refs.xml")
    test_tree.to_xml("test_data/entity_refs/test_xml.xml")
    with open("test_data/entity_refs/test_xml.xml") as f:
        test_data = f.readlines()
    with open("test_data/entity_refs/predef_entity_refs.xml") as f:
        original_data = f.readlines()
    os.remove("test_data/entity_refs/test_xml.xml")
    assert original_data == test_data

@mark.skip()
@mark.it(
    "Loading from predef_entity_refs.xml to object structure results in object structure with the entity referecnes replaced with their actual values"
)
def test_predef_refs_replace():
    test_tree = load_xml_from_file("test_data/entity_refs/predef_entity_refs.xml")
    assert test_tree.get_from_path([0]).value == "2 < 5"
    assert test_tree.get_from_path([1]).value == "5 > 2"
    assert test_tree.get_from_path([2]).value == "House & Garden"
    assert test_tree.get_from_path([3]).value == "Matthew's Computer"
    assert test_tree.get_from_path([4]).value == 'The computer is "old"'

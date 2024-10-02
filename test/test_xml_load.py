from src.xml_load import load_xml_from_file, remove_refs
from pytest import mark
import os


@mark.it(
    "Loading from bookstore.xml file to object structure, then dumping to XML, results in an XML file identical to bookstore.xml"
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
    "Loading from leaf_without_value.xml to object structure, then dumping to XML, results in an XML file identical to leaf_without_value.xml"
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


@mark.skip()
@mark.it(
    "Loading from predef_entity_refs.xml to object structure, then dumping to XML, results in an XML file identical to predef_entity_refs.xml"
)
def test_remove_refs_full_cycle():
    test_tree = load_xml_from_file("test_data/entity_refs/predef_entity_refs.xml")
    test_tree.to_xml("test_data/entity_refs/test_xml.xml")
    with open("test_data/entity_refs/test_xml.xml") as f:
        test_data = f.readlines()
    with open("test_data/entity_refs/predef_entity_refs.xml") as f:
        original_data = f.readlines()
    os.remove("test_data/entity_refs/test_xml.xml")
    assert original_data == test_data


@mark.it(
    "Loading from predef_entity_refs.xml to object structure results in object structure with the entity references replaced with their actual values"
)
def test_remove_refs_object():
    test_tree = load_xml_from_file("test_data/entity_refs/predef_entity_refs.xml")
    assert test_tree.get_from_path([0]).value == "2 < 5"
    assert test_tree.get_from_path([1]).value == "5 > 2"
    assert test_tree.get_from_path([2]).value == "House & Garden"
    assert test_tree.get_from_path([3]).value == "Matthew's Computer"
    assert test_tree.get_from_path([4]).value == 'The computer is "old"'
    assert test_tree.get_from_path([5]).attribute == ("type", "'PC&Mac'")
    assert test_tree.get_from_path([5]).value == "The computer is < slow"


class Testremove_refs:
    @mark.it('Removes single instance of "&lt;" and replaces it with "<"')
    def test_lt_single(self):
        test_data = "&lt;"
        result = remove_refs(test_data)
        expected = "<"
        assert result == expected

    @mark.it(
        'Removes multiple instances of "&lt;" inside a word and replaces them with "<"'
    )
    def test_lt_word(self):
        test_data = "my favourite inequality is 5 &lt; 6, tha&lt;t is cool"
        result = remove_refs(test_data)
        expected = "my favourite inequality is 5 < 6, tha<t is cool"
        assert result == expected

    @mark.it('Removes single instance of "&gt;" and replaces it with ">"')
    def test_gt_single(self):
        test_data = "&gt;"
        result = remove_refs(test_data)
        expected = ">"
        assert result == expected

    @mark.it(
        'Removes multiple instances of "&lt;" inside a word and replaces them with ">"'
    )
    def test_gt_word(self):
        test_data = "my favourite inequality is 6 &gt; 5, tha&gt;t is cool"
        result = remove_refs(test_data)
        expected = "my favourite inequality is 6 > 5, tha>t is cool"
        assert result == expected

    @mark.it('Removes single instance of "&amp;" and replaces it with "&"')
    def test_amp_single(self):
        test_data = "&amp;"
        result = remove_refs(test_data)
        expected = "&"
        assert result == expected

    @mark.it(
        'Removes multiple instances of "&amp;" inside a word and replaces them with "&"'
    )
    def test_amp_word(self):
        test_data = "my favourite numbers are 6 &amp; 5, the&amp;y are cool"
        result = remove_refs(test_data)
        expected = "my favourite numbers are 6 & 5, the&y are cool"
        assert result == expected

    @mark.it('Removes single instance of "&apos;" and replaces it with "\'"')
    def test_apos_single(self):
        test_data = "&apos;"
        result = remove_refs(test_data)
        expected = "'"
        assert result == expected

    @mark.it(
        'Removes multiple instances of "&apos;" inside a word and replaces them with "\'"'
    )
    def test_apos_word(self):
        test_data = "my favourite punctuation is &apos;, it&apos;s really cool"
        result = remove_refs(test_data)
        expected = "my favourite punctuation is ', it's really cool"
        assert result == expected

    @mark.it('Removes single instance of "&quot;" and replaces it with \'"\'')
    def test_quot_single(self):
        test_data = "&quot;"
        result = remove_refs(test_data)
        expected = '"'
        assert result == expected

    @mark.it(
        'Removes multiple instances of "&quot;" inside a word and replaces them with \'"\''
    )
    def test_quot_word(self):
        test_data = (
            "&quot;my favourite punctuation is &quot;, it&quot;s really cool&quot;"
        )
        result = remove_refs(test_data)
        expected = '"my favourite punctuation is ", it"s really cool"'
        assert result == expected

    @mark.it("Correctly handles pathalogical mixed example")
    def test_all(self):
        test_data = "&lt;&gt;&amp;&amp;&apos;&quot;&gt;&apos;"
        result = remove_refs(test_data)
        expected = "<>&&'\">'"
        assert result == expected

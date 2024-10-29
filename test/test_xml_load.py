from src.xml_load import *
from pytest import mark, raises
import os


@mark.it(
    "Loading from bookstore.xml file to object structure, then dumping to XML, results in an XML file identical to bookstore.xml"
)
def test_load_and_dump_bookstore():
    expected_path = "test_data/book_store/bookstore.xml"
    result_path = "test_data/book_store/test_xml.xml"
    test_tree = load_xml_from_file(expected_path)
    test_tree.to_xml(result_path)
    with open(result_path) as f:
        test_data = f.readlines()
    with open(expected_path) as f:
        bookstore_data = f.readlines()
    os.remove(result_path)
    assert bookstore_data == test_data


@mark.it(
    "Loading from leaf_without_value.xml to object structure, then dumping to XML, results in an XML file identical to leaf_without_value.xml"
)
def test_pathological():
    expected_path = "test_data/leaf_without_value/leaf_without_value.xml"
    result_path = "test_data/leaf_without_value/test_xml.xml"
    test_tree = load_xml_from_file(expected_path)
    test_tree.to_xml(result_path, self_closing=False)
    with open(result_path) as f:
        test_data = f.readlines()
    with open(expected_path) as f:
        original_data = f.readlines()
    os.remove(result_path)
    assert original_data == test_data


@mark.it("Correctly load XML file containing tags with multiple attributes")
def test_multiple_attributes():
    expected_path = "test_data/multi_attrs/multi_attrs.xml"
    result_path = "test_data/multi_attrs/test_xml.xml"
    test_tree = load_xml_from_file(expected_path)
    test_tree.to_xml(result_path, self_closing=False)
    with open(result_path) as f:
        test_data = f.readlines()
    with open(expected_path) as f:
        original_data = f.readlines()
    os.remove(result_path)
    assert original_data == test_data


@mark.it(
    "Loading from predef_entity_refs.xml to object structure, then dumping to XML, results in an XML file identical to predef_entity_refs.xml, ie. correctly replaces entity refs both when reading and writing xml"
)
def test_remove_refs_full_cycle():
    expected_path = "test_data/entity_refs/predef_entity_refs.xml"
    result_path = "test_data/entity_refs/test_xml.xml"
    test_tree = load_xml_from_file(expected_path)
    test_tree.to_xml(result_path, self_closing=False)
    with open(result_path) as f:
        test_data = f.readlines()
    with open(expected_path) as f:
        original_data = f.readlines()
    os.remove(result_path)
    assert original_data == test_data


@mark.it(
    "Loading from predef_entity_refs.xml to object structure results in object structure with the entity references in values replaced with their actual values"
)
def test_remove_refs_values():
    test_tree = load_xml_from_file("test_data/entity_refs/predef_entity_refs.xml")
    assert test_tree.get_from_path([0]).value == "2 < 5"
    assert test_tree.get_from_path([1]).value == "5 > 2"
    assert test_tree.get_from_path([2]).value == "House & Garden"
    assert test_tree.get_from_path([3]).value == "Matthew's Computer"
    assert test_tree.get_from_path([4]).value == 'The computer is "old"'
    assert test_tree.get_from_path([5]).value == "The computer is < slow"


@mark.it(
    "Loading from predef_entity_refs.xml to object structure results in object structure with the entity references in attributes replaced with their actual values"
)
def test_remove_refs_attribute():
    test_tree = load_xml_from_file("test_data/entity_refs/predef_entity_refs.xml")
    assert test_tree.get_from_path([5]).attributes == {"type": "'PC&Mac'"}
    test_tree = load_xml_from_file("test_data/multi_attrs/multi_attrs.xml")
    assert test_tree.get_from_path([0]).attributes == {
        "category": "cooking",
        "pictures": "lots",
        "colour": "green",
    }
    assert test_tree.get_from_path([0, 0]).attributes == {
        "lang": "en",
        "second_lang": "ar",
    }


@mark.it("Correctly reads self-closing tag with attributes")
def test_self_closing_attr():
    test_tree = load_xml_from_file("test_data/self_closing/self_closing.xml")
    assert test_tree.get_from_path([0]).attributes == {"category": "cooking"}
    assert test_tree.get_from_path([0, 0]).attributes == {
        "lang": "en",
        "second_lang": "de",
    }
    assert not test_tree.get_from_path([]).attributes
    assert not test_tree.get_from_path([0, 1]).attributes
    assert not test_tree.get_from_path([0, 2]).attributes


@mark.it("Reads self-closing tags as leaves with no value")
def test_self_closing_vals():
    test_tree = load_xml_from_file("test_data/self_closing/self_closing.xml")
    assert not test_tree.get_from_path([0]).value
    assert not test_tree.get_from_path([0, 0]).value
    assert not test_tree.get_from_path([0, 1]).value
    assert not test_tree.get_from_path([0, 2]).value


@mark.it(
    "Loading from XML file with custom defined entity refs results in these entity refs being stored in the root's entities attribute"
)
def test_load_xml_custom_entity_refs():
    test_tree = load_xml_from_file("test_data/def_entity_refs/def_entity_refs.xml")
    assert test_tree.entities == {"Waterstones": "company", "l": "j"}


@mark.it(
    "Raises TypeError when attempting to load from file which doesn't contain an XML tree structure"
)
def test_load_faulty_file():
    with raises(TypeError) as err:
        load_xml_from_file("test_data/not_xml/not_xml.sc")
    assert (
        str(err.value) == "No parsable XML tree found at test_data/not_xml/not_xml.sc."
    )


@mark.it(
    "Raises TypeError when trying to load from file which contains correct first line but doesn't contain an XML tree structure"
)
def test_load_faulty_file_2():
    with raises(TypeError) as err:
        load_xml_from_file("test_data/not_xml/also_not_xml.sc")
    assert (
        str(err.value)
        == "No parsable XML tree found at test_data/not_xml/also_not_xml.sc."
    )


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


class Testextract_entities:
    @mark.it("Extracts single entity from the doc_info")
    def test_single_entity(self):
        test_data = """
            <!DOCTYPE bookstore [
            <!ENTITY j "l">
            ]>
            """
        result = extract_entities(test_data)
        expected = {"l": "j"}
        assert result == expected

    @mark.it("Extracts single entity from the doc_info whose value contains a space")
    def test_single_space_entity(self):
        test_data = """
            <!DOCTYPE bookstore [
            <!ENTITY j "l m">
            ]>
            """
        result = extract_entities(test_data)
        expected = {"l m": "j"}
        assert result == expected

    @mark.it("Extracts multiple entities from the doc_info")
    def test_multi_entity(self):
        test_data = """
            <!DOCTYPE bookstore [
            <!ENTITY j "l">
            <!ENTITY k "b">
            <!ENTITY company "Matthew inc.">
            ]>
            """
        result = extract_entities(test_data)
        expected = {"l": "j", "b": "k", "Matthew inc.": "company"}
        assert result == expected

    @mark.it("Returns empty dictionary when no entities are defined in the doc_info")
    def test_zero_entity(self):
        test_data = """
            <!DOCTYPE bookstore [
            ]>
            """
        result = extract_entities(test_data)
        expected = {}
        assert result == expected


class Testextract_metadata:
    @mark.it(
        "Metadata fields of the root object are filled according to metadata in the file"
    )
    def test_load_metadata(self):
        test_tree = load_xml_from_file("test_data/weird_metadata/weird_metadata.xml")
        assert test_tree.xml_version == str(22.5)
        assert test_tree.encoding == "happy birthDa9y"


class Testget_next_line:
    @mark.it("Generates non-comment lines")
    def test_non_comment(self):
        f = generate_noncomment_lines("test_data/book_store/bookstore.xml")
        assert next(f) == '<?xml version="1.0" encoding="UTF-8"?>'
        assert next(f) == "<bookstore>"
        assert next(f) == '<book category="cooking">'
        assert next(f) == '<title lang="en">Everyday Italian</title>'
        assert next(f) == "<author>Giada De Laurentiis</author>"
        assert next(f) == "<year>2005</year>"

    @mark.it("Ignores commented lines, including consecutive commented lines")
    def test_comment(self):
        f = generate_noncomment_lines("test_data/comments/comments.xml")
        assert next(f) == '<?xml version="1.0" encoding="UTF-8"?>'
        assert next(f) == "<bookstore>"
        assert next(f) == '<book category="cooking">'
        assert next(f) == '<title lang="en">Everyday Italian</title>'
        assert next(f) == "<author>Giada De Laurentiis</author>"
        assert next(f) == "<year>2005</year>"

    @mark.it("Ignores multi-line comments")
    def test_multiline_comment(self):
        f = generate_noncomment_lines("test_data/comments/minus_a_book.xml")
        assert next(f) == '<?xml version="1.0" encoding="UTF-8"?>'
        assert next(f) == "<bookstore>"
        assert next(f) == '<book category="children">'

    @mark.it("Preserves non-commented data on lines where a comment begins")
    def test_end_line_comments(self):
        f = generate_noncomment_lines("test_data/comments/end_of_line_comment.xml")
        assert next(f) == '<?xml version="1.0" encoding="UTF-8"?>'
        assert next(f) == "<bookstore>"
        assert next(f) == '<book category="cooking">'
        assert next(f) == '<title lang="en">Everyday Italian</title>'
        assert next(f) == "</book>"

    @mark.it("Preserves non-commented data on lines where a comment ends")
    def test_begin_line_comments(self):
        f = generate_noncomment_lines("test_data/comments/end_of_line_comment.xml")
        for _ in range(5):
            next(f)
        assert next(f) == '<book category="web">'
        assert next(f) == '<title lang="en">Learning XML</title>'


class Teststarts_a_new_comment:
    @mark.it("Returns False, None if no open-comment syntax in line")
    def test_1(self):
        test_line = '<book category="children">'
        expected = (False, None)
        result = starts_a_new_comment(test_line)
        assert result == expected

    @mark.it("Returns True, None if entire line is a comment")
    def test_2(self):
        test_line = '<!--<book category="children">-->'
        expected = (True, None)
        result = starts_a_new_comment(test_line)
        assert result == expected

    @mark.it(
        "Returns True with line before comment if usable line appears before the comment begins"
    )
    def test_3(self):
        test_line = '<book category="children"><!--'
        expected = (True, '<book category="children">')
        result = starts_a_new_comment(test_line)
        assert result == expected


class Testends_a_comment:
    @mark.it("Returns False, None if no end-comment syntax in line")
    def test_1(self):
        test_line = '<book category="children">'
        expected = (False, None)
        result = ends_a_comment(test_line)
        assert result == expected

    @mark.it("Returns True, None if entire line is a comment")
    def test_2(self):
        test_line = '<!--<book category="children">-->'
        expected = (True, None)
        result = ends_a_comment(test_line)
        assert result == expected

    @mark.it(
        "Returns True with line after comment if usable line appears after the comment ends"
    )
    def test_3(self):
        test_line = '--><book category="children">'
        expected = (True, '<book category="children">')
        result = ends_a_comment(test_line)
        assert result == expected

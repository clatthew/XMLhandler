from src.xml_element import XMLElement
from re import compile


def get_element_from_line(line: str, entities: dict = {}) -> XMLElement | None:
    """Create an XMLElement object from a line of an XML file.

    Extract the ``tag_name``, ``attributes`` and ``value`` of the XML element contained in line, if line contains a start tag. If line contains only a stop tag, return ``None``.
    
    Arguments:
    ``line`` -- an arbitrary string containing XML syntax.
    ``entities`` -- a dictionary containing user-defined entity references which will be replaced when building the XMLElement.
    """
    non_marker_chars = '[^</>=" ]*'
    value_chars = '[^</>="]*'
    start_pattern = rf'<(?P<tag_name>{non_marker_chars}) ?(?P<attributes>({non_marker_chars}="{non_marker_chars}" ?)*)>$'
    self_closing_pattern = rf"{start_pattern[:-2]}/>$"
    stop_pattern = rf"</{non_marker_chars}>$"
    generic_pattern = rf"{start_pattern[:-2]}/?>(?P<value>{value_chars})?(</\1>)?$"

    if compile(stop_pattern).match(line):
        return None

    tag_name = compile(generic_pattern).match(line).group("tag_name")

    attributes_string = compile(generic_pattern).match(line).group("attributes")
    if attributes_string:
        attribute_list = attributes_string.split(" ")
        attribute_pattern = compile(rf'({non_marker_chars})="({non_marker_chars})"')
        attributes = {}
        for attribute_pair in attribute_list:
            key = attribute_pattern.match(attribute_pair).group(1)
            val = attribute_pattern.match(attribute_pair).group(2)
            val = remove_refs(val, entities)
            attributes[key] = val
    else:
        attributes = None

    if compile(start_pattern).match(line):
        return XMLElement(tag_name, attributes)

    if compile(self_closing_pattern).match(line):
        return XMLElement(tag_name, attributes, value="")

    value = compile(generic_pattern).match(line).group("value")
    value = remove_refs(value)
    return XMLElement(tag_name, attributes, value=value)


def remove_refs(line: str, def_refs: dict = {}) -> str:
    """Restore a string containing XML entity references to the human-readable version.

    Arguments:
    ``line`` -- an arbitrary string containing XML syntax.
    ``def_refs`` -- a dictionary containing entity references defined at the beginning of the XML document (defaults to empty dict).
    """
    predef_refs = {"lt": "<", "gt": ">", "apos": "'", "quot": '"', "amp": "&"}
    refs = def_refs | predef_refs
    for ref in refs:
        dec_ref = f"&{ref};"
        ref_len = len(dec_ref)
        while dec_ref in line:
            index = line.index(dec_ref)
            line = line[:index] + refs[ref] + line[index + ref_len :]
    return line


def extract_entities(doc_info: str) -> dict:
    """Read the document information of an XML file and return a dictionary containing the defined entity references.

    Arguments:
    ``doc_info`` -- the beginning of an XML file containing strings like '<!ENTITY j \"l\">'.
    """
    entity_list = [i for i in doc_info.split("<!") if i[0:6].upper() == "ENTITY"]
    entities = {}
    for element in entity_list:
        val_start = element.index(" ") + 1
        key_start = element.index('"') + 1
        key_end = element.index('"', key_start)
        val = element[val_start : key_start - 2]
        key = element[key_start:key_end]
        entities[key] = val
    return entities


def extract_metadata(preamble: str) -> dict:
    """Return the XML version and encoding protocol defined on the first line of the XML file.

    Arguments:
    ``premble`` -- an arbitrary string containing XML syntax.
    """
    metadata = {}
    for key in ["xml version", "encoding"]:
        key_start = preamble.lower().index(key)
        val_start = preamble.lower().index('"', key_start + len(key)) + 1
        val_end = preamble.lower().index('"', val_start + 1)
        metadata[key] = preamble[val_start:val_end]
    return metadata


def starts_a_new_comment(line: str) -> tuple[bool, str | None]:
    """Return (True, str| None) if line contains characters which mark the beginning of an XML comment.

    Identify whether a line is entirely a comment, partially a commment, or not a comment at all. If the line is partially a comment, return the part of the line before the comment begins as the second part of the return.

    Arguments:
    ``line`` -- an arbitrary string containing XML syntax.
    """
    comment_start_token = "<!--"
    if comment_start_token not in line:
        return False, None
    comment_start_pos = line.index(comment_start_token)
    line_before_comment = line[:comment_start_pos].strip()
    if line_before_comment:
        return True, line_before_comment
    return True, None


def ends_a_comment(line: str) -> tuple[bool, str | None]:
    """Return (True, str| None) if line contains characters which mark the end of an XML comment.

    Identify whether a line is entirely a comment, partially a commment, or not a comment at all. If the line is partially a comment, return the part of the line after the comment ends as the second part of the return.

    Arguments:
    ``line`` -- an arbitrary string containing XML syntax.
    """
    comment_end_token = "-->"
    token_length = len(comment_end_token)
    if comment_end_token not in line:
        return False, None
    comment_end_pos = line.index(comment_end_token)
    line_after_comment = line[comment_end_pos + token_length :].strip()
    if line_after_comment:
        return True, line_after_comment
    return True, None


def generate_noncomment_lines(filepath: str):
    """Return a generator which supplies non-comment information from the XML file.

    Arguments:
    ``filepath`` -- location of the XML file being read"""
    with open(filepath, "r") as f:
        in_comment = False
        line = f.readline()
        while line:
            comment_starts_in_line, line_before_comment = starts_a_new_comment(line)
            if not in_comment:
                if not comment_starts_in_line:
                    yield (line.strip())
                elif line_before_comment:
                    yield line_before_comment
                    in_comment = True
                else:
                    in_comment = True
            elif comment_starts_in_line:
                in_comment = True
            while in_comment:
                comment_ends_in_line, line_after_comment = ends_a_comment(line)
                if comment_ends_in_line:
                    in_comment = False
                    if line_after_comment:
                        yield line_after_comment
                else:
                    line = f.readline()
            line = f.readline()


def load_xml_from_file(filepath: str):
    """Return an XMLElement object containing information described in the XML file at the filepath given.

    Handle exceptions raised by badly formed XML files or files not containing XML content.
    Arguments:
    ``filepath`` -- location of the XML file being read
    """
    try:
        return load_from(filepath)
    except ValueError:
        raise TypeError(f"No parsable XML tree found at {filepath}.")
    except AttributeError:
        raise TypeError(f"No parsable XML tree found at {filepath}.")


def load_from(filepath: str):
    """Return an XMLElement object containing information described in the XML file at the filepath given.

    Arguments:
    ``filepath`` -- location of the XML file being read"""

    f = generate_noncomment_lines(filepath)
    metadata = extract_metadata(next(f))

    line = next(f)
    entities = {}

    if "<!DOCTYPE" in line:
        doc_info = line
        while "]>" not in doc_info:
            doc_info += next(f)
        entities = extract_entities(doc_info)
        line = next(f)

    root_element = get_element_from_line(line.strip(), entities)
    root_element.xml_version = metadata["xml version"]
    root_element.encoding = metadata["encoding"]
    current_parent = root_element
    root_element.add_entity(entities)
    for line in f:
        element = get_element_from_line(line.strip(), entities)
        if element:
            current_parent.add_child(element)
            if element.value is None:
                current_parent = element
        else:
            current_parent = current_parent.parent
    return root_element

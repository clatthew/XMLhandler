from src.xml_element import XMLElement
from re import compile
from typing import TextIO


def get_element_from_line(line: str, entities: dict = {}):
    non_marker_chars = '[^</>=" ]*'
    value_chars = '[^</>="]*'
    start_pattern = rf'<(?P<tag_name>{non_marker_chars}) ?(?P<attributes>({non_marker_chars}="{non_marker_chars}" ?)*)>$'
    self_closing_pattern = rf"{start_pattern[:-2]}/>$"
    stop_pattern = rf"</{non_marker_chars}>$"
    generic_pattern = rf"{start_pattern[:-2]}/?>(?P<value>{value_chars})?(</\1>)?$"
    # print(generic_pattern)
    print(line+"endofline")
    # print(compile(generic_pattern).match(line).group("tag_name"))

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


def remove_refs(line: str, def_refs: dict = {}):
    predef_refs = {"lt": "<", "gt": ">", "apos": "'", "quot": '"', "amp": "&"}
    refs = def_refs | predef_refs
    for ref in refs:
        dec_ref = f"&{ref};"
        ref_len = len(dec_ref)
        while dec_ref in line:
            index = line.index(dec_ref)
            line = line[:index] + refs[ref] + line[index + ref_len :]
    return line


def extract_entities(doc_info: str):
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


def extract_metadata(preamble: str):
    metadata = {}
    for key in ["xml version", "encoding"]:
        key_start = preamble.lower().index(key)
        val_start = preamble.lower().index('"', key_start + len(key)) + 1
        val_end = preamble.lower().index('"', val_start + 1)
        metadata[key] = preamble[val_start:val_end]
    return metadata

def starts_a_new_comment(line: str) -> tuple[bool, str|None]:
    """return True if line contains characters starting the beginning of a comment"""
    comment_start_token = "<!--"
    if comment_start_token not in line:
        return False, None
    comment_start_pos = line.index(comment_start_token)
    line_before_comment = line[:comment_start_pos].strip()
    if line_before_comment:
        return True, line_before_comment
    return True, None

def ends_a_comment(line: str) -> tuple[bool, str|None]:
    comment_end_token = "-->"
    token_length =len(comment_end_token)
    if comment_end_token not in line:
        return False, None
    comment_end_pos = line.index(comment_end_token)
    line_after_comment = line[comment_end_pos + token_length:].strip()
    if line_after_comment:
        return True, line_after_comment
    return True, None

def generate_noncomment_lines(filepath: str):
    with open (filepath, 'r') as f:
        in_comment = False
        line = f.readline()
        while line:
            comment_starts_in_line, line_before_comment = starts_a_new_comment(line)
            if not in_comment:
                if not comment_starts_in_line:
                    yield(line.strip())
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
    """return XMLElement object containing information described in the XML file at filepath"""

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

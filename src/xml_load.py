from src.xml_element import XMLElement
from re import compile


def get_element_from_line(line, entities={}):
    non_marker_chars = "[^</>= ]*"
    value_chars = "[^</>=]*"
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
        attribute_pattern = compile(r'([^"=]*)="([^"=]*)"')
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


def remove_refs(line, def_refs={}):
    predef_refs = {"lt": "<", "gt": ">", "apos": "'", "quot": '"', "amp": "&"}
    refs = def_refs | predef_refs
    for ref in refs:
        dec_ref = f"&{ref};"
        ref_len = len(dec_ref)
        while dec_ref in line:
            index = line.index(dec_ref)
            line = line[:index] + refs[ref] + line[index + ref_len :]
    return line


def extract_entities(doc_info):
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


def extract_metadata(preamble):
    metadata = {}
    for key in ["xml version", "encoding"]:
        key_start = preamble.lower().index(key)
        val_start = preamble.lower().index('"', key_start + len(key)) + 1
        val_end = preamble.lower().index('"', val_start + 1)
        metadata[key] = preamble[val_start:val_end]
    return metadata


def get_next_line(f):
    next_line = f.readline()
    while "<!--" in next_line:
        next_line = f.readline()
    return next_line


def load_xml_from_file(filepath):
    with open(filepath, "r") as f:
        metadata = extract_metadata(f.readline())
        line = get_next_line(f)
        entities = {}
        if "<!DOCTYPE" in line:
            doc_info = line
            while "]>" not in doc_info:
                doc_info += get_next_line(f)
            entities = extract_entities(doc_info)
            line = get_next_line(f)

        root_element = get_element_from_line(line.strip(), entities)
        root_element.xml_version = metadata["xml version"]
        root_element.encoding = metadata["encoding"]
        current_parent = root_element
        root_element.add_entity(entities)
        for line in f:
            element = get_element_from_line(line.strip(), entities)
            if element:
                try:
                    current_parent.add_child(element)
                except:
                    current_parent.add_child(element)
                if element.value is None:
                    current_parent = element
            else:
                current_parent = current_parent.parent
    return root_element

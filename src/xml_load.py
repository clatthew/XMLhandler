from src.xml_element import XMLElement


def get_element_from_line(line, entities={}):
    stop_tag = False
    for i in range(len(line)):
        if line[i] != " ":
            break
    if line[i : i + 2] == "</":
        stop_tag = True
    tag_inner_start = line.index("<") + 1 + stop_tag
    tag_inner_stop = line.index(">")
    tag_inner = line[tag_inner_start:tag_inner_stop]
    if not stop_tag and "/" in tag_inner:
        tag_inner = tag_inner[:-1]
    tag_name = tag_inner.split()[0]

    attributes = None
    if "=" in tag_inner:
        attribute_list = tag_inner.split()[1:]
        attributes = {}
        for attr in attribute_list:
            attr_list = attr.split("=")
            attr_key = attr_list[0]
            attr_val = remove_refs(attr_list[1][1:-1], entities)
            attributes[attr_key] = attr_val

    value = None
    if line.count("<") == 2:
        value_start = line.index(">") + 1
        value_end = line.index("<", tag_inner_start + 1)
        value = line[value_start:value_end]
        value = remove_refs(value, entities)

    if line[tag_inner_stop - 1 : tag_inner_stop + 1] == "/>":
        value = ""

    if not stop_tag:
        return XMLElement(tag_name, attributes, value)


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


def load_xml_from_file(filepath):
    with open(filepath, "r") as f:
        metadata = extract_metadata(f.readline())
        line = f.readline()
        entities = {}
        if "<!DOCTYPE" in line:
            doc_info = line
            while "]>" not in doc_info:
                doc_info += f.readline()
            entities = extract_entities(doc_info)
            line = f.readline()
        root_element = get_element_from_line(line, entities)
        root_element.xml_version = metadata["xml version"]
        root_element.encoding = metadata["encoding"]
        current_parent = root_element
        root_element.add_entity(entities)
        for line in f:
            element = get_element_from_line(line, entities)
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

from src.xml_element import XMLElement


def get_element_from_line(line, entities={}):
    stop_tag = False
    for i in range(len(line)):
        if line[i] != " ":
            break
    if line[i : i + 2] == "</":
        stop_tag = True
    print(f"line:{line}")
    tag_inner_start = line.index("<") + 1 + stop_tag
    tag_inner_stop = line.index(">")
    tag_inner = line[tag_inner_start:tag_inner_stop]
    tag_name = tag_inner.split()[0]
    if not stop_tag and "/" in tag_inner:
        tag_inner = tag_inner[:-1]

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


def load_xml_from_file(filepath):
    with open(filepath, "r") as f:
        preamble = f.readline()
        line = f.readline()
        entities = {}
        if "<!DOCTYPE" in line:
            line = f.readline()
            while "]>" not in line:
                line_list = line.split()
                val = line_list[1]
                key = f"{line_list[2][1:-2]}"
                entities[key] = val
                line = f.readline()

            line = f.readline()
        # root_element = get_element_from_line(f.readline(), entities)
        root_element = get_element_from_line(line, entities)
        current_parent = root_element
        root_element.add_entity(entities)
        # print(f'root element: {root_element}')
        for line in f:
            # print(root_element)
            # print(f'line: {line}')
            element = get_element_from_line(line, entities)
            if element:
                try:
                    current_parent.add_child(element)
                except:
                    # print(element)
                    # print(current_parent)
                    current_parent.add_child(element)
                if element.value is None:
                    # print(f"element has None value: {element}")
                    current_parent = element
            else:
                # print(current_parent)
                current_parent = current_parent.parent
    return root_element

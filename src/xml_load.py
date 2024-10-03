from src.xml_element import XMLElement


def get_element_from_line(line):
    stop_tag = False
    for i in range(len(line)):
        if line[i] != " ":
            break
    if line[i : i + 2] == "</":
        stop_tag = True

    tag_inner_start = line.index("<") + 1 + stop_tag
    tag_inner_stop = line.index(">")
    tag_inner = line[tag_inner_start:tag_inner_stop]
    tag_name = tag_inner.split()[0]
    if not stop_tag and "/" in tag_inner:
        tag_inner = tag_inner[:-1]

    # check if line[tag_inner_stop - 1 : tag_inner_stop + 1] == "/>" for a self-closing tag

    attributes = None
    if "=" in tag_inner:
        attribute_list = tag_inner.split()[1:]
        attributes = {}
        for attr in attribute_list:
            attr_list = attr.split("=")
            attr_key = attr_list[0]
            attr_val = remove_refs(attr_list[1][1:-1])
            attributes[attr_key] = attr_val

    value = None
    if line.count("<") == 2:
        value_start = line.index(">") + 1
        value_end = line.index("<", tag_inner_start + 1)
        value = line[value_start:value_end]
        value = remove_refs(value)

    if line[tag_inner_stop - 1 : tag_inner_stop + 1] == "/>":
        value = ""

    if not stop_tag:
        return XMLElement(tag_name, attributes, value)


def remove_refs(line):
    refs = {"&lt;": "<", "&gt;": ">", "&amp;": "&", "&apos;": "'", "&quot;": '"'}
    for ref in refs:
        ref_len = len(ref)
        while ref in line:
            index = line.index(ref)
            line = line[:index] + refs[ref] + line[index + ref_len :]
    return line


def load_xml_from_file(filepath):
    with open(filepath, "r") as f:
        preamble = f.readline()
        root_element = get_element_from_line(f.readline())
        current_parent = root_element
        for line in f:
            element = get_element_from_line(line)
            if element:
                current_parent.add_child(element)
                if element.value is None:
                    current_parent = element
            else:
                current_parent = current_parent.parent
    return root_element

from json import dumps


class XMLElement:
    predef_entities = {"&": "amp", "<": "lt", ">": "gt", "'": "apos", '"': "quot"}

    def __init__(
        self, tag: str, attributes=None, value=None, encoding=None, xml_version=None
    ):
        self.tag = tag
        self.__attributes = {}
        self.__value = value
        self.children = []
        self.parent = None
        self.root = self
        if attributes:
            self.add_attribute(attributes)
        self.__entities = {}
        self.encoding = encoding
        self.xml_version = xml_version

    @property
    def tag(self):
        return self.__tag

    @tag.setter
    def tag(self, new_val):
        is_valid_name(new_val, "tag name")
        self.__tag = new_val

    @property
    def entities(self):
        return self.__entities.copy()

    def add_entity(self, entity: dict):
        """
        The entity key is its intended value. The entity value is its alias which will &appear; in the XML document.
        """
        if self.is_root:
            try:
                self.__entities |= entity
            except:
                raise TypeError("Entity must be of type dict")
        else:
            raise TypeError("Cannot add entity to non-root element")

    def add_attribute(self, new_attribute: dict):
        for key in new_attribute:
            is_valid_name(key, "attribute key")
        try:
            self.__attributes |= new_attribute
        except:
            raise TypeError("Attribute must be of type dict")

    def remove_attribute(self, key):
        del self.__attributes[key]

    def remove_entity(self, key):
        del self.__entities[key]

    @property
    def is_root(self):
        return self.root is self

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_val):
        if self.children:
            raise ValueError("Cannot add value to an element with children")
        else:
            self.__value = new_val

    @property
    def path(self):
        if self.is_root:
            return []
        else:
            return self.parent.path + [self.parent.children.index(self)]

    def add_child(self, new_child):
        if new_child in self.descendants:
            raise ValueError("cannot add descendant as child")
        if self.value:
            raise ValueError(
                "Cannot add children to an element with a value. Please set value to None."
            )
        self.children.append(new_child)
        new_child.parent = self
        for xmlelt in new_child.descendants:
            xmlelt.root = self.root
            if xmlelt.entities:
                self.add_entity(xmlelt.entities)
            xmlelt.metadata = None

    def make_child(self, tag: str, attributes=None, value=None):
        new_child = XMLElement(tag, attributes, value)
        self.add_child(new_child)

    def add_sibling(self, new_sibling):
        self.parent.add_child(new_sibling)

    def make_sibling(self, tag=None, attributes=None, value=None):
        if not tag:
            tag = self.tag
        new_sibling = XMLElement(tag, attributes, value)
        self.add_sibling(new_sibling)

    @property
    def last_child(self):
        if self.children:
            return self.children[-1]

    @property
    def depth(self):
        if self.parent:
            return 1 + self.parent.depth
        else:
            return 0

    @property
    def is_leaf(self):
        return not self.children

    @property
    def no_children(self):
        return len(self.children)

    @property
    def size(self):
        return len(self.descendants)

    @property
    def attributes(self):
        return self.__attributes.copy()

    def make_xml_tags(self, tab_size, self_closing=True):
        offset = " " * self.depth * tab_size

        if self.is_leaf and self_closing and not self.value:
            return [offset, f"<{self.tag}{self.attribute_string}/>"]

        open_tag = f"<{self.tag}{self.attribute_string}>"

        close_tag = f"</{self.tag}>"

        if self.__value is None:
            val_to_write = None
        else:
            val_to_write = self.insert_entity_refs(str(self.__value))
        return [offset, open_tag, val_to_write, close_tag]

    def to_xml(self, filepath, tab_size=2, self_closing=True):
        if self.xml_version:
            xml_version = self.xml_version
        else:
            xml_version = "1.0"
        if self.encoding:
            encoding = self.encoding
        else:
            encoding = "UTF-8"
        with open(filepath, "w", encoding=encoding) as f:
            f.write(f'<?xml version="{xml_version}" encoding="{encoding}"?>\n')
            if self.root.entities:
                f.write(f"<!DOCTYPE {self.root.tag} [\n")
                for entity in self.root.entities:
                    f.write(f'<!ENTITY {self.root.entities[entity]} "{entity}">\n')
                f.write("]>\n")
            self.write_xml_body(f, tab_size, self_closing)

    def write_xml_body(self, f, tab_size, self_closing):
        if self.is_leaf:
            f.write("".join(self.make_xml_tags(tab_size, self_closing)) + "\n")
        else:
            f.write(
                self.make_xml_tags(tab_size, self_closing)[0]
                + self.make_xml_tags(tab_size, self_closing)[1]
                + "\n"
            )
            for child in self.children:
                child.write_xml_body(f, tab_size, self_closing)
            f.write(
                self.make_xml_tags(tab_size, self_closing)[0]
                + self.make_xml_tags(tab_size, self_closing)[3]
            )
            if not self.is_root:
                f.write("\n")

    def __str__(self):
        output = ""
        for xmlelt in list(self):
            output += xmlelt.print_line()
        return output

    def print_line(self):
        end = "\033[0m"
        underline = "\033[4m"
        output = ""
        if not self.is_root:
            output += "   " * self.parent.depth + "∟"
        output += underline + self.tag + end
        if self.attributes:
            output += f" ({self.attribute_string})"
        if self.__value:
            output += ": " + str(self.__value)
        output += max((60 - len(output)), 5) * " " + str(self.path)
        output += "\n"
        return output

    @property
    def descendants(self):
        descendant_list = [self]
        for child in self.children:
            descendant_list += child.descendants
        return descendant_list

    def __iter__(self):
        yield from self.descendants

    def get_from_path(self, path):
        try:
            if path:
                return self.children[path[0]].get_from_path(path[1:])
            else:
                return self
        except:
            raise IndexError(f"no element found at path {path}")

    def remove_from_path(self, path):
        to_remove = self.get_from_path(path)
        if to_remove.is_root:
            raise IndexError("cannot remove root element")
        parent = self.get_from_path(path[:-1])
        parent.children.remove(to_remove)

    def insert_entity_refs(self, string):
        refs = XMLElement.predef_entities | self.root.entities
        for ref in refs:
            no_to_replace = string.count(ref)
            last_index = 0
            for _ in range(no_to_replace):
                location = string.index(ref, last_index)
                string = (
                    string[:location]
                    + "&"
                    + refs[ref]
                    + ";"
                    + string[location + len(ref) :]
                )
                last_index = location
        return string

    @property
    def attribute_string(self):
        if not self.attributes:
            return ""
        attribute_string = " "
        for key in self.attributes:
            val = self.insert_entity_refs(str(self.attributes[key]))
            attribute_string += f'{key}="{val}" '
        attribute_string = attribute_string[:-1]
        return attribute_string

    @property
    def dict(self):
        self_dict = {
            "attributes": self.attributes,
            "value": self.value,
            "children": [child.dict for child in self.children],
        }
        return {self.tag: self_dict}

    def json(self, indent=2, sort_keys=False):
        return dumps(self.dict, indent=indent, sort_keys=sort_keys)


def is_valid_name(new_name, name_type):
    for ref in list(XMLElement.predef_entities) + [" "]:
        try:
            assert ref not in new_name
        except:
            raise ValueError(f'{name_type.capitalize()} may not contain "{ref}"')

    try:
        assert new_name[0].isalpha() or new_name[0] == "_"
    except:
        raise ValueError(
            f"{name_type.capitalize()} must begin with letter or underscore"
        )

    try:
        assert new_name[0:3].lower() != "xml"
    except:
        raise ValueError(f'{name_type.capitalize()} may not begin with "xml"')

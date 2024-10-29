from json import dumps
from typing import Any, TextIO, Literal


class XMLElement:
    predef_entities = {"&": "amp", "<": "lt", ">": "gt", "'": "apos", '"': "quot"}

    def __init__(
        self,
        tag: str,
        attributes: dict = None,
        value: str = None,
        encoding: str = None,
        xml_version: str = None,
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
    def tag(self, new_val: str):
        """The name displayed inside the XML tags."""
        is_valid_name(new_val, "tag name")
        self.__tag = new_val

    @property
    def entities(self):
        """Return a copy of the dictionary containing the element's user-defined entity references."""
        return self.__entities.copy()

    def add_entity(self, entity: dict):
        """Add the entities suppled in ``entity`` to the element's entities attribute.

        The entity key is its intended value. The entity value is its alias which will &appear; in the XML document.

        Arguments:
        ``entity`` -- a dictionary containing human-readable values as keys and the values which will appear in the XML document as values.
        """
        if self.is_root:
            try:
                self.__entities |= entity
            except:
                raise TypeError("Entity must be of type dict")
        else:
            raise TypeError("Cannot add entity to non-root element")

    @property
    def attributes(self):
        """Return a copy of the dictionary containing the element's ``attributes``."""
        return self.__attributes.copy()

    def add_attribute(self, new_attribute: dict):
        """Add to the ``attributes`` property of the XMLElement.

        Arguments:
        ``new_attribute`` -- dict object containing the new attributes to add to the element.
        """
        for key in new_attribute:
            is_valid_name(key, "attribute key")
        try:
            self.__attributes |= new_attribute
        except:
            raise TypeError("Attribute must be of type dict")

    def remove_attribute(self, key: str):
        """Remove the attribute with the supplied ``key`` from the XMLElement.

        Arguments:
        ``key`` -- the key of the attribute to be removed.
        """
        del self.__attributes[key]

    def remove_entity(self, key: str):
        """Remove the entity with the supplied ``key`` from the XMLElement.

        Arguments:
        ``key`` -- the key of the entity to be removed.
        """
        del self.__entities[key]

    @property
    def is_root(self):
        """Return ``True`` if the XMLElement object is at the root of its tree."""
        return self.root is self

    @property
    def value(self):
        """Return the ``value`` of the XMLElement, which appears between the start and stop tags."""
        return self.__value

    @value.setter
    def value(self, new_val: Any):
        if self.children:
            raise ValueError("Cannot add value to an element with children")
        else:
            self.__value = new_val

    @property
    def path(self) -> list[int]:
        """Return the ``path`` of the element from its root note.

        The path of the root node is [], the path of its first child [0], the path of its second child's third child is [1, 2].
        """
        if self.is_root:
            return []
        else:
            return self.parent.path + [self.parent.children.index(self)]

    def add_child(self, new_child: "XMLElement"):
        """Add a child to the current element.

        Arguments:
        ``new_child`` -- XMLElement to add as child of the current XMLElement.
        """
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

    def make_child(self, tag: str, attributes: dict = None, value: str = None):
        """Create a child and add it to the current XMLElement's children.

        Arguments:
        ``tag`` -- the name to be written inside the new child's tags.
        ``attributes`` -- the attributes beloinging to the new child.
        ``value`` -- the text which will appear between the child's start and stop tags."""
        new_child = XMLElement(tag, attributes, value)
        self.add_child(new_child)

    def add_sibling(self, new_sibling):
        """Add a child to the current element's parent node.

        Arguments:
        ``new_child`` -- XMLElement to add as child of the current XMLElement's parent.
        """
        try:
            self.parent.add_child(new_sibling)
        except AttributeError:
            raise IndexError("Cannot add sibling to element without a parent.")

    def make_sibling(self, tag=None, attributes: dict = None, value: str = None):
        """Create a child and add it to the current XMLElement's parent's children.

        Arguments:
        ``tag`` -- the name to be written inside the new element's tags.
        ``attributes`` -- the attributes beloinging to the new element.
        ``value`` -- the text which will appear between the element's start and stop tags."""
        if not tag:
            tag = self.tag
        new_sibling = XMLElement(tag, attributes, value)
        self.add_sibling(new_sibling)

    @property
    def last_child(self):
        """Return the most recently-added child of the XMLElement object."""
        if self.children:
            return self.children[-1]

    @property
    def depth(self):
        """Return the number of generations of parents which a node has.

        Root node has depth 0, its children have depth 1, etc."""
        if self.parent:
            return 1 + self.parent.depth
        else:
            return 0

    @property
    def is_leaf(self):
        """Return ``True`` if the XMLElement object does not have any children."""
        return not self.children

    @property
    def no_children(self):
        """Return the number of immediate children of the XMLElement."""
        return len(self.children)

    @property
    def size(self):
        """Return the number of elements in the element's XML tree which descend from it, including itself."""
        return len(self.descendants)

    def make_xml_tags(self, tab_size, self_closing=True) -> list[str]:
        """Return the conponents needed to create the XML tags for an XMLElement.

        for all tags, return a list containing
            0. Whitespace to print before the tag begins
            1. the start tag, including any attributes
        for non-self-closing tags, the list will also contain
            2. value to be written between the tags
            3. the stop tag

        Arguments:
        ``tab_size`` -- the size of the indent between each level of the tree
        ``self_closing`` -- changes the way leaf nodes without a value are displayed (defaults to ``True``)"""
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

    def to_xml(self, filepath: str, tab_size: int = 2, self_closing: bool = True):
        """Write the XMLElement tree structure to a well-formed XML file located at ``filepath``.

        Arguments:
        ``filepath`` -- location of the resulting XML file.
        ``tab_size`` -- number of spaces used for each level of indentation.
        ``self_closing`` -- ``True``: use self-closing tags where possible, eg. <matthew/>. ``False``: use start and stop tags for all elements, eg. <matthew></matthew>."""
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

    def write_xml_body(self, f: TextIO, tab_size: int, self_closing: bool):
        """Write the descendants of the XMLElement object to the writable object ``f``.
        
        Arguments:
        ``f`` -- a writable file object.
        ``tab_size`` -- the number of spaces used for each level of indentation (defaults to 2).
        ``self_closing`` -- controls the appearance of leaf tags without values. See ``to_xml`` for example."""
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

    def print_line(self) -> str:
        """Return a string containing the element's information in an easy-to-read format."""
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
        """Return a list containing the XMLElement object and all of the elements below it in the tree."""
        descendant_list = [self]
        for child in self.children:
            descendant_list += child.descendants
        return descendant_list

    def __iter__(self):
        yield from self.descendants

    def get_from_path(self, path: list):
        """Return the XMLElement object located at the ``path`` given.

        Arguments:
        ``path`` -- list containing the ``path`` to the desired element."""
        try:
            if path:
                return self.children[path[0]].get_from_path(path[1:])
            else:
                return self
        except:
            raise IndexError(f"no element found at path {path}")

    def remove_from_path(self, path: str):
        """Remove the XMLElement at the given ``path`` from the tree."""
        to_remove = self.get_from_path(path)
        if to_remove.is_root:
            raise IndexError("cannot remove root element")
        parent = self.get_from_path(path[:-1])
        parent.children.remove(to_remove)

    def insert_entity_refs(self, string: str):
        """Return the given ``string`` with pre-defined and user-defined entities replaced with their entity references.

        Arguments:
        ``string`` -- an arbitrary string which will have its entities replaced."""
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
        """Return a string containing the ``attribute`` portion of the XMLElement's start tag."""
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
        """Return a dictionary version of the element tree including and descending from the XMLElement."""
        self_dict = {
            "attributes": self.attributes,
            "value": self.value,
            "children": [child.dict for child in self.children],
        }
        return {self.tag: self_dict}

    def json(self, indent: int = 2, sort_keys: bool = False):
        """Return a json string of the element tree including and descending from the XMLElement.

        Arguments:
        ``indent`` -- number of spaces used for each level of indentation (defaults to 2).
        ``sort_keys`` -- ``True``: json objects have their keys in alphabetical order. ``False``: json objects have keys in order attributes, value, children (defaults to ``False``)."""
        return dumps(self.dict, indent=indent, sort_keys=sort_keys)


def is_valid_name(
    new_name_candidate: str, name_type: Literal["tag name", "attribute key"]
):
    """Raise a ValueError if the candidate name is not a valid attribute key or tag name.

    Valid names
        - do not contain any of the predefined entities (<>/'"&)
        - begin with a letter or underscore
        - do not begin with the letters XML in upper or lower case.

    Arguments:
    ``new_name_candidate`` -- the name candidate which will be checked for validity.
    ``name_type`` -- tag name or attribute key. Used for formatting error messages."""
    for ref in list(XMLElement.predef_entities) + [" "]:
        try:
            assert ref not in new_name_candidate
        except:
            raise ValueError(f'{name_type.capitalize()} may not contain "{ref}"')

    try:
        assert new_name_candidate[0].isalpha() or new_name_candidate[0] == "_"
    except:
        raise ValueError(
            f"{name_type.capitalize()} must begin with letter or underscore"
        )

    try:
        assert new_name_candidate[0:3].lower() != "xml"
    except:
        raise ValueError(f'{name_type.capitalize()} may not begin with "xml"')

from pickle import dump


class XMLElement:
    def __init__(
        self, tag: str, attribute=None, value=None, parent=None, is_root=False
    ):
        self.tag = tag
        self.attribute = attribute
        self.__value = value
        self.children = []
        self.parent = parent
        self.root = self

    @property
    def is_root(self):
        return self.root is self

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, new_val):
        if self.children:
            raise ValueError('Cannot add value to an element with children')
        else:
            self.__value = new_val

    @property
    def path(self):
        if self.root is self:
            return []
        else:
            return self.parent.path + [self.parent.children.index(self)]

    def add_child(self, new_child):
        if new_child in self.descendants:
            raise ValueError("cannot add descendant as child")
        if self.value:
            raise ValueError("Cannot add children to an element with a value. Please set value to None.")
        self.children.append(new_child)
        new_child.parent = self
        # new_child.is_root = False
        for xmlelt in new_child.descendants:
            xmlelt.root = self.root

    def make_child(self, tag: str, attribute=None, value=None):
        new_child = XMLElement(tag, attribute, value)
        self.add_child(new_child)

    def add_sibling(self, new_sibling):
        self.parent.add_child(new_sibling)

    def make_sibling(self, tag=None, attribute=None, value=None):
        if not tag:
            tag = self.tag
        new_sibling = XMLElement(tag, attribute, value)
        self.add_sibling(new_sibling)

    def to_pickle(self, filepath=None):
        if not filepath:
            filepath = f"{self.tag}.pkl"
        with open(filepath, "wb") as f:
            dump(self, f)

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
    def no_children(self):
        return len(self.children)

    @property
    def size(self):
        return len(self.descendants)

    def make_xml_tags(self):
        if self.attribute:
            open_tag = f'<{self.tag} {self.attribute[0]}="{self.attribute[1]}">'
        else:
            open_tag = f"<{self.tag}>"
        close_tag = f"</{self.tag}>"
        offset = "  " * self.depth
        if self.__value is None:
            val_to_write = None
        else:
            val_to_write = str(self.__value)
        return [offset, open_tag, val_to_write, close_tag]

    def to_xml(self, filepath):
        f = open(filepath, "w")
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.write_xml_body(f)

        f.close()

    def write_xml_body(self, f):
        if self.children:
            f.write(self.make_xml_tags()[0] + self.make_xml_tags()[1] + "\n")
            for child in self.children:
                child.write_xml_body(f)
            f.write(self.make_xml_tags()[0] + self.make_xml_tags()[3])
            if not self.is_root:
                f.write("\n")
        else:
            f.write("".join(self.make_xml_tags()) + "\n")

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
        if self.attribute:
            output += f' ({self.attribute[0]}="{self.attribute[1]}")'
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

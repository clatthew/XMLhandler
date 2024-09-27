from pickle import dump


class XMLElement:
    def __init__(
        self, tag: str, attribute=None, value=None, parent=None, is_root=False
    ):
        self.tag = tag
        self.attribute = attribute
        self.value = value
        self.is_root = is_root
        self.children = []
        self.parent = parent
        if self.is_root:
            self.root = self

    def add_child(self, new_child):
        if new_child is self:
            raise ValueError("cannot add self as child")
        new_child.parent = self
        new_child.is_root = False
        for xmlelt in new_child.descendants:
            xmlelt.root = self.root
        self.children.append(new_child)

    def make_child(self, tag: str, attribute=None, value=None):
        new_child = XMLElement(tag, attribute, value)
        self.add_child(new_child)

    def make_sibling(self, tag=None, attribute=None, value=None):
        if not tag:
            tag = self.tag
        new_sibling = XMLElement(tag, attribute, value)
        self.parent.add_child(new_sibling)

    def to_pickle(self, filepath=None):
        if not filepath:
            filepath = self.tag
        with open(f"{filepath}.pkl", "wb") as f:
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

    @property
    def descendants(self):
        descendant_list = [self]
        for child in self.children:
            descendant_list += child.descendants
        return descendant_list

    def __iter__(self):
        yield from self.descendants

    # def descendants(self):
    #     iterator = XMLIterator(self)
    #     return iterator

    # def __iter__(self):
    #     return XMLIterator(self)


# class XMLIterator:
#     def __init__(self, iterable):
#         self.iterable = iterable

#     def __iter__(self):
#         return self
    
#     def __next__(self):
#         yield self.iterable
#         for child in self.iterable.children:
#             yield iter(child)
        
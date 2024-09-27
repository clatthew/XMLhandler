from pickle import dump 
class XMLElement:
    def __init__(self, tag : str, attribute=None, value=None, parent=None, root=False):
        self.tag = tag
        self.attribute = attribute
        self.value = value
        self.root = root
        self.children = []
        self.parent = parent

    def add_child(self, new_child):
        new_child.parent = self
        new_child.root = False
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
        with open (f'{filepath}.pkl', 'wb') as f:
            dump(self, f)

    @property
    def last_child(self):
        if self.children:
            return self.children[-1]
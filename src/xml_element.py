class XMLElement:
    def __init__(self, attribute=None, value=None, parent=None, root=False):
        self.attribute = attribute
        self.value = value
        self.root = root
        self.children = []
        self.parent = parent

    def add_child(self, attribute=None, value=None):
        child = XMLElement(attribute, value, parent=self)
        self.children.append(child)

    def add_sibling(self, attribute=None, value=None):
        self.parent.add_child(attribute, value)

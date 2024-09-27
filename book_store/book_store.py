from src.xml_element import XMLElement
# from pickle import load
def build_bookstore_file(filetype):
    root_element = XMLElement("bookstore", is_root=True)
    root_element.make_child('book', ('category', 'cooking'))
    root_element.last_child.make_child('title', ('lang','en'), 'Everyday Italian')
    root_element.last_child.make_child('author', value="Giada De Laurentiis")
    root_element.last_child.make_child('year', value=2005)
    root_element.last_child.make_child('price', value=30)
    root_element.make_child('book', ('category', 'children'))
    root_element.last_child.make_child('title', ('lang','en'), 'Harry Potter')
    root_element.last_child.make_child('author', value="J K. Rowling")
    root_element.last_child.make_child('year', value=2005)
    root_element.last_child.make_child('price', value=29.99)
    root_element.make_child('book', ('category', 'web'))
    root_element.last_child.make_child('title', ('lang','en'), 'Learning XML')
    root_element.last_child.make_child('author', value="Erik T. Ray")
    root_element.last_child.make_child('year', value=2003)
    root_element.last_child.make_child('price', value=39.95)
    # print(loaded_tree.tag, [child.value for child in loaded_tree.children[0].children])
    if filetype == 'xml':
        root_element.to_xml('book_store/bookstore_export.xml')
    if filetype == 'pkl':
        root_element.to_pickle('book_store/bookstore.pkl')
    return root_element

if __name__ == "__main__":
    tree = build_bookstore_file()
    print(tree)
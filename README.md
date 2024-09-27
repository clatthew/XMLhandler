# XMLhndlr
> by clatthew
## To do: initial features
### XML structure ✅
- tree structure ✅
- all XML attributes, tags, etc ✅

### dict
- convert XML structure to python dict
- option to exclude tags to make dict more compact

### save and load objects ✅
- save internal XML structure to pickle ✅
- open from pickle ✅

### edit file ✴️ 
- add children ✅
- add siblings ✅
- edit attributes and values
- preview tree structure in the terminal ✅
- remove items ✅

### load from XML file
- load data and structure from XML file into the object structure

### dump to XML file ✴️
- dump object structure into a well-formed XML file ✅
- **still to do:** properly handle characters < > & ' "

## XML file structure
> notes from [w3schools](https://www.w3schools.com/xml/)
- first line: `<?xml version="1.0" encoding="UTF-8"?>`
- Root element: name
- middle elemenets: (optional) sttribute (inside tag, eg. `<book category="cooking">`). must be in quotes
- lead elements: (optional) category inside tag, text between open tag and close tag.
- elements start with `<open_tag>` and end with `</close_tag>`
- all text is stored as plain text in the file. In python, a decision would have to be made about data types.
```xml
<?xml version="1.0" encoding="UTF-8"?>
<bookstore>
  <book category="cooking">
    <title lang="en">Everyday Italian</title>
    <author>Giada De Laurentiis</author>
    <year>2005</year>
    <price>30.00</price>
  </book>
  <book category="children">
    <title lang="en">Harry Potter</title>
    <author>J K. Rowling</author>
    <year>2005</year>
    <price>29.99</price>
  </book>
  <book category="web">
    <title lang="en">Learning XML</title>
    <author>Erik T. Ray</author>
    <year>2003</year>
    <price>39.95</price>
  </book>
</bookstore> 
```

### Entity references
The following symbols cannot be used in XML content. The following entity references must be used instead.

entity reference | unicode symbol | name
-|-|-
`&lt;` | < | less than
`&gt;` | > | greater than
`&amp;` | & | ampersand
`apos;` | ' | apostrophe
`&quot;` | " | quotation mark
`LF` | | new line

### Comments
Comments will be ignored when creating the XML object model
```xml
<!-- This is a commment -->
```
### Empty elements
`<element></element>` and `<element />` are equivalent. Empty elements can have attributes.

### Naming rules
XML elements must follow these naming rules:
- Element names are case-sensitive
- Element names must start with a letter or underscore
- Element names cannot start with the letters xml (or XML, or Xml, etc)
- Element names can contain letters, digits, hyphens, underscores, and periods
- Element names cannot contain spaces

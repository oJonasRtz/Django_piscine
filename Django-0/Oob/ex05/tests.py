from elements import *
from elem import Elem, Text

COLORS = {
	"reset": "\033[0m",
	"green": "\033[32m",
	"red": "\033[31m",
	"yellow": "\033[33m",
	"blue": "\033[34m"
}

def log(msg, color="reset"):
	print(f"{COLORS[color]}{msg}{COLORS['reset']}")


ALL_TAG_CLASSES = [
	Html, Head, Body, Title, Meta, Img, Table, Tr, Th, Td,
	Ul, Ol, Li, H1, H2, P, Div, Span, Hr, Br
]

DOUBLE_TAG_CLASSES = [cls for cls in ALL_TAG_CLASSES if cls().tag_type == 'double']
SIMPLE_TAG_CLASSES = [cls for cls in ALL_TAG_CLASSES if cls().tag_type == 'simple']

def test(name, func):
	try:
		func()
		log(f"[PASS] {name}", "green")
		return True
	except AssertionError as e:
		log(f"[FAIL] {name}", "red")
		log(f"  -> {e}", "yellow")
		return False
	except Exception as e:
		log(f"[ERROR] {name}", "red")
		log(f"  -> Unexpected error: {e}", "yellow")
		return False
	

# -- TESTS --
def test_inheritance():
	for cls in ALL_TAG_CLASSES:
		assert isinstance(cls(), Elem), f"{cls.__name__} should be a subclass of Elem"

def test_empty_tags():
	for cls in DOUBLE_TAG_CLASSES:
		tag = cls().tag
		expected = f'<{tag}></{tag}>'
		assert str(cls()) == expected, f"{cls.__name__} should render as {expected}"

	for cls in SIMPLE_TAG_CLASSES:
		tag = cls().tag
		expected = f'<{tag} />'
		assert str(cls()) == expected, f"{cls.__name__} should render as {expected}"
 
def test_nesting_all_tags_as_parents():
	for cls in DOUBLE_TAG_CLASSES:
		parent = cls(Span(Text("inside")))
		tag = cls().tag
		expected = (
			f'<{tag}>\n'
			'  <span>\n'
			'    inside\n'
			'  </span>\n'
			f'</{tag}>'
		)
		assert str(parent) == expected, (
			f"{cls.__name__} nesting failed. Expected {expected}, got {str(parent)}"
		)


def test_nesting_all_tags_as_children():
	for cls in ALL_TAG_CLASSES:
		child = cls(attr={"id": "child"})
		parent = Div([child])
		child_render = str(child)
		expected = f'<div>\n  {child_render}\n</div>'
		assert str(parent) == expected, (
			f"{cls.__name__} as child nesting failed. Expected {expected}, got {str(parent)}"
		)

def test_content_all_double_tags():
	for cls in DOUBLE_TAG_CLASSES:
		elem = cls(Text("My Title"))
		tag = cls().tag
		expected = f'<{tag}>\n  My Title\n</{tag}>'
		assert str(elem) == expected, f"{cls.__name__} content failed. Expected {expected}, got {str(elem)}"

def test_attributes_all_tags():
	attrs = {"id": "node", "class": "primary"}

	for cls in DOUBLE_TAG_CLASSES:
		tag = cls().tag
		elem = cls(attr=attrs)
		expected = f'<{tag} class="primary" id="node"></{tag}>'
		assert str(elem) == expected, (
			f"{cls.__name__} attributes failed. Expected {expected}, got {str(elem)}"
		)

	for cls in SIMPLE_TAG_CLASSES:
		tag = cls().tag
		elem = cls(attr=attrs)
		expected = f'<{tag} class="primary" id="node" />'
		assert str(elem) == expected, (
			f"{cls.__name__} attributes failed. Expected {expected}, got {str(elem)}"
		)

def test_self_closing():
    assert str(Br()) == '<br />', "Br should render as <br />"
    assert str(Hr()) == '<hr />', "Hr should render as <hr />"

def test_list_content():
    ul = Ul([
		Li(Text("A")),
		Li(Text("B")),
	])
    expected = '<ul>\n  <li>\n    A\n  </li>\n  <li>\n    B\n  </li>\n</ul>'
    assert str(ul) == expected, f"Expected {expected}, got {str(ul)}"
    
def test_full_document():
    doc = Html([
        Head([
            Title(Text('"Hello ground!"'))
        ]),
        Body([
            H1(Text('"Oh no, not again!"')),
            Img(attr={"src": "http://i.imgur.com/pfp3T.jpg"})
        ])
    ])

    expected = (
        "<html>\n"
        "  <head>\n"
        "    <title>\n"
        "      &quot;Hello ground!&quot;\n"
        "    </title>\n"
        "  </head>\n"
        "  <body>\n"
        "    <h1>\n"
        "      &quot;Oh no, not again!&quot;\n"
        "    </h1>\n"
        "    <img src=\"http://i.imgur.com/pfp3T.jpg\" />\n"
        "  </body>\n"
        "</html>"
    )

    assert str(doc) == expected, f"Expected:\n{expected}\nGot:\n{str(doc)}"
    
# -- RUN TESTS --
def run_tests():
	log("=== RUNNING TESTS ===", "blue")
	
	#tests = [
	#	("Test description", test_function),
	#]
	tests = [
		('Inheritance test', test_inheritance),
		('Empty tags test', test_empty_tags),
		('Nesting parents test', test_nesting_all_tags_as_parents),
		('Nesting children test', test_nesting_all_tags_as_children),
		('Text content all tags test', test_content_all_double_tags),
		('Attributes all tags test', test_attributes_all_tags),
		('Self-closing test', test_self_closing),
		('List content test', test_list_content),
		('Full document test', test_full_document)
	]
	passed = 0
	
	for name, fun in tests:
		if test(name, fun):
			passed += 1
	
	#print results
	total = len(tests)
	print()
	if passed == total:
		log(f"All {total} tests passed!", "green")
		return
	log(f"{passed}/{total} tests passed.", "red")

if __name__ == "__main__":
	run_tests()
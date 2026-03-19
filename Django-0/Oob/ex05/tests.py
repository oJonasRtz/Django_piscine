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
	assert isinstance(Html(), Elem), "Html should be a subclass of Elem"
	assert isinstance(Body(), Elem), "Body should be a subclass of Elem"
	assert isinstance(Br(), Elem), "Br should be a subclass of Elem"
	assert isinstance(Hr(), Elem), "Hr should be a subclass of Elem"
	assert isinstance(Head(), Elem), "Head should be a subclass of Elem"
	assert isinstance(Title(), Elem), "Title should be a subclass of Elem"
	assert isinstance(Meta(), Elem), "Meta should be a subclass of Elem"
	assert isinstance(Img(), Elem), "Img should be a subclass of Elem"
	assert isinstance(Table(), Elem), "Table should be a subclass of Elem"
	assert isinstance(Tr(), Elem), "Tr should be a subclass of Elem"
	assert isinstance(Th(), Elem), "Th should be a subclass of Elem"
	assert isinstance(Td(), Elem), "Td should be a subclass of Elem"
	assert isinstance(Ul(), Elem), "Ul should be a subclass of Elem"
	assert isinstance(Ol(), Elem), "Ol should be a subclass of Elem"
	assert isinstance(Li(), Elem), "Li should be a subclass of Elem"
	assert isinstance(H1(), Elem), "H1 should be a subclass of Elem"
	assert isinstance(H2(), Elem), "H2 should be a subclass of Elem"
	assert isinstance(P(), Elem), "P should be a subclass ofElem"

def test_empty_tags():
	assert str(Html()) == '<html></html>',  "Html should render as <html></html>"
	assert str(Body()) == '<body></body>',  "Body should render as <body></body>"
	assert str(Br()) == '<br />',  "Br should render as <br />"
	assert str(Hr()) == '<hr />',  "Hr should render as <hr />"
	assert str(Head()) == '<head></head>',  "Head should render as <head></head>"
	assert str(Title()) == '<title></title>',  "Title should render as <title></title>"
	assert str(Meta()) == '<meta />',  "Meta should render as <meta />"
	assert str(Img()) == '<img />',  "Img should render as <img />"
	assert str(Table()) == '<table></table>',  "Table should render as <table></table>"
	assert str(Tr()) == '<tr></tr>',  "Tr should render as <tr></tr>"
	assert str(Th()) == '<th></th>',  "Th should render as <th></th>"
	assert str(Td()) == '<td></td>',  "Td should render as <td></td>"
	assert str(Ul()) == '<ul></ul>',  "Ul should render as <ul></ul>"
	assert str(Ol()) == '<ol></ol>',  "Ol should render as <ol></ol>"
	assert str(Li()) == '<li></li>',  "Li should render as <li></li>"
	assert str(H1()) == '<h1></h1>',  "H1 should render as <h1></h1>"
	assert str(H2()) == '<h2></h2>',  "H2 should render as <h2></h2>"
	assert str(P()) == '<p></p>',  "P should render as <p></p>"
 
def test_nesting():
    doc = Html([Head(), Body()])
    expected = '<html>\n  <head></head>\n  <body></body>\n</html>'
    assert str(doc) == expected, f"Expected {expected}, got {str(doc)}"

def test_text_content():
    title = Title(Text("My Title"))
    expected = '<title>\n  My Title\n</title>'
    assert str(title) == expected, f"Expected {expected}, got {str(title)}"

def test_attributes():
	img = Img(attr={"src": "image.png", "alt": "An image"})
	expected = '<img alt="An image" src="image.png" />'
	assert str(img) == expected, f"Expected {expected}, got {str(img)}"

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
		('Nesting test', test_nesting),
		('Text content test', test_text_content),
		('Attributes test', test_attributes),
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
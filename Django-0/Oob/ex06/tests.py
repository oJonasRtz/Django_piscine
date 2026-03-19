import os

from Page import Page
from elem import Elem, Text
from elements import *

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
def assert_valid(root, msg="Expected valid tree"):
	assert Page(root).is_valid() is True, msg


def assert_invalid(root, msg="Expected invalid tree"):
	assert Page(root).is_valid() is False, msg


def make_valid_doc():
	return Html([
		Head(Title(Text("Title"))),
		Body([
			H1(Text("H1")),
			Div([
				H2(Text("H2")),
				Span([Text("inline"), P(Text("p in span"))]),
				Text("body text"),
				Table([
					Tr([Th(Text("A")), Th(Text("B"))]),
					Tr([Th(Text("C")), Th(Text("D"))]),
				]),
				Ul([Li(Text("one")), Li(Text("two"))]),
				Ol([Li(Text("alpha"))]),
			])
		])
	])


def test_constructor_rejects_non_elem_root():
	raised = False
	try:
		Page("not an element")
	except Exception:
		raised = True
	assert raised, "Page constructor should reject roots that are not Elem subclasses"


def test_valid_document_tree():
	assert_valid(make_valid_doc(), "Reference valid tree should pass")


def test_unknown_node_type_is_invalid():
	class Custom(Elem):
		def __init__(self, content=None, attr={}):
			super().__init__(tag='custom', attr=attr, content=content, tag_type='double')

	bad = Html([
		Head(Title(Text("Title"))),
		Body(Div(Custom(Text("x"))))
	])
	assert_invalid(bad, "Unknown type in tree should make the page invalid")


def test_html_must_contain_head_then_body_only():
	assert_invalid(Html([Body(), Head()]), "Html must contain Head then Body in this order")
	assert_invalid(Html([Head()]), "Html with missing Body must be invalid")
	assert_invalid(Html([Head(), Body(), Div()]), "Html must not contain extra nodes")
	assert_valid(Html([Head([Title(Text("Title"))]), Body()]), "Html with correct structure should be valid")

def test_head_must_contain_exactly_one_title():
	assert_invalid(Html([Head(), Body()]), "Head without Title should be invalid")
	assert_invalid(Html([Head([Title(), Title()]), Body()]), "Head with two Title tags should be invalid")
	assert_valid(Html([Head([Title(), Meta()]), Body()]), "Head must only contain one Title")


def test_body_child_constraints():
	ok_body = Body([H1(Text("ok")), H2(Text("ok")), Div(), Table(), Ul([Li(Text("x"))]), Ol([Li(Text("y"))]), Span(Text("z")), Text("plain")])
	assert_valid(Html([Head(Title(Text("T"))), ok_body]), "Body should accept only allowed children")

	bad_body = Body([P(Text("no"))])
	assert_invalid(Html([Head(Title(Text("T"))), bad_body]), "Body should reject disallowed children")


def test_div_child_constraints():
	ok_div = Div([H1(Text("ok")), H2(Text("ok")), Div(), Table(), Ul([Li(Text("x"))]), Ol([Li(Text("y"))]), Span(Text("z")), Text("plain")])
	assert_valid(Html([Head(Title(Text("T"))), Body(ok_div)]), "Div should accept only allowed children")

	bad_div = Div([Li(Text("no"))])
	assert_invalid(Html([Head(Title(Text("T"))), Body(bad_div)]), "Div should reject disallowed children")


def test_title_h1_h2_li_th_td_must_contain_exactly_one_text():
	title_many = Html([Head(Title([Text("a"), Text("b")])), Body(H1(Text("ok")))])
	assert_invalid(title_many, "Title must contain exactly one Text")

	h1_bad = Html([Head(Title(Text("ok"))), Body(H1(Span(Text("no"))))])
	h2_bad = Html([Head(Title(Text("ok"))), Body(H2([Text("a"), Text("b")]))])
	li_bad = Html([Head(Title(Text("ok"))), Body(Ul([Li(Span(Text("no")))]))])
	th_bad = Html([Head(Title(Text("ok"))), Body(Table([Tr([Th(Span(Text("no")))])]))])
	td_bad = Html([Head(Title(Text("ok"))), Body(Table([Tr([Td([Text("a"), Text("b")])])]))])

	assert_invalid(h1_bad, "H1 must contain exactly one Text")
	assert_invalid(h2_bad, "H2 must contain exactly one Text")
	assert_invalid(li_bad, "Li must contain exactly one Text")
	assert_invalid(th_bad, "Th must contain exactly one Text")
	assert_invalid(td_bad, "Td must contain exactly one Text")


def test_p_must_only_contain_text():
	assert_valid(Html([Head(Title(Text("ok"))), Body(Div(P([Text("a"), Text("b")])))]), "P containing only Text should be valid")
	assert_invalid(Html([Head(Title(Text("ok"))), Body(Div(P(Span(Text("x")))))]), "P containing an Elem should be invalid")


def test_span_must_only_contain_text_or_p():
	ok = Html([Head(Title(Text("ok"))), Body(Div(Span([Text("a"), P(Text("b"))])))])
	bad = Html([Head(Title(Text("ok"))), Body(Div(Span(H1(Text("no")))))])
	assert_valid(ok, "Span containing only Text or P should be valid")
	assert_invalid(bad, "Span containing disallowed child should be invalid")


def test_ul_and_ol_rules():
	assert_valid(Html([Head(Title(Text("ok"))), Body(Div(Ul([Li(Text("one"))])))]), "Ul with Li children should be valid")
	assert_valid(Html([Head(Title(Text("ok"))), Body(Div(Ol([Li(Text("one")), Li(Text("two"))])))]), "Ol with Li children should be valid")

	assert_invalid(Html([Head(Title(Text("ok"))), Body(Div(Ul()))]), "Ul must contain at least one Li")
	assert_invalid(Html([Head(Title(Text("ok"))), Body(Div(Ol([Li(Text("one")), Span(Text("no"))])))]), "Ol must contain only Li")


def test_tr_rules_and_mutual_exclusion_of_th_td():
	ok_th = Html([Head(Title(Text("ok"))), Body(Table([Tr([Th(Text("a")), Th(Text("b"))])]))])
	ok_td = Html([Head(Title(Text("ok"))), Body(Table([Tr([Td(Text("a")), Td(Text("b"))])]))])
	empty_tr = Html([Head(Title(Text("ok"))), Body(Table([Tr()]))])
	mixed_tr = Html([Head(Title(Text("ok"))), Body(Table([Tr([Th(Text("a")), Td(Text("b"))])]))])
	wrong_tr = Html([Head(Title(Text("ok"))), Body(Table([Tr([Li(Text("x"))])]))])

	assert_valid(ok_th, "Tr with only Th should be valid")
	assert_valid(ok_td, "Tr with only Td should be valid")
	assert_invalid(empty_tr, "Tr must contain at least one Th or Td")
	assert_invalid(mixed_tr, "Tr cannot mix Th and Td")
	assert_invalid(wrong_tr, "Tr must contain only Th or only Td")


def test_table_must_contain_only_tr():
	ok = Html([Head(Title(Text("ok"))), Body(Table([Tr([Td(Text("1"))]), Tr([Td(Text("2"))])]))])
	bad = Html([Head(Title(Text("ok"))), Body(Table([Tr([Td(Text("1"))]), Div()]))])
	assert_valid(ok, "Table with only Tr children should be valid")
	assert_invalid(bad, "Table containing non-Tr child should be invalid")


def test_str_prepends_doctype_only_for_html_root():
	html_page = Page(make_valid_doc())
	non_html_page = Page(Div(Text("x")))

	html_str = str(html_page)
	non_html_str = str(non_html_page)

	assert html_str.startswith("<!DOCTYPE html>\n"), "Html root output must start with doctype"
	assert not non_html_str.startswith("<!DOCTYPE html>"), "Non-html root output must not start with doctype"


def test_write_to_file_prepends_doctype_only_for_html_root():
	html_path = "./_tmp_page_html.html"
	non_html_path = "./_tmp_page_non_html.html"

	try:
		Page(make_valid_doc()).write_to_file(html_path)
		Page(Div(Text("x"))).write_to_file(non_html_path)

		with open(html_path, "r", encoding="utf-8") as f:
			html_data = f.read()
		with open(non_html_path, "r", encoding="utf-8") as f:
			non_html_data = f.read()

		assert html_data.startswith("<!DOCTYPE html>\n"), "Html file output must include doctype"
		assert not non_html_data.startswith("<!DOCTYPE html>"), "Non-html file output must not include doctype"
	finally:
		if os.path.exists(html_path):
			os.remove(html_path)
		if os.path.exists(non_html_path):
			os.remove(non_html_path)

# -- RUN TESTS --
def run_tests():
	log("=== RUNNING TESTS ===", "blue")
	
	#tests = [
	#	("Test description", test_function),
	#]
	tests = [
		('Constructor rejects non-Elem root', test_constructor_rejects_non_elem_root),
		('Valid document tree', test_valid_document_tree),
		('Unknown node type invalid', test_unknown_node_type_is_invalid),
		('Html order and shape', test_html_must_contain_head_then_body_only),
		('Head exact Title', test_head_must_contain_exactly_one_title),
		('Body child constraints', test_body_child_constraints),
		('Div child constraints', test_div_child_constraints),
		('Single Text constraints', test_title_h1_h2_li_th_td_must_contain_exactly_one_text),
		('P only Text', test_p_must_only_contain_text),
		('Span only Text or P', test_span_must_only_contain_text_or_p),
		('Ul and Ol rules', test_ul_and_ol_rules),
		('Tr rules and mutual exclusivity', test_tr_rules_and_mutual_exclusion_of_th_td),
		('Table only Tr', test_table_must_contain_only_tr),
		('String doctype behavior', test_str_prepends_doctype_only_for_html_root),
		('File doctype behavior', test_write_to_file_prepends_doctype_only_for_html_root),
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
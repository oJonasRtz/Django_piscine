import os
import ast
import inspect
import textwrap

from Page import Page
from elem import Elem, Text
from elements import *

COLORS = {
	"reset": "\033[0m",
	"green": "\033[32m",
	"red": "\033[31m",
	"yellow": "\033[33m",
	"blue": "\033[34m",
	"magenta": "\033[35m"
}

def log(msg, color="reset"):
	print(f"{COLORS[color]}{msg}{COLORS['reset']}")


ASSERT_COUNTER = {
	"executed": 0,
	"passed": 0,
}


def _reset_assert_counter():
	ASSERT_COUNTER["executed"] = 0
	ASSERT_COUNTER["passed"] = 0


def _count_expected_asserts(func):
	source = textwrap.dedent(inspect.getsource(func))
	tree = ast.parse(source)
	total = 0

	for node in ast.walk(tree):
		if isinstance(node, ast.Assert):
			total += 1
		elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
			if node.func.id in {"check", "assert_valid", "assert_invalid"}:
				total += 1

	return total


def check(condition, msg="Assertion failed"):
	ASSERT_COUNTER["executed"] += 1
	if condition:
		ASSERT_COUNTER["passed"] += 1
		return
	raise AssertionError(msg)

def test(name, func):
	_reset_assert_counter()
	try:
		func()
		log(f"[PASS] {name} [{ASSERT_COUNTER['passed']}/{ASSERT_COUNTER['executed']}]", "green")
		return True
	except AssertionError as e:
		log(f"[FAIL] {name} [{ASSERT_COUNTER['passed']}/{ASSERT_COUNTER['executed']}]", "red")
		log(f"  -> {e}", "yellow")
		return False
	except Exception as e:
		log(f"[ERROR] {name} [{ASSERT_COUNTER['passed']}/{ASSERT_COUNTER['executed']}]", "red")
		log(f"  -> Unexpected error: {e}", "yellow")
		return False
	

# -- TESTS --
def assert_valid(root, msg="Expected valid tree"):
	check(Page(root).is_valid() is True, msg)


def assert_invalid(root, msg="Expected invalid tree"):
	check(Page(root).is_valid() is False, msg)


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
	invalid_roots = [
		None,
		"not an element",
		123,
		3.14,
		True,
		[],
		{},
		Text("plain text"),
		object(),
	]

	for root in invalid_roots:
		raised_type_error = False
		try:
			Page(root)
		except TypeError:
			raised_type_error = True
		except Exception as e:
			raise AssertionError(
				f"Expected TypeError for {type(root).__name__}, got {type(e).__name__}"
			)

		check(
			raised_type_error,
			f"Page constructor should reject {type(root).__name__} as non-Elem root"
		)

	valid_page = None
	try:
		valid_page = Page(Div(Text("ok")))
	except Exception as e:
		raise AssertionError(
			f"Page constructor should accept Elem root, got {type(e).__name__}"
		)

	check(isinstance(valid_page.root, Elem), "Valid Elem root should be accepted")


def test_valid_document_tree():
	assert_valid(make_valid_doc(), "Reference valid tree should pass")


def test_unknown_node_type_is_invalid():
	class Custom(Elem):
		def __init__(self, content=None, attr={}):
			super().__init__(tag='custom', attr=attr, content=content, tag_type='double')

	bad_custom_class = Html([
		Head(Title(Text("Title"))),
		Body(Div(Custom(Text("x"))))
	])
	assert_invalid(bad_custom_class, "Unknown type in tree should make the page invalid")

	bad_custom_tag = Html([
		Head(Title(Text("Title"))),
		Body(Div(Elem(tag='custom_tag', content=Text("x"), tag_type='double')))
	])
	assert_invalid(bad_custom_tag, "Unknown string tag should make the page invalid")

	bad_int_tag = Html([
		Head(Title(Text("Title"))),
		Body(Div(Elem(tag=123, content=Text("x"), tag_type='double')))
	])
	assert_invalid(bad_int_tag, "Non-string/basic numeric tag should make the page invalid")

	raised_invalid_content = False
	try:
		Html([
			Head(Title(Text("Title"))),
			Body(Div(Elem(tag='span', content=123, tag_type='double')))
		])
	except Elem.ValidationError:
		raised_invalid_content = True

	check(raised_invalid_content, "Basic type in content (int) should be rejected")


def test_html_must_contain_head_then_body_only():
	assert_invalid(Html([Body(), Head()]), "Html must contain Head then Body in this order")
	assert_invalid(Html([Head()]), "Html with missing Body must be invalid")
	assert_invalid(Html([Head(), Body(), Div()]), "Html must not contain extra nodes")
	assert_valid(Html([Head([Title(Text("Title"))]), Body()]), "Html with correct structure should be valid")

def test_head_must_contain_exactly_one_title():
	assert_invalid(Html([Head(), Body()]), "Head without Title should be invalid")
	assert_invalid(Html([Head([Title([Text("A")]), Title([Text("B")])]), Body()]), "Head with two Title tags should be invalid")
	assert_valid(Html([Head([Title([Text("Title")]), Meta()]), Body()]), "Head must only contain one Title")


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
	assert_valid(Html([Head(Title(Text("ok"))), Body(Span(P(Text("inside"))))]), "P containing only one Text should be valid")
	assert_valid(Html([Head(Title(Text("ok"))), Body(Span(P([Text("a"), Text("b")])))]), "P containing multiple Text should be valid")
	assert_invalid(Html([Head(Title(Text("ok"))), Body(Span(P(Span(Text("x")))))]), "P containing an Elem should be invalid")


def test_span_must_only_contain_text_or_p():
	ok = Html([Head(Title(Text("ok"))), Body(Div(Span([Text("a"), P(Text("b"))])))])
	bad = Html([Head(Title(Text("ok"))), Body(Div(Span(H1(Text("no")))))])
	only_text = Html([Head(Title(Text("ok"))), Body(Div(Span([Text("a"), Text("b")])))])
	only_p = Html([Head(Title(Text("ok"))), Body(Div(Span([P(Text("a")), P(Text("b"))])))])
 
	assert_valid(ok, "Span containing only Text or P should be valid")
	assert_invalid(bad, "Span containing disallowed child should be invalid")
	assert_valid(only_text, "Span containing only Text should be valid")
	assert_valid(only_p, "Span containing only P should be valid")

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
	empty_table = Html([Head(Title(Text("ok"))), Body(Table())])
 
	assert_valid(ok, "Table with only Tr children should be valid")
	assert_invalid(bad, "Table containing non-Tr child should be invalid")
	assert_valid(empty_table, "Table with no children should be valid")


def test_str_prepends_doctype_only_for_html_root():
	html_page = Page(make_valid_doc())
	non_html_page = Page(Div(Text("x")))

	html_str = str(html_page)
	non_html_str = str(non_html_page)

	check(html_str.startswith("<!DOCTYPE html>\n"), "Html root output must start with doctype")
	check(not non_html_str.startswith("<!DOCTYPE html>"), "Non-html root output must not start with doctype")


def test_write_to_file_prepends_doctype_only_for_html_root():
	html_path = "./_tmp_page_html.html"
	non_html_path = "./_tmp_page_non_html.html"
	txt_path = "./_tmp_page_html.txt"

	try:
		Page(make_valid_doc()).write_to_file(html_path)
		Page(Div(Text("x"))).write_to_file(non_html_path)
		Page(make_valid_doc()).write_to_file(txt_path)

		with open(html_path, "r", encoding="utf-8") as f:
			html_data = f.read()
		with open(non_html_path, "r", encoding="utf-8") as f:
			non_html_data = f.read()
		with open(txt_path, "r", encoding="utf-8") as f:
			txt_data = f.read()

		check(html_data.startswith("<!DOCTYPE html>\n"), "Html file output must include doctype")
		check(not non_html_data.startswith("<!DOCTYPE html>"), "Non-html file output must not include doctype")
		check(not txt_data.startswith("<!DOCTYPE html>"), "Txt file output must not include doctype")
	finally:
		if os.path.exists(html_path):
			os.remove(html_path)
		if os.path.exists(non_html_path):
			os.remove(non_html_path)
		if os.path.exists(txt_path):
			os.remove(txt_path)


def test_import_restrictions_for_turn_in_files():
	base_dir = os.path.dirname(__file__)
	files = {
		"elem.py": {"mode": "no-imports", "allowed": set()},
		"elements.py": {"mode": "local-imports", "allowed": {"elem"}},
		"Page.py": {"mode": "local-imports", "allowed": {"elem", "elements"}},
	}

	for filename, rules in files.items():
		path = os.path.join(base_dir, filename)
		with open(path, "r", encoding="utf-8") as f:
			source = f.read()

		tree = ast.parse(source)
		for node in ast.walk(tree):
			if isinstance(node, ast.Import):
				if rules["mode"] == "no-imports":
					check(False, f"{filename} must not contain imports")

				for alias in node.names:
					module = alias.name.split(".")[0]
					check(
						module in rules["allowed"],
						f"{filename} can only import local files: {', '.join(sorted(rules['allowed']))}"
					)

			elif isinstance(node, ast.ImportFrom):
				if rules["mode"] == "no-imports":
					check(False, f"{filename} must not contain imports")

				module = (node.module or "").split(".")[0]
				check(
					node.level == 0 and module in rules["allowed"],
					f"{filename} can only import local files: {', '.join(sorted(rules['allowed']))}"
				)


def dry_bonus_repeated_logic_in_page_test():
	page_path = os.path.join(os.path.dirname(__file__), "Page.py")
	with open(page_path, "r", encoding="utf-8") as f:
		source = f.read()

	tree = ast.parse(source)
	page_cls = None
	for node in tree.body:
		if isinstance(node, ast.ClassDef) and node.name == "Page":
			page_cls = node
			break

	check(page_cls is not None, "Page class not found in Page.py")

	def _contains_call(expr):
		for n in ast.walk(expr):
			if isinstance(n, ast.Call):
				return True
		return False

	def _if_returns_constant_value(if_node):
		"""Return (matched, value) for simple pattern: if <cond>: return <const>."""
		if if_node.orelse:
			return (False, None)
		if len(if_node.body) != 1:
			return (False, None)
		ret = if_node.body[0]
		if not isinstance(ret, ast.Return):
			return (False, None)
		val = ret.value
		if isinstance(val, ast.Constant) and isinstance(val.value, bool):
			return (True, val.value)
		return (False, None)

	def _collect_consecutive_if_suggestions(method_name, statements, out):
		"""Collect suggestions only for consecutive if statements with same return bool."""
		run_lines = []
		run_value = None

		def flush_run():
			nonlocal run_lines, run_value
			if run_value is not None and len(run_lines) > 1:
				out.append((method_name, run_value, list(run_lines)))
			run_lines = []
			run_value = None

		for stmt in statements:
			if isinstance(stmt, ast.If):
				matched, val = _if_returns_constant_value(stmt)
				if matched:
					line = getattr(stmt, "lineno", -1)
					if run_value is None:
						run_value = val
						run_lines = [line]
					elif run_value == val:
						run_lines.append(line)
					else:
						flush_run()
						run_value = val
						run_lines = [line]
				else:
					flush_run()
			else:
				flush_run()

			# Recurse into nested blocks independently.
			if isinstance(stmt, ast.If):
				_collect_consecutive_if_suggestions(method_name, stmt.body, out)
				_collect_consecutive_if_suggestions(method_name, stmt.orelse, out)
			elif isinstance(stmt, (ast.For, ast.While)):
				_collect_consecutive_if_suggestions(method_name, stmt.body, out)
				_collect_consecutive_if_suggestions(method_name, stmt.orelse, out)
			elif isinstance(stmt, (ast.With, ast.AsyncWith)):
				_collect_consecutive_if_suggestions(method_name, stmt.body, out)
			elif isinstance(stmt, ast.Try):
				_collect_consecutive_if_suggestions(method_name, stmt.body, out)
				for handler in stmt.handlers:
					_collect_consecutive_if_suggestions(method_name, handler.body, out)
				_collect_consecutive_if_suggestions(method_name, stmt.orelse, out)
				_collect_consecutive_if_suggestions(method_name, stmt.finalbody, out)

		flush_run()

	# Ignore nodes driven by function calls: repeated helper usage is encouraged by DRY.
	interesting_types = (ast.If, ast.For, ast.While, ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Try)
	repeated = []

	# Only compare patterns inside each method scope.
	method_nodes = [n for n in page_cls.body if isinstance(n, ast.FunctionDef)]
	if_suggestions = []
	for method in method_nodes:
		patterns = {}
		_collect_consecutive_if_suggestions(method.name, method.body, if_suggestions)
		for node in ast.walk(method):
			if not isinstance(node, interesting_types):
				continue
			# Keep control-flow repetition checks strict inside the same method.
			# Repeated guards like `if self._is_text(node):` should be flagged.
			if isinstance(node, ast.Assign) and _contains_call(node.value):
				continue
			if isinstance(node, ast.AnnAssign) and node.value is not None and _contains_call(node.value):
				continue
			if isinstance(node, ast.AugAssign) and _contains_call(node.value):
				continue
			if isinstance(node, ast.Try):
				call_inside_try = any(isinstance(n, ast.Call) for n in ast.walk(node))
				if call_inside_try:
					continue

			key = f"{type(node).__name__}:{ast.dump(node, include_attributes=False)}"
			patterns.setdefault(key, []).append(getattr(node, "lineno", -1))

		for key, lines in patterns.items():
			if len(lines) > 1:
				repeated.append((method.name, key, lines))

	# Split hard failures from advisory suggestions.
	hard_repeated = repeated

	# Report advisory suggestions without failing the bonus test.
	for method_name, ret_value, lines in sorted(if_suggestions, key=lambda x: len(x[2]), reverse=True)[:5]:
		loc = ",".join(f"L{n}" for n in lines if n != -1)
		log(
			f"[DRY SUGGESTION] {method_name}: ifs with same return ({ret_value}) at {loc}; consider merging conditions with 'or' in one if",
			"yellow"
		)

	# Keep hard duplicate patterns as failing signal.
	details = []
	for method_name, key, lines in sorted(hard_repeated, key=lambda x: len(x[2]), reverse=True)[:5]:
		kind = key.split(":", 1)[0]
		loc = ",".join(f"L{n}" for n in lines if n != -1)
		details.append(f"{method_name}: {kind} repeated at {loc}")

	check(
		len(hard_repeated) == 0,
		"Possible repeated logic in Page.py (consider extracting helper functions): " + " | ".join(details)
	)

# -- RUN TESTS --
def run_tests():
	log("=== RUNNING TESTS ===", "blue")
	
	#tests = [
	#	("Test description", test_function),
	#]
	tests = [
		('Import restrictions (turn-in files)', test_import_restrictions_for_turn_in_files),
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
	bonus_tests = [
		('DRY repeated logic check', dry_bonus_repeated_logic_in_page_test),
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
	else:
		log(f"{passed}/{total} tests passed.", "red")

	print()
	log("=== BONUS TESTS (optional) ===", "blue")
	for name, fun in bonus_tests:
		if test(name, fun):
			log(f"[EXTRA DONE] {name} 🎉", "magenta")
		else:
			log(f"[EXTRA TODO] {name} (does not affect main score)", "yellow")

if __name__ == "__main__":
	run_tests()
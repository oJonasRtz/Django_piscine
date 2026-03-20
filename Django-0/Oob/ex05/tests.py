import ast
import os

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


ASSERT_COUNTER = {
	"executed": 0,
	"passed": 0,
}


def _reset_assert_counter():
	ASSERT_COUNTER["executed"] = 0
	ASSERT_COUNTER["passed"] = 0


def check(condition, msg="Assertion failed"):
	ASSERT_COUNTER["executed"] += 1
	if condition:
		ASSERT_COUNTER["passed"] += 1
		return
	raise AssertionError(msg)


ALL_TAG_CLASSES = [
	Html, Head, Body, Title, Meta, Img, Table, Tr, Th, Td,
	Ul, Ol, Li, H1, H2, P, Div, Span, Hr, Br
]

DOUBLE_TAG_CLASSES = [cls for cls in ALL_TAG_CLASSES if cls().tag_type == 'double']
SIMPLE_TAG_CLASSES = [cls for cls in ALL_TAG_CLASSES if cls().tag_type == 'simple']

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
def test_inheritance():
	for cls in ALL_TAG_CLASSES:
		check(isinstance(cls(), Elem), f"{cls.__name__} should be a subclass of Elem")

def test_empty_tags():
	for cls in DOUBLE_TAG_CLASSES:
		tag = cls().tag
		expected = f'<{tag}></{tag}>'
		check(str(cls()) == expected, f"{cls.__name__} should render as {expected}")

	for cls in SIMPLE_TAG_CLASSES:
		tag = cls().tag
		expected = f'<{tag} />'
		check(str(cls()) == expected, f"{cls.__name__} should render as {expected}")
 
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
		check(str(parent) == expected, (
			f"{cls.__name__} nesting failed. Expected {expected}, got {str(parent)}"
		))


def test_nesting_all_tags_as_children():
	for cls in ALL_TAG_CLASSES:
		child = cls(attr={"id": "child"})
		parent = Div([child])
		child_render = str(child)
		expected = f'<div>\n  {child_render}\n</div>'
		check(str(parent) == expected, (
			f"{cls.__name__} as child nesting failed. Expected {expected}, got {str(parent)}"
		))

def test_content_all_double_tags():
	for cls in DOUBLE_TAG_CLASSES:
		elem = cls(Text("My Title"))
		tag = cls().tag
		expected = f'<{tag}>\n  My Title\n</{tag}>'
		check(str(elem) == expected, f"{cls.__name__} content failed. Expected {expected}, got {str(elem)}")

def test_attributes_all_tags():
	attrs = {"id": "node", "class": "primary"}

	for cls in DOUBLE_TAG_CLASSES:
		tag = cls().tag
		elem = cls(attr=attrs)
		expected = f'<{tag} class="primary" id="node"></{tag}>'
		check(str(elem) == expected, (
			f"{cls.__name__} attributes failed. Expected {expected}, got {str(elem)}"
		))

	for cls in SIMPLE_TAG_CLASSES:
		tag = cls().tag
		elem = cls(attr=attrs)
		expected = f'<{tag} class="primary" id="node" />'
		check(str(elem) == expected, (
			f"{cls.__name__} attributes failed. Expected {expected}, got {str(elem)}"
		))

def test_self_closing():
	check(str(Br()) == '<br />', "Br should render as <br />")
	check(str(Hr()) == '<hr />', "Hr should render as <hr />")

def test_list_content():
	ul = Ul([
		Li(Text("A")),
		Li(Text("B")),
	])
	expected = '<ul>\n  <li>\n    A\n  </li>\n  <li>\n    B\n  </li>\n</ul>'
	check(str(ul) == expected, f"Expected {expected}, got {str(ul)}")
	
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

	check(str(doc) == expected, f"Expected:\n{expected}\nGot:\n{str(doc)}")


def test_subject_shortcut_example():
	doc = Html([Head(), Body()])
	expected = "<html>\n  <head></head>\n  <body></body>\n</html>"
	check(str(doc) == expected, "Html([Head(), Body()]) should match subject example output")


def test_no_direct_elem_instantiation_in_elements_module():
	elements_path = os.path.join(os.path.dirname(__file__), "elements.py")
	with open(elements_path, "r", encoding="utf-8") as f:
		source = f.read()

	tree = ast.parse(source)
	direct_elem_calls = []
	for node in ast.walk(tree):
		if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Elem":
			direct_elem_calls.append(node.lineno)

	check(
		len(direct_elem_calls) == 0,
		"Direct Elem(...) instantiation in elements.py is prohibited from ex05 onward"
	)


def test_import_restrictions_for_subject():
	base_dir = os.path.dirname(__file__)
	elem_path = os.path.join(base_dir, "elem.py")
	elements_path = os.path.join(base_dir, "elements.py")

	with open(elem_path, "r", encoding="utf-8") as f:
		elem_source = f.read()
	with open(elements_path, "r", encoding="utf-8") as f:
		elements_source = f.read()

	elem_tree = ast.parse(elem_source)
	elem_imports = [node for node in ast.walk(elem_tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
	check(len(elem_imports) == 0, "elem.py must not import external modules in ex05")

	elements_tree = ast.parse(elements_source)
	for node in ast.walk(elements_tree):
		if isinstance(node, ast.Import):
			check(False, "elements.py should not use 'import ...'; only 'from elem import ...' is allowed")
		elif isinstance(node, ast.ImportFrom):
			check(node.level == 0 and node.module == "elem", "elements.py can only import from elem.py")


def dry_bonus_all_classes_only_define_init_and_use_super():
	elements_path = os.path.join(os.path.dirname(__file__), "elements.py")
	with open(elements_path, "r", encoding="utf-8") as f:
		source = f.read()

	tree = ast.parse(source)
	class_nodes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
	for cls in class_nodes:
		methods = [node for node in cls.body if isinstance(node, ast.FunctionDef)]
		method_names = [m.name for m in methods]
		check(method_names == ["__init__"], f"{cls.name} should only redefine __init__ (DRY)")

		init_node = methods[0]
		has_super = False
		for node in ast.walk(init_node):
			if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
				base = node.func.value
				is_super_call = isinstance(base, ast.Call) and isinstance(base.func, ast.Name) and base.func.id == "super"
				if is_super_call and node.func.attr == "__init__":
					has_super = True
					break
		check(has_super, f"{cls.name}.__init__ should call super().__init__(...) (DRY)")


def dry_bonus_repeated_logic_checker_test():
	target_path = os.path.join(os.path.dirname(__file__), "elements.py")
	with open(target_path, "r", encoding="utf-8") as f:
		source = f.read()

	tree = ast.parse(source)

	def _contains_call(expr):
		for n in ast.walk(expr):
			if isinstance(n, ast.Call):
				return True
		return False

	def _if_returns_constant_value(if_node):
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

	def _collect_consecutive_if_suggestions(scope_name, statements, out):
		run_lines = []
		run_value = None

		def flush_run():
			nonlocal run_lines, run_value
			if run_value is not None and len(run_lines) > 1:
				out.append((scope_name, run_value, list(run_lines)))
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

			if isinstance(stmt, ast.If):
				_collect_consecutive_if_suggestions(scope_name, stmt.body, out)
				_collect_consecutive_if_suggestions(scope_name, stmt.orelse, out)
			elif isinstance(stmt, (ast.For, ast.While)):
				_collect_consecutive_if_suggestions(scope_name, stmt.body, out)
				_collect_consecutive_if_suggestions(scope_name, stmt.orelse, out)
			elif isinstance(stmt, (ast.With, ast.AsyncWith)):
				_collect_consecutive_if_suggestions(scope_name, stmt.body, out)
			elif isinstance(stmt, ast.Try):
				_collect_consecutive_if_suggestions(scope_name, stmt.body, out)
				for handler in stmt.handlers:
					_collect_consecutive_if_suggestions(scope_name, handler.body, out)
				_collect_consecutive_if_suggestions(scope_name, stmt.orelse, out)
				_collect_consecutive_if_suggestions(scope_name, stmt.finalbody, out)

		flush_run()

	interesting_types = (ast.If, ast.For, ast.While, ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Try)
	repeated = []
	if_suggestions = []

	def _process_function(scope_name, func_node):
		patterns = {}
		_collect_consecutive_if_suggestions(scope_name, func_node.body, if_suggestions)
		for node in ast.walk(func_node):
			if not isinstance(node, interesting_types):
				continue
			if isinstance(node, ast.Assign) and _contains_call(node.value):
				continue
			if isinstance(node, ast.AnnAssign) and node.value is not None and _contains_call(node.value):
				continue
			if isinstance(node, ast.AugAssign) and _contains_call(node.value):
				continue
			if isinstance(node, ast.Try):
				if any(isinstance(n, ast.Call) for n in ast.walk(node)):
					continue

			key = f"{type(node).__name__}:{ast.dump(node, include_attributes=False)}"
			patterns.setdefault(key, []).append(getattr(node, "lineno", -1))

		for key, lines in patterns.items():
			if len(lines) > 1:
				repeated.append((scope_name, key, lines))

	for node in tree.body:
		if isinstance(node, ast.FunctionDef):
			_process_function(node.name, node)
		elif isinstance(node, ast.ClassDef):
			for child in node.body:
				if isinstance(child, ast.FunctionDef):
					_process_function(f"{node.name}.{child.name}", child)

	for scope_name, ret_value, lines in sorted(if_suggestions, key=lambda x: len(x[2]), reverse=True)[:5]:
		loc = ",".join(f"L{n}" for n in lines if n != -1)
		log(
			f"[DRY SUGGESTION] {scope_name}: ifs with same return ({ret_value}) at {loc}; consider merging with 'or'",
			"yellow"
		)

	details = []
	for scope_name, key, lines in sorted(repeated, key=lambda x: len(x[2]), reverse=True)[:5]:
		kind = key.split(":", 1)[0]
		loc = ",".join(f"L{n}" for n in lines if n != -1)
		details.append(f"{scope_name}: {kind} repeated at {loc}")

	check(
		len(repeated) == 0,
		"Possible repeated logic in elements.py (consider extracting helper functions): " + " | ".join(details)
	)

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
		('Full document test', test_full_document),
		('Subject shortcut example test', test_subject_shortcut_example),
		('Import restrictions test', test_import_restrictions_for_subject),
		('No direct Elem() in elements.py', test_no_direct_elem_instantiation_in_elements_module),
	]
	bonus_tests = [
		('DRY classes stay minimal', dry_bonus_all_classes_only_define_init_and_use_super),
		('DRY repeated logic check', dry_bonus_repeated_logic_checker_test),
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
			log(f"[EXTRA DONE] {name}", "green")
		else:
			log(f"[EXTRA TODO] {name} (does not affect main score)", "yellow")

if __name__ == "__main__":
	run_tests()
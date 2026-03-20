import ast
import os
import subprocess
import sys

from elem import Elem, Text

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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def test_text_basic_behavior():
	check(isinstance(Text(), str), "Text must inherit from str")
	check(str(Text()) == "", "Default Text() should be empty string")
	check(str(Text("foo")) == "foo", "Text should keep plain string content")
	check(str(Text("foo\nbar")) == "foo\n<br />\nbar", "Text should convert newlines to <br />")
	check(str(Text('<>"\'')) == "&lt;&gt;&quot;&apos;", "Text should escape HTML sensitive chars")


def test_elem_core_behavior():
	root = Elem(tag="div", attr={"id": "main"}, content=[Text("hello"), Elem()], tag_type="double")
	data = str(root)
	check(data.startswith('<div id="main">'), "Elem should render opening tag with attributes")
	check("hello" in data, "Elem should render text content")
	check("<div></div>" in data, "Elem should render nested elem content")
	check(data.endswith("</div>"), "Elem should render closing tag for double tag type")

	simple = Elem(tag="img", attr={"src": "x"}, tag_type="simple")
	check(str(simple) == '<img src="x" />', "Simple tag should render as self-closing tag")


def test_elem_validation_error_on_bad_content():
	bad_raised = False
	try:
		Elem(content=1)
	except Elem.ValidationError:
		bad_raised = True
	check(bad_raised, "Elem must raise ValidationError on invalid content type")

	bad_list_raised = False
	try:
		Elem(content=[Text("ok"), 1])
	except Elem.ValidationError:
		bad_list_raised = True
	check(bad_list_raised, "Elem must raise ValidationError when list contains invalid content type")


def test_subject_html_structure_replication():
	html = Elem(tag='html', content=[
		Elem(tag='head', content=[
			Elem(tag='title', content=Text('"Hello ground!"'), tag_type='double')
		], tag_type='double'),
		Elem(tag='body', content=[
			Elem(tag='h1', content=[Text('"Oh no, not again!"')], tag_type='double'),
			Elem(tag='img', attr={'src': "http://i.imgur.com/pfp3T.jpg"}, tag_type='simple'),
		], tag_type='double')
	], tag_type='double')

	doc = str(html)
	check(doc.startswith("<html>"), "Structure should start with html tag")
	check("<head>" in doc and "</head>" in doc, "Structure should contain head tag")
	check("<title>" in doc and "</title>" in doc, "Structure should contain title tag")
	check("&quot;Hello ground!&quot;" in doc, "Title text should be present and escaped")
	check("<body>" in doc and "</body>" in doc, "Structure should contain body tag")
	check("<h1>" in doc and "</h1>" in doc, "Structure should contain h1 tag")
	check("&quot;Oh no, not again!&quot;" in doc, "H1 text should be present and escaped")
	check('<img src="http://i.imgur.com/pfp3T.jpg" />' in doc, "Structure should contain required img tag")


def test_elem_file_has_no_imports():
	elem_path = os.path.join(BASE_DIR, "elem.py")
	with open(elem_path, "r", encoding="utf-8") as f:
		source = f.read()

	tree = ast.parse(source)
	imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
	check(len(imports) == 0, "ex04 allows no imports in elem.py")


def test_official_subject_tests_py_passes():
	official_tests = os.path.join(BASE_DIR, "tests.py")
	check(
		os.path.exists(official_tests),
		"Official tests.py not found in ex04. Please extract d02.tar and ensure tests.py is present."
	)

	result = subprocess.run(
		[sys.executable, "tests.py"],
		cwd=BASE_DIR,
		capture_output=True,
		text=True,
	)

	combined_output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
	if result.returncode != 0:
		preview = "\n".join(combined_output.strip().splitlines()[-12:])
		check(False, f"Official tests.py exited with code {result.returncode}.\nLast output lines:\n{preview}")

	check("Tests succeeded!" in combined_output, "Official tests.py did not report 'Tests succeeded!'")


def dry_bonus_repeated_logic_checker_test():
	target_path = os.path.join(BASE_DIR, "elem.py")
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
		"Possible repeated logic in elem.py (consider extracting helper functions): " + " | ".join(details)
	)

# -- RUN TESTS --
def run_tests():
	log("=== RUNNING TESTS ===", "blue")
	
	#tests = [
	#	("Test description", test_function),
	#]
	tests = [
		("Text basic behavior", test_text_basic_behavior),
		("Elem core behavior", test_elem_core_behavior),
		("Elem ValidationError behavior", test_elem_validation_error_on_bad_content),
		("Subject HTML structure replication", test_subject_html_structure_replication),
		("No imports in elem.py", test_elem_file_has_no_imports),
		("Official tests.py passes", test_official_subject_tests_py_passes),
	]
	bonus_tests = [
		("DRY repeated logic check", dry_bonus_repeated_logic_checker_test),
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
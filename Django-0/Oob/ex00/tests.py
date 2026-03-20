import os
import sys
import subprocess
import ast

import render
import settings

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


def _run_render(args):
	return subprocess.run(
		[sys.executable, "render.py", *args],
		cwd=BASE_DIR,
		capture_output=True,
		text=True,
	)


def _cleanup(*paths):
	for path in paths:
		if os.path.exists(path):
			os.remove(path)


def _read_file(path):
	with open(path, "r", encoding="utf-8") as f:
		return f.read()


def _write_file(path, content):
	with open(path, "w", encoding="utf-8") as f:
		f.write(content)


def test_render_success_creates_html_and_replaces_patterns():
	template_path = os.path.join(BASE_DIR, "_tmp_success.template")
	html_path = os.path.join(BASE_DIR, "_tmp_success.html")

	_cleanup(template_path, html_path)
	try:
		with open(template_path, "w", encoding="utf-8") as f:
			f.write('<p>"-Who are you?\n-A {name}!"</p>')

		result = _run_render([os.path.basename(template_path)])
		check(result.returncode == 0, "render.py should exit with code 0 on success")
		check(os.path.exists(html_path), "Expected output .html file to be created")

		with open(html_path, "r", encoding="utf-8") as f:
			data = f.read()
		check("John Doe" in data, "Expected {name} to be replaced using settings.py")
	finally:
		_cleanup(template_path, html_path)


def test_wrong_extension_is_handled():
	txt_path = os.path.join(BASE_DIR, "_tmp_wrong_ext.txt")
	html_path = os.path.join(BASE_DIR, "_tmp_wrong_ext.html")

	_cleanup(txt_path, html_path)
	try:
		with open(txt_path, "w", encoding="utf-8") as f:
			f.write("{name}")

		result = _run_render([os.path.basename(txt_path)])
		check(result.returncode == 0, "Wrong extension should be handled gracefully")
		check("not supported or does not exist" in result.stdout, "Expected error message for wrong extension")
		check(not os.path.exists(html_path), "No output html should be created for wrong extension")
	finally:
		_cleanup(txt_path, html_path)


def test_non_existing_file_is_handled():
	missing = "_tmp_missing_file.template"
	html_path = os.path.join(BASE_DIR, "_tmp_missing_file.html")

	_cleanup(html_path)
	result = _run_render([missing])
	check(result.returncode == 0, "Missing file should be handled gracefully")
	check("not supported or does not exist" in result.stdout, "Expected message for missing file")
	check(not os.path.exists(html_path), "No output html should be created for missing file")


def test_wrong_number_of_arguments_is_handled():
	result_no_args = _run_render([])
	check(result_no_args.returncode == 0, "No-arg invocation should be handled gracefully")
	check("Usage:" in result_no_args.stdout, "Expected usage message when no args are provided")

	result_extra_args = _run_render(["myCv.template", "extra_arg"])
	check(result_extra_args.returncode == 0, "Extra args invocation should be handled gracefully")
	check("Usage:" in result_extra_args.stdout, "Expected usage message when too many args are provided")


def test_render_template_keeps_unknown_patterns():
	template = "Hello {name}, unknown={unknown_key}"
	rendered = render.render_template(template)
	check("John Doe" in rendered, "Known variable should be replaced")
	check("{unknown_key}" in rendered, "Unknown variable should remain unchanged")


def test_rejects_invalid_variable_formats():
	template = (
		"valid={name} | dollar=$name | percent=%name% | "
		"hyphen={name-last} | spaced={first name} | bang={!name}"
	)
	rendered = render.render_template(template)

	check("valid=John Doe" in rendered, "Valid {name} format should be replaced")
	check("$name" in rendered, "Dollar format should not be replaced")
	check("%name%" in rendered, "Percent format should not be replaced")
	check("{name-last}" in rendered, "Hyphenated placeholder should not be replaced")
	check("{first name}" in rendered, "Spaced placeholder should not be replaced")
	check("{!name}" in rendered, "Bang-prefixed placeholder should not be replaced")


def test_rejects_unsupported_settings_value_types():
	settings_path = os.path.join(BASE_DIR, "settings.py")
	original_settings = _read_file(settings_path)
	template_path = os.path.join(BASE_DIR, "_tmp_unsupported_types.template")
	html_path = os.path.join(BASE_DIR, "_tmp_unsupported_types.html")

	_cleanup(template_path, html_path)
	try:
		_write_file(
			settings_path,
			'\n'.join([
				'name = "TypeCheck"',
				'good_number = 42',
				'bad_dict = {"k": "v"}',
				'bad_tuple = (1, 2, 3)',
				'bad_set = {"a", "b"}',
			]) + '\n'
		)
		_write_file(
			template_path,
			"<p>{name} | {good_number} | {bad_dict} | {bad_tuple} | {bad_set}</p>"
		)

		result = _run_render([os.path.basename(template_path)])
		check(result.returncode == 0, "render.py should run with mixed supported/unsupported settings types")
		check(os.path.exists(html_path), "Output html should be created")

		data = _read_file(html_path)
		check("TypeCheck" in data, "Supported string should be replaced")
		check("42" in data, "Supported numeric should be replaced")
		check("{bad_dict}" in data, "Dict value should be ignored and stay as placeholder")
		check("{bad_tuple}" in data, "Tuple value should be ignored and stay as placeholder")
		check("{bad_set}" in data, "Set value should be ignored and stay as placeholder")
	finally:
		_write_file(settings_path, original_settings)
		_cleanup(template_path, html_path)


def test_is_valid_file_only_accepts_template_extension():
	template_path = os.path.join(BASE_DIR, "_tmp_valid_check.template")
	wrong_ext_path = os.path.join(BASE_DIR, "_tmp_valid_check.txt")

	_cleanup(template_path, wrong_ext_path)
	try:
		with open(template_path, "w", encoding="utf-8") as f:
			f.write("x")
		with open(wrong_ext_path, "w", encoding="utf-8") as f:
			f.write("x")

		check(render.is_valid_file(template_path), "Existing .template file should be valid")
		check(not render.is_valid_file(wrong_ext_path), "Existing non-.template file should be invalid")
		check(not render.is_valid_file("/tmp/this_file_should_not_exist_42.template"), "Missing .template file should be invalid")
	finally:
		_cleanup(template_path, wrong_ext_path)


def test_generated_filename_matches_template_name_with_custom_settings():
	settings_path = os.path.join(BASE_DIR, "settings.py")
	original_settings = _read_file(settings_path)
	template_path = os.path.join(BASE_DIR, "_tmp_profile.template")
	html_path = os.path.join(BASE_DIR, "_tmp_profile.html")

	_cleanup(template_path, html_path)
	try:
		_write_file(
			settings_path,
			'\n'.join([
				'name = "Ada"',
				'email = "ada@example.com"',
				'skills = ["Python", "Testing"]',
			]) + '\n'
		)
		_write_file(template_path, "<p>{name} | {email} | {skills}</p>")

		result = _run_render([os.path.basename(template_path)])
		check(result.returncode == 0, "render.py should succeed with custom settings")
		check(os.path.exists(html_path), "Generated filename should match template basename")

		data = _read_file(html_path)
		check("Ada" in data, "Expected custom name replacement")
		check("ada@example.com" in data, "Expected custom email replacement")
		check("Python, Testing" in data, "Expected list replacement formatting")
	finally:
		_write_file(settings_path, original_settings)
		_cleanup(template_path, html_path)


def test_missing_settings_variable_remains_in_generated_html():
	settings_path = os.path.join(BASE_DIR, "settings.py")
	original_settings = _read_file(settings_path)
	template_name = "myCv.template"
	template_path = os.path.join(BASE_DIR, template_name)
	html_path = os.path.join(BASE_DIR, "myCv.html")
	original_html = _read_file(html_path) if os.path.exists(html_path) else None

	try:
		_write_file(
			settings_path,
			'\n'.join([
				'email = "missing-name@example.com"',
				'skills = ["Only", "Subset"]',
			]) + '\n'
		)

		result = _run_render([template_name])
		check(result.returncode == 0, "render.py should still succeed when some keys are missing")
		check(os.path.exists(html_path), "Expected output html file for myCv.template")

		data = _read_file(html_path)
		check("{name}" in data, "Missing variable {name} should remain unchanged in generated html")
		check("missing-name@example.com" in data, "Known variables should still be replaced")
	finally:
		_write_file(settings_path, original_settings)
		if original_html is None:
			_cleanup(html_path)
		else:
			_write_file(html_path, original_html)


def test_extra_list_ssupport():
	settings_path = os.path.join(BASE_DIR, "settings.py")
	original_settings = _read_file(settings_path)
	template_path = os.path.join(BASE_DIR, "_tmp_bonus_list.template")
	html_path = os.path.join(BASE_DIR, "_tmp_bonus_list.html")

	_cleanup(template_path, html_path)
	try:
		_write_file(
			settings_path,
			'\n'.join([
				'name = "Bonus"',
				'skills = ["a", "b", "c"]',
			]) + '\n'
		)
		_write_file(template_path, "<p>{skills}</p>")

		result = _run_render([os.path.basename(template_path)])
		check(result.returncode == 0, "render.py should run for bonus list formatting test")
		check(os.path.exists(html_path), "Bonus output html should be created")

		data = _read_file(html_path)
		check("a, b, c" in data, 'List should be rendered as "a, b, c"')
	finally:
		_write_file(settings_path, original_settings)
		_cleanup(template_path, html_path)


def test_render_imports_are_whitelisted():
	render_path = os.path.join(BASE_DIR, "render.py")
	allowed_modules = {"sys", "os", "re", "settings"}

	source = _read_file(render_path)
	tree = ast.parse(source)

	for node in ast.walk(tree):
		if isinstance(node, ast.Import):
			for alias in node.names:
				module_name = alias.name.split(".")[0]
				check(
					module_name in allowed_modules,
					f"Disallowed import in render.py: '{alias.name}'. Allowed: sys, os, re, settings"
				)
		elif isinstance(node, ast.ImportFrom):
			module_name = (node.module or "").split(".")[0]
			check(
				module_name in allowed_modules and node.level == 0,
				f"Disallowed from-import in render.py: from {node.module} import ..."
			)


def dry_bonus_repeated_logic_checker_test():
	target_path = os.path.join(BASE_DIR, "render.py")
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
		"Possible repeated logic in render.py (consider extracting helper functions): " + " | ".join(details)
	)

# -- RUN TESTS --
def run_tests():
	log("=== RUNNING TESTS ===", "blue")
	
	#tests = [
	#	("Test description", test_function),
	#]
	tests = [
		("Render success creates html", test_render_success_creates_html_and_replaces_patterns),
		("Import whitelist for render.py", test_render_imports_are_whitelisted),
		("Wrong extension handled", test_wrong_extension_is_handled),
		("Missing file handled", test_non_existing_file_is_handled),
		("Wrong args handled", test_wrong_number_of_arguments_is_handled),
		("Unknown pattern stays", test_render_template_keeps_unknown_patterns),
		("Reject invalid variable formats", test_rejects_invalid_variable_formats),
		("Reject dict/tuple/set settings values", test_rejects_unsupported_settings_value_types),
		("is_valid_file extension rules", test_is_valid_file_only_accepts_template_extension),
		("Generated filename matches template name", test_generated_filename_matches_template_name_with_custom_settings),
		("Missing setting key remains in html", test_missing_settings_variable_remains_in_generated_html),
	]
	bonus_tests = [
		("extra list support", test_extra_list_ssupport),
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
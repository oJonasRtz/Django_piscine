import ast
import os

import machine

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
def test_empty_cup():
	cup = machine.CoffeeMachine.EmptyCup()

	# inheritance
	check(isinstance(cup, machine.beverages.HotBeverage), "EmptyCup should inherit from HotBeverage")

	# attributes
	name = "empty cup"
	price = 0.90
	check(cup.name == name, f"Expected name '{name}', got '{cup.name}'")
	check(cup.price == price, f"Expected price {price}, got {cup.price}")

	# behavior
	description = "An empty cup?! Gimme my money back!"
	check(cup.description() == description, f"Expected description '{description}', got '{cup.description()}'")

	expected = (
		"name : empty cup\n"
		"price : 0.90\n"
		"description : An empty cup?! Gimme my money back!"
	)
	check(str(cup) == expected, f"Expected string representation:\n{expected}\nGot:\n{str(cup)}")

def serve_10_drinks(m: machine.CoffeeMachine):
	for i in range(10):
		try:
			drink = m.serve(machine.beverages.HotBeverage)
			check(isinstance(drink, machine.beverages.HotBeverage), f"Expected a HotBeverage, got {type(drink)}")
		except Exception as e:
			check(False, f"Broke to early at iteration {i}: {e}")


def serve_returns_requested_beverage_test():
	m = machine.CoffeeMachine()
	original_random = machine.random.random
	try:
		machine.random.random = lambda: 0.99
		drink = m.serve(machine.beverages.Coffee)
		check(isinstance(drink, machine.beverages.Coffee), "When not empty, serve() should return requested beverage class instance")
	finally:
		machine.random.random = original_random


def serve_returns_empty_cup_test():
	m = machine.CoffeeMachine()
	original_random = machine.random.random
	try:
		machine.random.random = lambda: 0.0
		drink = m.serve(machine.beverages.Coffee)
		check(isinstance(drink, machine.CoffeeMachine.EmptyCup), "When random branch triggers, serve() should return EmptyCup")
	finally:
		machine.random.random = original_random

def broken_machine_test():
	m = machine.CoffeeMachine()
	
 	# Serve 10 drinks to break the machine
	serve_10_drinks(m)	
 
	try:
		m.serve(machine.beverages.HotBeverage)
		check(False, "Expected Exception was not raised")
	except Exception as e:
		check(type(e) is machine.CoffeeMachine.BrokenMachineException, f"Expected BrokenMachineException, got {type(e)}")
		expected_message = "This coffee machine has to be repaired."
		check(str(e) == expected_message, f"Expected exception message '{expected_message}', got '{str(e)}'")
		
def serve_test():
	try:
		m = machine.CoffeeMachine()
		drink = m.serve(int)
		check(False, "Should have raised an exception for non-HotBeverage class")
	except Exception:
		pass  # Expected to raise an exception, so we pass if it does
	
	# should not raise an exception when serving 10 drinks
	try:
		m = machine.CoffeeMachine()
		serve_10_drinks(m)
	except Exception as e:
		check(False, f"Unexpected error during serve test: {e}")

	# -- check for randomness --
	m = machine.CoffeeMachine()
	seen_empty = False
	seen_drink = False
	for _ in range(10):
		drink = m.serve(machine.beverages.HotBeverage)
		if isinstance(drink, machine.CoffeeMachine.EmptyCup):
			seen_empty = True
		else:
			seen_drink = True
	
	if seen_empty and seen_drink:
		return  # Passed randomness test
	
	check(False, "Randomness test failed: only one type of result was seen in 10 serves")


def repair_test():
	m = machine.CoffeeMachine()
	serve_10_drinks(m)  # break the machine
	
	try:
		m.repair()
	except Exception as e:
		check(False, f"Unexpected error during repair: {e}")

	# After repair, should be able to serve again
	try:
		m.serve(machine.beverages.HotBeverage)
	except Exception as e:
		check(False, f"Unexpected error after repair: {e}")

def broken_persistense_test():
	e = machine.CoffeeMachine.BrokenMachineException()
	expected_message = "This coffee machine has to be repaired."
	check(str(e) == expected_message, f"Expected exception message '{expected_message}', got '{str(e)}'")
	
	m = machine.CoffeeMachine()
	serve_10_drinks(m)  # break the machine

	# Check if its Out of service and still broken without repairing
	for _ in range(5):
		try:
			m.serve(machine.beverages.HotBeverage)
			check(False, "Expected Exception was not raised")
		except Exception as e:
			check(type(e) is machine.CoffeeMachine.BrokenMachineException, f"Expected BrokenMachineException, got {type(e)}")
			check(str(e) == expected_message, f"Expected exception message '{expected_message}', got '{str(e)}'")

def rebreak_test():
	m = machine.CoffeeMachine()
	serve_10_drinks(m)  # break the machine
	m.repair()          # repair the machine

	# Serve 10 drinks to break the machine again
	serve_10_drinks(m)

	try:
		m.serve(machine.beverages.HotBeverage)
		check(False, "Expected Exception was not raised after re-breaking")
	except Exception as e:
		check(type(e) is machine.CoffeeMachine.BrokenMachineException, f"Expected BrokenMachineException, got {type(e)}")
		expected_message = "This coffee machine has to be repaired."
		check(str(e) == expected_message, f"Expected exception message '{expected_message}', got '{str(e)}'")


def machine_imports_whitelist_test():
	machine_path = os.path.join(os.path.dirname(__file__), "machine.py")
	allowed_modules = {"random", "beverages"}

	with open(machine_path, "r", encoding="utf-8") as f:
		source = f.read()

	tree = ast.parse(source)
	for node in ast.walk(tree):
		if isinstance(node, ast.Import):
			for alias in node.names:
				module = alias.name.split(".")[0]
				check(module in allowed_modules, f"Disallowed import in machine.py: '{alias.name}'")
		elif isinstance(node, ast.ImportFrom):
			module = (node.module or "").split(".")[0]
			check(module in allowed_modules and node.level == 0, f"Disallowed from-import in machine.py: from {node.module} import ...")


def dry_bonus_no_exact_duplicate_code_blocks_test():
	machine_path = os.path.join(os.path.dirname(__file__), "machine.py")
	with open(machine_path, "r", encoding="utf-8") as f:
		source = f.read()

	tree = ast.parse(source)
	coffee_machine_cls = None
	for node in tree.body:
		if isinstance(node, ast.ClassDef) and node.name == "CoffeeMachine":
			coffee_machine_cls = node
			break

	check(coffee_machine_cls is not None, "CoffeeMachine class not found in machine.py")

	all_lines = source.splitlines()
	class_lines = all_lines[coffee_machine_cls.lineno - 1:coffee_machine_cls.end_lineno]

	# Heuristic DRY check: repeated meaningful lines can indicate copy/paste logic.
	ignored_prefixes = ("def ", "class ", "#", "@", "else:", "elif ")
	counts = {}
	for idx, raw in enumerate(class_lines, start=coffee_machine_cls.lineno):
		line = raw.strip()
		if not line:
			continue
		if line.endswith(":") and (line.startswith("try") or line.startswith("except") or line.startswith("finally")):
			continue
		# Reusing helper calls (e.g. self._reset_state()) is usually a DRY improvement,
		# so this bonus check should not flag those as duplication.
		is_plain_call = line.endswith(")") and "=" not in line and not line.startswith("return ")
		if is_plain_call:
			continue
		if line.startswith(ignored_prefixes):
			continue
		if line not in counts:
			counts[line] = []
		counts[line].append(idx)

	repeated = sorted([(line, lines) for line, lines in counts.items() if len(lines) > 1], key=lambda x: x[0])
	details = [f"L{',L'.join(map(str, lines))}: {line}" for line, lines in repeated[:5]]
	check(
		len(repeated) == 0,
		"Possible repeated code lines in machine.py (consider extracting helper functions): " + " | ".join(details)
	)


def dry_bonus_repeated_logic_checker_test():
	target_path = os.path.join(os.path.dirname(__file__), "machine.py")
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
		"Possible repeated logic in machine.py (consider extracting helper functions): " + " | ".join(details)
	)

# -- RUN TESTS --
def run_tests():
	log("=== RUNNING TESTS ===", "blue")
	log("Note: Some tests involve randomness, so they may fail occasionally. If a test fails, try running the tests again or change the probability.", "yellow")
	
	#tests = [
	#	("Test description", test_function),
	#]
	tests = [
		("EmptyCup class test", test_empty_cup),
		("Serve returns requested beverage", serve_returns_requested_beverage_test),
		("Serve returns EmptyCup", serve_returns_empty_cup_test),
		("Broken machine test", broken_machine_test),
		("Repair test", repair_test),
		("Serve test", serve_test),
		("Broken machine persistence test", broken_persistense_test),
		("Re-breaking test", rebreak_test),
		("machine.py import whitelist", machine_imports_whitelist_test),
	]
	bonus_tests = [
		("DRY no exact duplicate code blocks", dry_bonus_no_exact_duplicate_code_blocks_test),
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
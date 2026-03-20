import ast
import os

import beverages

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
def hot_beverage_test():
	hot = beverages.HotBeverage()
	
	# -- Attribute tests --
	check(hasattr(hot, 'price'), "HotBeverage should have a 'price' attribute")
	check(hasattr(hot, 'name'), "HotBeverage should have a 'name' attribute")

	expected_price = 0.30
	expected_name = "hot beverage"
	check(hot.price == expected_price, f"Expected price {expected_price}, got {hot.price}")
	check(hot.name == expected_name, f"Expected name '{expected_name}', got '{hot.name}'")
	
	# -- Description method --
	expected_description = "Just some hot water in a cup."
	check(callable(hot.description), "HotBeverage should have a 'description' method")
	check(hot.description() == expected_description, f"Expected description '{expected_description}', got '{hot.description()}'")
	
	# -- String representation --
	expected_str = (
		"name : hot beverage\n"
		"price : 0.30\n"
		"description : Just some hot water in a cup."
	)
	check(str(hot) == expected_str, f"Expected string representation:\n{expected_str}\nGot:\n{str(hot)}")

def hot_beverage_child_test(instance, name, price, description):
	check(isinstance(instance, beverages.HotBeverage), f"{name} should be a subclass of HotBeverage")
	check(instance.name == name, f"Expected name '{name}', got '{instance.name}'")
	check(instance.price == price, f"Expected price {price}, got {instance.price}")
	check(instance.description() == description, f"Expected description '{description}', got '{instance.description()}'")
	check(str(instance) == (
		f"name : {name}\n"
		f"price : {price:.2f}\n"
		f"description : {description}"
	), f"String representation mismatch for {name}")
 
 
def coffee_test():
	coffee = beverages.Coffee()
	name = "coffee"
	price = 0.40
	description = "A coffee, to stay awake."
 
	hot_beverage_child_test(coffee, name, price, description)
	pass

def tea_test():
	tea = beverages.Tea()
	name = "tea"
	price = 0.30
	description = "Just some hot water in a cup."
 
	hot_beverage_child_test(tea, name, price, description)
	pass

def chocolate_test():
	choco = beverages.Chocolate()
	name = "chocolate"
	price = 0.50
	description = "Chocolate, sweet chocolate..."
 
	hot_beverage_child_test(choco, name, price, description)

def cappuccino_test():
	cappuccino = beverages.Cappuccino()
	name = "cappuccino"
	price = 0.45
	description = "Un po’ di Italia nella sua tazza!"
 
	hot_beverage_child_test(cappuccino, name, price, description)


def no_imports_allowed_test():
	beverages_path = os.path.join(os.path.dirname(__file__), "beverages.py")
	with open(beverages_path, "r", encoding="utf-8") as f:
		source = f.read()

	tree = ast.parse(source)
	import_nodes = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
	check(len(import_nodes) == 0, "beverages.py must not contain any import statements")


def dry_simplicity_test():
	beverages_path = os.path.join(os.path.dirname(__file__), "beverages.py")
	with open(beverages_path, "r", encoding="utf-8") as f:
		source = f.read()

	tree = ast.parse(source)
	class_nodes = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}
	child_names = ["Coffee", "Tea", "Chocolate", "Cappuccino"]

	for name in child_names:
		check(name in class_nodes, f"Missing class {name}")
		cls = class_nodes[name]

		methods = [node for node in cls.body if isinstance(node, ast.FunctionDef)]
		method_names = [m.name for m in methods]
		check(method_names == ["__init__"], f"{name} should only redefine __init__ to keep DRY")

		init_node = methods[0]
		has_super_init_call = False
		for node in ast.walk(init_node):
			if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
				is_super = isinstance(node.func.value, ast.Call) and isinstance(node.func.value.func, ast.Name) and node.func.value.func.id == "super"
				if is_super and node.func.attr == "__init__":
					has_super_init_call = True
					break

		check(has_super_init_call, f"{name}.__init__ should call super().__init__()")


def dry_bonus_repeated_logic_checker_test():
	target_path = os.path.join(os.path.dirname(__file__), "beverages.py")
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
		"Possible repeated logic in beverages.py (consider extracting helper functions): " + " | ".join(details)
	)

# -- RUN TESTS --
def run_tests():
	log("=== RUNNING TESTS ===", "blue")
	
	#tests = [
	#	("Test description", test_function),
	#]
	tests = [
		("HotBeverage class test", hot_beverage_test),
		("Coffee class test", coffee_test),
		("Tea class test", tea_test),
		("Chocolate class test", chocolate_test),
		("Cappuccino class test", cappuccino_test),
		("No imports allowed", no_imports_allowed_test),
	]
	bonus_tests = [
		("DRY class simplicity", dry_simplicity_test),
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
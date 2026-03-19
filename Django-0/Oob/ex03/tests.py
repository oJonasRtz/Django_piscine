import machine

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
def test_empty_cup():
	cup = machine.CoffeeMachine.EmptyCup()

	# inheritance
	assert isinstance(cup, machine.beverages.HotBeverage)

	# attributes
	name = "empty cup"
	price = 0.90
	assert cup.name == name, f"Expected name '{name}', got '{cup.name}'"
	assert cup.price == price, f"Expected price {price}, got {cup.price}"

	# behavior
	description = "An empty cup?! Gimme my money back!"
	assert cup.description() == description, f"Expected description '{description}', got '{cup.description()}'"

	expected = (
		"name : empty cup\n"
		"price : 0.90\n"
		"description : An empty cup?! Gimme my money back!"
	)
	assert str(cup) == expected, f"Expected string representation:\n{expected}\nGot:\n{str(cup)}"

def serve_10_drinks(m: machine.CoffeeMachine):
	for i in range(10):
		try:
			drink = m.serve(machine.beverages.HotBeverage)
			assert isinstance(drink, machine.beverages.HotBeverage), f"Expected a HotBeverage, got {type(drink)}"
		except Exception as e:
			assert False, f"Broke to early at iteration {i}: {e}"

def broken_machine_test():
	m = machine.CoffeeMachine()
	
 	# Serve 10 drinks to break the machine
	serve_10_drinks(m)	
 
	try:
		m.serve(machine.beverages.HotBeverage)
		assert False, "Expected Exception was not raised"
	except Exception as e:
		assert type(e) is machine.CoffeeMachine.BrokenMachineException, f"Expected BrokenMachineException, got {type(e)}"
		expected_message = "This coffee machine has to be repaired."
		assert str(e) == expected_message, f"Expected exception message '{expected_message}', got '{str(e)}'"
		
def serve_test():
	try:
		m = machine.CoffeeMachine()
		drink = m.serve(int)
		assert False, "Should have raised an exception for non-HotBeverage class"
	except Exception:
		pass  # Expected to raise an exception, so we pass if it does
	
	# should not raise an exception when serving 10 drinks
	try:
		m = machine.CoffeeMachine()
		serve_10_drinks(m)
	except Exception as e:
		assert False, f"Unexpected error during serve test: {e}"    

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
	
	assert False, "Randomness test failed: only one type of result was seen in 10 serves"


def repair_test():
	m = machine.CoffeeMachine()
	serve_10_drinks(m)  # break the machine
	
	try:
		m.repair()
	except Exception as e:
		assert False, f"Unexpected error during repair: {e}"

	# After repair, should be able to serve again
	try:
		m.serve(machine.beverages.HotBeverage)
	except Exception as e:
		assert False, f"Unexpected error after repair: {e}"

def broken_persistense_test():
	e = machine.CoffeeMachine.BrokenMachineException()
	expected_message = "This coffee machine has to be repaired."
	assert str(e) == expected_message, f"Expected exception message '{expected_message}', got '{str(e)}'"
	
	m = machine.CoffeeMachine()
	serve_10_drinks(m)  # break the machine

	# Check if its Out of service and still broken without repairing
	for _ in range(5):
		try:
			m.serve(machine.beverages.HotBeverage)
			assert False, "Expected Exception was not raised"
		except Exception as e:
			assert type(e) is machine.CoffeeMachine.BrokenMachineException, f"Expected BrokenMachineException, got {type(e)}"
			assert str(e) == expected_message, f"Expected exception message '{expected_message}', got '{str(e)}'"

def rebreak_test():
	m = machine.CoffeeMachine()
	serve_10_drinks(m)  # break the machine
	m.repair()          # repair the machine

	# Serve 10 drinks to break the machine again
	serve_10_drinks(m)

	try:
		m.serve(machine.beverages.HotBeverage)
		assert False, "Expected Exception was not raised after re-breaking"
	except Exception as e:
		assert type(e) is machine.CoffeeMachine.BrokenMachineException, f"Expected BrokenMachineException, got {type(e)}"
		expected_message = "This coffee machine has to be repaired."
		assert str(e) == expected_message, f"Expected exception message '{expected_message}', got '{str(e)}'"

# -- RUN TESTS --
def run_tests():
	log("=== RUNNING TESTS ===", "blue")
	
	#tests = [
	#	("Test description", test_function),
	#]
	tests = [
		("EmptyCup class test", test_empty_cup),
		("Broken machine test", broken_machine_test),
		("Repair test", repair_test),
		("Serve test", serve_test),
		("Broken machine persistence test", broken_persistense_test),
		("Re-breaking test", rebreak_test)
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
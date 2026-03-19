import intern

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
DEFAULT_NAME = "My name? I’m nobody, an intern, I have no name."

def test_name():
    # -- test default name --
    nameless = intern.Intern()
    assert str(nameless) == DEFAULT_NAME, f"Expected default name, got '{nameless.name}'"

	# -- test custom name --
    custom_name = "Alice"
    alice = intern.Intern(custom_name)
    assert str(alice) == custom_name, f"Expected name '{custom_name}', got '{alice.name}'"

def __str__test():
    assert str(intern.Intern()) == DEFAULT_NAME, "Expected default name string representation"
    name = intern.Intern("Bob")
    assert str(name) == "Bob", "Expected custom name string representation"

def coffee_str_test():
    expected = "This is the worst coffee you ever tasted."
    coffee = intern.Coffee()
    assert str(coffee) == expected, f"Expected '{expected}', got '{str(coffee)}'"

def make_coffee_test():
	myIntern = intern.Intern()
	myCoffee = myIntern.make_coffee()
	
	assert isinstance(myCoffee, intern.Coffee), "Expected an instance of Coffee"
	assert str(myCoffee) == "This is the worst coffee you ever tasted.", "Coffee string mismatch"
 
def work_test():
    i = intern.Intern()
    
    try:
        i.work()
        assert False, "Expected Exception was not raised"
    except Exception as e:
        assert type(e) is Exception, f"Expected an Exception to be raised, got {type(e)}"
        expected = "I’m just an intern, I can’t do that..."
        assert str(e) == expected, f"Expected exception message '{expected}', got '{str(e)}'"

# -- RUN TESTS --
def run_tests():
	log("=== RUNNING TESTS ===", "blue")
	
	tests = [
		("Name Test", test_name),
		("Intern.__str__ Test", __str__test),
		("Coffee.__str__ Test", coffee_str_test),
		("make_coffee Test", make_coffee_test),
		("Intern.work Test", work_test)
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
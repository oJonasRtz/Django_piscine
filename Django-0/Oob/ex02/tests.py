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
#// -- write your tests here --

# -- RUN TESTS --
def run_tests():
	log("=== RUNNING TESTS ===", "blue")
	
	#tests = [
	#	("Test description", test_function),
	#]
	tests = []
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
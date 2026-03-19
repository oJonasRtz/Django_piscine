import beverages

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
def hot_beverage_test():
    hot = beverages.HotBeverage()
	
	# -- Attribute tests --
    assert hasattr(hot, 'price'), "HotBeverage should have a 'price' attribute"
    assert hasattr(hot, 'name'), "HotBeverage should have a 'name' attribute"

    expected_price = 0.30
    expected_name = "hot beverage"
    assert hot.price == expected_price, f"Expected price {expected_price}, got {hot.price}"
    assert hot.name == expected_name, f"Expected name '{expected_name}', got '{hot.name}'"
    
    # -- Description method --
    expected_description = "Just some hot water in a cup."
    assert callable(hot.description), "HotBeverage should have a 'description' method"
    assert hot.description() == expected_description, f"Expected description '{expected_description}', got '{hot.description()}'"
    
    # -- String representation --
    expected_str = (
		"name : hot beverage\n"
		"price : 0.30\n"
		"description : Just some hot water in a cup."
	)
    assert str(hot) == expected_str, f"Expected string representation:\n{expected_str}\nGot:\n{str(hot)}"

def hot_beverage_child_test(instance, name, price, description):
    assert isinstance(instance, beverages.HotBeverage), f"{name} should be a subclass of HotBeverage"
    assert instance.name == name, f"Expected name '{name}', got '{instance.name}'"
    assert instance.price == price, f"Expected price {price}, got {instance.price}"
    assert instance.description() == description, f"Expected description '{description}', got '{instance.description()}'"
    assert str(instance) == (
		f"name : {name}\n"
		f"price : {price:.2f}\n"
		f"description : {description}"
	), f"String representation mismatch for {name}"
 
 
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
		("Cappuccino class test", cappuccino_test)
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
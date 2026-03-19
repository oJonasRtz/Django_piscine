import beverages
import random

class CoffeeMachine:
	def __init__(self):
		self.broken = False
		self.drinks_limit = 10
		self.drinks_served = 0
		
	# -- Classes --
	class EmptyCup(beverages.HotBeverage):
		def __init__(self):
			super().__init__()
			self.name = "empty cup"
			self.price = 0.90
			self._description = "An empty cup?! Gimme my money back!"
	
	class BrokenMachineException(Exception):
		def __init__(self):
			super().__init__("This coffee machine has to be repaired.")
	
	# -- Methods --
	def serve(self, beverage: beverages.HotBeverage) -> beverages.HotBeverage:
		if self.broken:
			raise self.BrokenMachineException()
  		
		if not issubclass(beverage, beverages.HotBeverage):
			raise Exception("Can only serve HotBeverage subclasses.")
		
		self.drinks_served += 1
		self.broken = self.drinks_served >= self.drinks_limit
  
		if random.random() < 0.3:  # 30% chance to serve an empty cup
			return self.EmptyCup()
		return beverage()

	def repair(self):
		if not self.broken:
			return

		self.broken = False
		self.drinks_served = 0


def serve_test(machine, n):
	blue = '\033[34m'
	yellow = '\033[33m'
	reset = '\033[0m'
 
	for i in range(n):
		try:
			drink = machine.serve(beverages.HotBeverage)
			print(f"{blue}[{i + 1}]{reset}{yellow}Serving: {reset}{drink.name}...")
		except CoffeeMachine.BrokenMachineException as e:
			print(f"{blue}[{i + 1}]{reset}{yellow}Error: {reset}{e}")

def main():
	blue = '\033[34m'
	yellow = '\033[33m'
	reset = '\033[0m'
	
	#Serving Various Drinks
	print()
	machine = CoffeeMachine()
	print(f"{blue}=== Serving Drinks ==={reset}")
	print(f"{yellow}Serving: {reset}{machine.serve(beverages.Coffee).name}...")
	print(f"{yellow}Serving: {reset}{machine.serve(beverages.Tea).name}...")
	print(f"{yellow}Serving: {reset}{machine.serve(beverages.Chocolate).name}...")
	print(f"{yellow}Serving: {reset}{machine.serve(beverages.Cappuccino).name}...")
	print(f"{yellow}Serving: {reset}{machine.serve(beverages.HotBeverage).name}...")
 
 
	# Simulate serving until machine breaks
	print()
	print(f"\n{blue}=== Serving Until Machine Breaks ==={reset}")
	m = CoffeeMachine()
	serve_test(m, 15)  # Try to serve 15 times, which is more than the limit
	
	#fixing the machine
	m.repair()
	print(f"\n{blue}=== After Repair ==={reset}")
	serve_test(m, 15)
 
if __name__ == "__main__":
	main()
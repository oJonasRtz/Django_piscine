class HotBeverage:
    def __init__(self):
        self.price = 0.30
        self.name = "hot beverage"
        self._description = "Just some hot water in a cup."
    
    def description(self):
        return self._description
    
    def __str__(self):
        return f"name : {self.name}\nprice : {self.price:.2f}\ndescription : {self.description()}"


class Coffee(HotBeverage):
    def __init__(self):
        super().__init__()
        self.price = 0.40
        self.name = "coffee"
        self._description = "A coffee, to stay awake."
        
class Tea(HotBeverage):
    def __init__(self):
        super().__init__()
        self.price = 0.30
        self.name = "tea"
        self._description = "Just some hot water in a cup."
  
class Chocolate(HotBeverage):
    def __init__(self):
        super().__init__()
        self.price = 0.50
        self.name = "chocolate"
        self._description = "Chocolate, sweet chocolate..."
  
class Cappuccino(HotBeverage):
	def __init__(self):
		super().__init__()
		self.price = 0.45
		self.name = "cappuccino"
		self._description = "Un po’ di Italia nella sua tazza!"
  

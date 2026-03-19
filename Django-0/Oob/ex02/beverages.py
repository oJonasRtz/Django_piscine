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
  
def main():
    reset = '\033[0m'
    blue = '\033[34m'

    hot = HotBeverage()
    coffee = Coffee()
    tea = Tea()
    chocolate = Chocolate()
    cappuccino = Cappuccino()

    # print
    print(f"{blue}HotBeverage:{reset}\n{hot}\n")
    print(f"{blue}Coffee:{reset}\n{coffee}\n")
    print(f"{blue}Tea:{reset}\n{tea}\n")
    print(f"{blue}Chocolate:{reset}\n{chocolate}\n")
    print(f"{blue}Cappuccino:{reset}\n{cappuccino}\n")

if __name__ == "__main__":
    main()
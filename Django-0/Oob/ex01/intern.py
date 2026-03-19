class Coffee:
    def __init__(self):
        self.name = "This is the worst coffee you ever tasted."

    def __str__(self):
        return self.name

class Intern:
    def __init__(self, name = "My name? I’m nobody, an intern, I have no name."):
        self.name = name
        
    def __str__(self):
        return self.name
    
    def make_coffee(self):
        return Coffee()
    
    def work(self):
        raise Exception("I’m just an intern, I can’t do that...")
    
def main():
    i1 = Intern()
    i2 = Intern("Mark")
    
    #display names
    print(i1)
    print(i2)
    
    #make coffee
    print(f"{i2.name} makes coffee: {str(i1.make_coffee())}")
    
    #work
    try:
        i1.work()
    except Exception as e:
        print(f"{i1.name} tries to work: {str(e)}")
    
if __name__ == "__main__":
    main()


class Test:
    def __init__(self):
        self.ls = []
    
    def add(self,data):
        self.ls.append(data)
    
    def sub(self,idx):
        self.ls.pop(idx)
    
    def display(self):
        print("DATA :",self.ls)



def test_dd(test,data):
    test.add(data)

tests = {
    "1" : Test(),
    "2" : Test()
}

test1 = tests["1"]

test_dd(test1,5)
test_dd(test1,6)
test_dd(test1,7)

tests["1"].display()
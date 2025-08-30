from botbuilder.schema import Attachment

class UserProfile:
    def __init__(self,name:str=None,sex:str=None,age:int=0):
        self.name = name
        self.sex=sex
        self.age=age
        


from botbuilder.schema import Attachment
class UserProfile:
    def __init__(self, name: str = "", email: str = "", age: int = 0, phone: str = "",
                 movies_booked: list = None, food_ordered: list = None, parking_done: list = None,
                 profile_pic:Attachment =None
                 ):
        self.name = name
        self.email = email
        self.age = age
        self.phone = phone
        self.profile_pic=profile_pic

        self.movies_booked = movies_booked
        self.food_ordered = food_ordered 
        self.parking_done = parking_done 

    def __str__(self):
        return f"Name: {self.name}, Email: {self.email}, Age: {self.age}, Phone: {self.phone}"



class Transport:
    def __init__(self, brand, speed):
        self.brand = brand
        self.speed = speed
    
    def move(self):
        print(f"Transport is moving at {self.speed} km/h")
    
    def __str__(self):
        return f"Transport: {self.brand}, Speed: {self.speed}"

class Car(Transport):
    def __init__(self, brand, speed, seats):
        super().__init__(brand, speed)
        self.seats = seats
    
    def honk(self):
        print("Beep beep!")
    
    def move(self):
        print(f"Car {self.brand} is driving at {self.speed} km/h")
    
    def __str__(self):
        return f"brand: {self.brand}, Speed: {self.speed}, Seats: {self.seats}"

class Bike(Transport):
    def __init__(self, brand, speed, bike_type):
        super().__init__(brand, speed)
        self.type = bike_type
    
    def move(self):
        print(f"Bike {self.brand} is cycling at {self.speed} km/h")
    
    def __str__(self):
        return f"Bike: {self.brand}, Speed: {self.speed}, Type: {self.type}"

car1 = Car("Kia", 130, 5)
car2 = Car("Mercedes", 120, 6)
bike1 = Bike("BMW", 25, "road")
bike2 = Bike("123", 30, "road")

print(car1)
car1.move()
car1.honk()

print(bike1)   
bike1.move()
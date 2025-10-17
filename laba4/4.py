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
    
    def __len__(self):
        return self.seats
    
    def __eq__(self, other):
        return self.speed == other.speed
    
    def __add__(self, other):
        return self.speed + other.speed

class Bike(Transport):
    def __init__(self, brand, speed, bike_type):
        super().__init__(brand, speed)
        self.type = bike_type
    
    def move(self):
        print(f"Bike {self.brand} is cycling at {self.speed} km/h")
    
    def __str__(self):
        return f"Bike: {self.brand}, Speed: {self.speed}, Type: {self.type}"

transport = Transport("Generic", 80)
car1 = Car("Kia", 130, 7)
car2 = Car("Mercedes", 120, 6)
bike = Bike("BMW", 170, 5)

print(transport)  
print(car1)      
print(car2)     
print(bike)      

# print('\n')
# transport.move() 
# car1.move()       
# car2.move()      
# bike.move()      

# print('\n')
# car1.honk()      
# car2.honk()      

# print('\n')
# print(f"В машине {car1.brand} мест: {len(car1)}")  

# print('\n')
# print(f"car1 == car2: {car1 == car2}") 

# print('\n')
# total_speed = car1 + car2
# print(f"Суммарная скорость: {total_speed} km/h") 

# print('\n')
# try:
#     result = car1 + bike
#     print(f"Результат: {result}")
# except Exception as e:
#     print(f"Ошибка: {type(e).__name__}: {e}")

result = car1 + bike
print(result)
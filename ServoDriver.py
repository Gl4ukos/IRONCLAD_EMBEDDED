from gpiozero import Servo, LED
from time import sleep


class ServoDriver:        
    
    def __init__(self):
        self.SERVO_PIN = 18  # GPIO pin connected to the servo signal wire
        self.servo = Servo(self.SERVO_PIN)  # uses default min_pulse_width=1ms, max_pulse_width=2ms

    def move(self, angle):        
        self.servo.value = -1  # full left
        sleep(1)
        self.servo.value = 0   # center
        sleep(1)
        self.servo.value = 1   # full right
        sleep(1)
    
    def pivot(self, angle):
        self.servo.value = angle

if __name__ == "__main__":
    sc = ServoDriver()

    while True:
        
        sc.pivot(float(input()))
        sleep(1)
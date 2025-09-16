from gpiozero import Servo, LED, AngularServo
from time import sleep
from adafruit_servokit import ServoKit
import board
import busio
import math


class ServoDriver:        
    
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.kit = ServoKit(channels=16, i2c=self.i2c, address=0x41)
        self.servo_channel = 1
        self.physical_servo_offset = -0.2 #the servo is not excactly centered
        self.default_steering = 90 + math.degrees(self.physical_servo_offset) #degrees
        self.max_steer = self.default_steering + 40 #degrees
        self.min_steer = self.default_steering - 40 #degrees

    def clip_steering(self, val):
        return max(min(self.max_steer, val), self.min_steer)

    # expects steering in radians
    def translate_steering(self, val):
        return self.clip_steering(self.default_steering + math.degrees(val))


    # expects radians
    def pivot(self, angle):
        steering = self.translate_steering(angle)
        self.kit.servo[self.servo_channel].angle = steering
        

if __name__ == "__main__":
    sc = ServoDriver()

    while True:
        
        sc.pivot(float(input()))
        sleep(1)
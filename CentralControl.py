
import math
import socket
import threading
import serial
import struct
import time
import lgpio
from MotorDriver import MotorDriver
from ServoDriver import ServoDriver

class CentralControl:
    def __init__(self, udp_port = 5005):

        # UDP setup
        self.udp_ip = "0.0.0.0"
        self.udp_port = udp_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.udp_ip, self.udp_port))

        # Command storage
        self.velocity = 0.0
        self.steering = 0.0
        self.max_expected_speed = 0.0
        self.calibrated = 0
        self.lock = threading.Lock()

        # # Calibrating max speed
        # while(self.calibrated == 0):
        #     print("CALIBRATING MAX SPEED...")
        #     data, addr = self.sock.recvfrom(1024)
        #     vel, steer = struct.unpack('ff', data)
        #     if(steer == float(999)):
        #         self.max_expected_speed = vel
        #         self.calibrated = 1
        #         print("MAX SPEED: ", self.max_expected_speed)
        #     time.sleep(1)
        self.max_expected_speed = 30

        #starting drivers
        self.Motor = MotorDriver(self.max_expected_speed)
        self.Servo = ServoDriver()

        # Start receiver thread
        self.running = True
        self.thread = threading.Thread(target=self.udp_listener)
        self.thread.start()
        
        # Start sender thread
        self.sender_thread = threading.Thread(target=self.sender)
        self.sender_thread.start()
        

    def udp_listener(self):
        print(f"Listening for UDP commands on port {self.udp_port}...")
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                # Expecting two floats: velocity, steering
                vel, steer = struct.unpack('ff', data)
                with self.lock:
                    if(vel != self.velocity or (steer != self.steering)):
                        #print("Speed: ", vel, ", Steering: ",math.degrees(steer))
                        pass

                    self.velocity = vel
                    self.steering = steer

            except Exception as e:
                print("UDP receive error:", e)

    def sender(self):
        while self.running:
            with self.lock:
                vel = self.velocity
                steer = self.steering
            try:
                self.Motor.send_speed(vel)
                self.Servo.pivot(steer)

            except Exception as e:
                print("UART send error:", e)
            time.sleep(0.2)  # Hz update

    def stop(self):
        self.Motor.send_speed_by_index(0)
        time.sleep(0.5)
        self.Motor.shutdown_engine()
        self.Servo.pivot(0)
        time.sleep(0.5)

        self.running = False
        self.thread.join()
        self.sender_thread.join()
        self.ser.terminate_serial_connection()
        self.sock.close()


if __name__ == "__main__":
    mc = CentralControl()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        mc.stop()
        print("Stopped motor controller.")
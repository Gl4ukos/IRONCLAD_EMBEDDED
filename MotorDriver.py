import serial
import time


class MotorDriver:
    def __init__(self):
        self.DEV_ADDR = 0x32
        self.DUTY_REG_ADDR = 0x0006
        self.FREQ_REG_ADDR = 0x0007
        self.PWM_EN_REG_ADDR = 0x0008

        self.PWM_freq_factor = 4

        self.inv_speed_incremental = 1/25
        self.speed_values = [
            0,
            25,
            50,
            75,
            100,
            125,
            150,
            175,
            200,
            225,
            250
        ]

        self.ser = serial.Serial("/dev/ttyAMA0", 9600, timeout=1)
        print("->>> SETTING UP UART CONNECTION...")
        time.sleep(1)
        
        self.write_register( self.FREQ_REG_ADDR, self.PWM_freq_factor) #setting PWM frequency
        print("->>> SETTING UP DRIVER REGISTERS...")
        time.sleep(0.5)
        self.write_register( self.DUTY_REG_ADDR, 0) # setting Duty to 0 (speed)
        time.sleep(0.5)
        self.write_register( self.PWM_EN_REG_ADDR, 1) #enabling engine
        print("->>> POWERING UP...")
        time.sleep(0.5)
        print("->>> ENGINE ENABLED\n******************\n")
        time.sleep(1)

    def calc_crc(self,data: bytes) -> bytes:
        crc = 0xFFFF
        for pos in data:
            crc ^= pos
            for _ in range(8):
                if (crc & 0x0001) != 0:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        # The Arduino code (from the documentation website) swapped the bytes here
        crc = ((crc & 0x00FF) << 8) | ((crc & 0xFF00) >> 8)
        return crc.to_bytes(2, 'big')

    def write_register(self, reg_addr: int, value: int):
        frame = bytearray()
        frame.append(self.DEV_ADDR)
        frame.append(0x06)  # Write Single Register
        frame.extend(reg_addr.to_bytes(2, 'big'))
        frame.extend(value.to_bytes(2, 'big'))
        crc = self.calc_crc(frame)
        frame.extend(crc)
        print("Sending value:", value)
        self.ser.write(frame)

    def send_speed(self, speed):
        speed_index = (int(speed * self.inv_speed_incremental))
        self.write_register( self.DUTY_REG_ADDR, self.speed_values[speed_index])

    def send_formatted_speed(self, speed_index:int):
        self.write_register(self.DUTY_REG_ADDR, self.speed_values[speed_index])
    
    def shutdown_engine(self):
        self.write_register(self.DUTY_REG_ADDR, 0) #zero speed
        time.sleep(1)
        print("->>> POWERING DOWN...")
        self.write_register( self.PWM_EN_REG_ADDR, 0) #disable engine
        print("->>> ENGINE OFF\n**************\n")

    def terminate_serial_connection(self):
        time.sleep(1)
        self.ser.close()
        print("->>> CONNECTION TERMINATED")

if __name__ == "__main__":
    driver = MotorDriver()

    time.sleep(1)

    driver.send_formatted_speed(1)

    time.sleep(3)

    driver.send_formatted_speed(9)

    time.sleep(3)

    driver.send_formatted_speed(3)

    time.sleep(2)

    driver.send_formatted_speed(0)

    driver.shutdown_engine()
    driver.terminate_serial_connection()

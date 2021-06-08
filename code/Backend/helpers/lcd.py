from RPi import GPIO
import time

lcd_rs = 21
lcd_e = 20
lijst_pinnen = [16, 12, 25, 24, 23, 26, 19, 13]


class LCDRepository:
    def __init__(self, rs_pin=lcd_rs, e_pin=lcd_e, pinnen=lijst_pinnen):
        self.rs_pin = rs_pin
        self.e_pin = e_pin
        self.pinnen = pinnen
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.e_pin, GPIO.OUT)
        GPIO.setup(self.rs_pin, GPIO.OUT)
        for pin in self.pinnen:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.output(self.e_pin, GPIO.HIGH)

    def write_message(self, message):
        for letter in message:
            ascii_letter = ord(letter)
            self.send_character(ascii_letter)
            time.sleep(0.1)

    def cursor_on(self):
        self.send_instruction(0x0E)

    def set_data_bits(self, value):
        mask = 0x1
        for i in range(0, 8):
            pin = self.pinnen[i]
            if value & mask:
                GPIO.output(pin, GPIO.HIGH)
            else:
                GPIO.output(pin, GPIO.LOW)
            mask = mask << 1

    def send_instruction(self, value):
        GPIO.output(self.rs_pin, GPIO.LOW)
        self.set_data_bits(value)
        GPIO.output(self.e_pin, GPIO.LOW)
        GPIO.output(self.e_pin, GPIO.HIGH)
        time.sleep(0.01)

    def send_character(self, value):
        GPIO.output(self.rs_pin, GPIO.HIGH)
        self.set_data_bits(value)
        GPIO.output(self.e_pin, GPIO.LOW)
        GPIO.output(self.e_pin, GPIO.HIGH)
        time.sleep(0.01)

    def init_lcd(self):
        self.send_instruction(0x38)
        self.send_instruction(0x0f)
        self.send_instruction(0x01)

    def new_line(self):
        self.send_instruction(0xC0)

    # old, there's auto_scroll now
    def auto_line(self, message):
        length = 0
        for letter in message:
            length += 1
            ascii_letter = ord(letter)
            self.send_character(ascii_letter)
            if length == 16:
                self.new_line()
            time.sleep(0.1)

    def auto_scroll(self, message):
        length = 0
        for letter in message:
            length += 1

            ascii_letter = ord(letter)
            self.send_character(ascii_letter)
            if length == 16:
                self.new_line()
            if length % 16 == 0 and length >= 32:
                time.sleep(0.1)
                line1 = message[length-16:length]
                self.init_lcd()
                for letter in line1:
                    ascii_letter = ord(letter)
                    self.send_character(ascii_letter)
                self.new_line()
            time.sleep(0.1)

    def clear_screen(self):
        self.send_instruction(0x01)


def main():
    try:
        lcd = LCDRepository()
        lcd.init_lcd()
        lcd.write_message('This is')
        lcd.new_line()
        lcd.write_message('literally 1984  ')
        # lcd.auto_scroll(
        #     "This is literally 1984 as written by the author Gregorius Orwil Animal Fram Carol Marks")

    except KeyboardInterrupt as e:
        print(e)
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()

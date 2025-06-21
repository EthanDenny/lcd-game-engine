from RPLCD.i2c import CharLCD

lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
              cols=16, rows=2, dotsize=8,
              charmap='A00', auto_linebreaks=False)

alien_char = [
    0b00100,
    0b01110,
    0b10101,
    0b11111,
    0b01110,
    0b00100,
    0b01010,
    0b10001
]

lcd.create_char(0, alien_char)
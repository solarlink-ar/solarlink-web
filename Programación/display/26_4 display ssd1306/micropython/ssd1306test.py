from machine import Pin, I2C
from ssd1306_setup import setup
from writer import Writer
import ssd1306, freesans20

ssd = setup(use_spi = False, soft=False)
wri = Writer(ssd, freesans20)
Writer.set_textpos(ssd, 0, 0)
wri.printstring('Sunday\n')
ssd.show()









'''
# using default address 0x3C
i2c = I2C(1, sda=Pin(21), scl=Pin(22), freq = 400000)
display = ssd1306.SSD1306_I2C(128, 64, i2c) #display 128x64 init

fbuf = framebuf.FrameBuffer(bytearray(128 * 64 * 1), 88, 8, framebuf.MONO_VLSB) #framebuffer del tamaño de la pantalla
fbuf.text('Hello', 0, 0) #preparo un hello en el framebuf.
display.blit(fbuf, 0, 0, 0) #paso el hello en framebuf. al formato display en la ubicación deseada
display.show() #print
fbuf.text('Hello', 50, 50)
display.blit(fbuf, 50, 50, 0)
display.show()

'''
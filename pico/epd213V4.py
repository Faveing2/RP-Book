from machine import Pin, SPI
import framebuf
import utime
from time import ticks_us

EPD_WIDTH = 122
EPD_HEIGHT = 250

SPI_BAUD = 10_000_000

RST_PIN = 12
DC_PIN = 8
CS_PIN = 9
BUSY_PIN = 13

CUSTOM_LUT = False ### Very experimental, False for defaults

# Commands to control the epd driver
DRIVER_OUTPUT_SETTING = 0x01
GATE_DRIVE_SETTING = 0x03
SOURCE_DRIVE_VOLTAGE = 0x04
INIT_CODE_SETTING = 0x08
WRITE_INIT_CODE_SETTING = 0x09
READ_INITIAL_CODE_SETTING = 0x0a
BOOSTER_SOFT_START = 0x0c
DEEP_SLEEP_MODE = 0x10
DATA_ENTRY_MODE = 0x11
SW_RESET = 0x12
HV_READY_DETECT = 0x14
VCI_DETECTION = 0x15
TEMP_SENSOR_CONTROL = 0x18
WRITE_TEMP_SENSOR_REG = 0x1a
READ_TEMP_SENSOR_REG = 0x1b
WRITE_EXTERNAL_TEMP_SENSOR = 0x1c
MASTER_ACTIVATION = 0x20
DISPLAY_UPDATE_CONTROL_1 = 0x21
DISPLAY_UPDATE_CONTROL_2 = 0x22
WRITE_BW_RAM = 0x24
WRITE_RED_RAM = 0x26
READ_RAM = 0x27
VCOM_SENSE = 0x28
VCOM_SENSE_DURATION = 0x29
PROGRAM_VCOM_OTP = 0x2a
WRITE_VCOM_CONTROL = 0x2b
WRITE_VCOM = 0x2c
OTP_REG_READ = 0x2d
READ_USER_ID = 0x2e
READ_STATUS_BIT = 0x2f
BORDER_WAVEFORM = 0x3c
WRITE_LUT_REG = 0x32
EOPT_LUT = 0x3f
SET_RAM_X = 0x44
SET_RAM_Y = 0x45
SET_RAM_X_CURSOR = 0x4e
SET_RAM_Y_CURSOR = 0x4f

### Parameters
PARTIAL_LUT_DISPLAY_MODE = 0xC7


MODE_FULL = 0
MODE_FAST = 1
MODE_PARTIAL = 2

### LUT profiles copied from waveshare V3 driver (Documentation says they should be compatible?)
lut_partial_update = bytearray([
    0x0,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x80,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x40,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x05,0x0,0x0,0x0,0x0,0x0,0x0,  
    0x1,0x0,0x0,0x0,0x0,0x0,0x0,
    0x1,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0x0,0x0,0x0,0x0,0x0,0x0,0x0,
    0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0x0,0x0,0x0,
    0x22,0x17,0x41,0x00,0x32,0x36,
])

# lut_partial_update = bytearray([
#         0x0,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,# VS[LUT0]
#         0x80,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,# VS[LUT1]
#         0x40,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,# VS[LUT2]
#         0x0,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,# VS[LUT3]
#         0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,# VS[LUT4]
#         0x1,0x0,0x0,0x0,0x0,0x0,0x0, #Timing 0A Group 
#         0x0,0x0,0x0,0x0,0x0,0x0,0x0, #Timing 1A-b Group
#         0x0,0x0,0x0,0x0,0x0,0x0,0x0, #Timing 2 Group
#         0x0,0x0,0x0,0x0,0x0,0x0,0x0, #Timing 3 Group
#         0x0,0x0,0x0,0x0,0x0,0x0,0x0, #Timing 4 Group
#         0x0,0x0,0x0,0x0,0x0,0x0,0x0,
#         0x0,0x0,0x0,0x0,0x0,0x0,0x0,
#         0x0,0x0,0x0,0x0,0x0,0x0,0x0,
#         0x0,0x0,0x0,0x0,0x0,0x0,0x0,
#         0x0,0x0,0x0,0x0,0x0,0x0,0x0,
#         0x0,0x0,0x0,0x0,0x0,0x0,0x0,
#         0x0,0x0,0x0,0x0,0x0,0x0,0x0,
#         0x07,0x00,0x00,0x00,0x00,0x00,0x0,0x0,0x0, # FR values 0-7, last 3 bytes are XDN
#         0x22,0x17,0x41,0x00,0x32,0x36
# ])

#lut_partial_update = bytearray([0x0]*153)

# Settings that were added to the end of lut_partial_update
lut_partial_settings = bytearray([0x22,0x17,0x41,0x00,0x32,0x36])

lut_full_update = bytearray([ 
        0x80,0x4A,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x40,0x4A,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x80,0x4A,0x40,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x40,0x4A,0x80,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0xF,0x0,0x0,0x0,0x0,0x0,0x0,
        0xF,0x0,0x0,0xF,0x0,0x0,0x2,
        0xF,0x0,0x0,0x0,0x0,0x0,0x0,
        0x1,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x0,0x0,0x0,0x0,0x0,0x0,0x0,
        0x22,0x22,0x22,0x22,0x22,0x22,0x0,0x0,0x0,
        0x22,0x17,0x41,0x00,0x32,0x36
])

#lut_partial_update = lut_full_update[:]

lut_full_settings = bytearray([0x22,0x17,0x41,0x00,0x32,0x36])

class epd213v4:

    def __init__(self, mode:int):

        self.mode = mode

        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)

        if EPD_WIDTH % 8 == 0:
            self.width = EPD_WIDTH
        else :
            self.width = (EPD_WIDTH // 8) * 8 + 8
        self.height = EPD_HEIGHT

        self.spi = SPI(1)
        self.spi.init(baudrate=SPI_BAUD)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)

        self.frame_buf = bytearray(self.height * self.width // 8)
        self.old_frame_buf = bytearray(self.height * self.width // 8)

        self.frame = framebuf.FrameBuffer(self.frame_buf, self.height, self.width, framebuf.MONO_VLSB)
        self.old_frame = framebuf.FrameBuffer(self.old_frame_buf, self.height, self.width, framebuf.MONO_VLSB)

        self.old_frame.fill(0x00) # Fill with white so first partial refresh works correctly

        self.white = bytearray([0x00]*(self.height * self.width // 8))

        self.tx_buf = bytearray(self.height * self.width // 8) # Buffer that will hold data to be send to the screen

        self.init_screen()

    def init_screen(self):
        self.reset()
        self.readBusy()
        self.sendCommand(SW_RESET)
        self.readBusy()

        self.sendCommand(DRIVER_OUTPUT_SETTING)
        self.sendData(0xf9)
        self.sendData(0x00)
        self.sendData(0x00)

        self.sendCommand(DATA_ENTRY_MODE)
        self.sendData(0x07)

        self.setWindow(0,0, self.width-1, self.height-1)
        self.setCursor(0,0)

        self.sendCommand(BORDER_WAVEFORM)
        self.sendData(0x05)

        self.sendCommand(TEMP_SENSOR_CONTROL)
        self.sendData(0x80)

        self.sendCommand(DISPLAY_UPDATE_CONTROL_1)
        self.sendData(0x80)
        self.sendData(0x80)

        self.sendCommand(WRITE_TEMP_SENSOR_REG) # Write temp register
        self.sendData(0x64)
        self.sendData(0x00)

        if CUSTOM_LUT:
            self.sendCommand(EOPT_LUT)
            self.sendData(lut_partial_settings[0])
            self.sendCommand(GATE_DRIVE_SETTING)
            self.sendData(lut_partial_settings[1])
            self.sendCommand(SOURCE_DRIVE_VOLTAGE)
            self.sendData(lut_partial_settings[2])
            self.sendData(lut_partial_settings[3])
            self.sendData(lut_partial_settings[4])
            self.sendCommand(WRITE_VCOM)
            self.sendData(lut_partial_settings[5])

            # self.sendCommand(BOOSTER_SOFT_START)
            # self.sendData(0xEF)
            # self.sendData(0xEF)
            # self.sendData(0xEF)
            # self.sendData(0x00)

            # self.sendCommand(HV_READY_DETECT)
            # self.sendData(0x11)
        return 0

    def write_lut(self):

        start = ticks_us()

        if self.mode == MODE_FULL:
            self.sendCommand(WRITE_LUT_REG)
            self.dc_pin.value(1)
            self.cs_pin.value(0)
            self.spi.write(lut_full_update)
            self.cs_pin.value(1)
            self.readBusy()

            self.sendCommand(EOPT_LUT)
            self.sendData(lut_full_settings[0])
            self.sendCommand(GATE_DRIVE_SETTING)
            self.sendData(lut_full_settings[1])
            self.sendCommand(SOURCE_DRIVE_VOLTAGE)
            self.sendData(lut_full_settings[2])
            self.sendData(lut_full_settings[3])
            self.sendData(lut_full_settings[4])
            self.sendCommand(WRITE_VCOM)
            self.sendData(lut_full_settings[5])
        elif self.mode == MODE_PARTIAL:
            self.sendCommand(WRITE_LUT_REG)
            self.dc_pin.value(1)
            self.cs_pin.value(0)
            self.spi.write(lut_partial_update)
            self.cs_pin.value(1)
            #self.readBusy()
        elif self.mode == MODE_FAST:
            return 0 # No LUT for fast mode rn

        print("Write LUT:", ticks_us()-start)

    def setWindow(self, Xstart, Ystart, Xend, Yend):
        self.sendCommand(SET_RAM_X)
        self.sendData((Xstart>>3) & 0xFF)
        self.sendData((Xend>>3) & 0xFF)

        self.sendCommand(SET_RAM_Y)
        self.sendData(Ystart & 0xFF)
        self.sendData((Ystart >> 8) & 0xFF)
        self.sendData(Yend & 0xFF)
        self.sendData((Yend >> 8) & 0xFF)

    def setCursor(self, Xstart, Ystart):
        self.sendCommand(SET_RAM_X_CURSOR) # SET_RAM_X_ADDRESS_COUNTER
        self.sendData(Xstart & 0xFF)

        self.sendCommand(SET_RAM_Y_CURSOR) # SET_RAM_Y_ADDRESS_COUNTER
        self.sendData(Ystart & 0xFF)
        self.sendData((Ystart >> 8) & 0xFF)

    def sendCommand(self, command):
        self.dc_pin.value(0)
        self.cs_pin.value(0)
        self.spi.write(bytearray([command]))
        self.cs_pin.value(1)

    def sendData(self, data):
        self.dc_pin.value(1)
        self.cs_pin.value(0)
        self.spi.write(bytearray([data]))
        self.cs_pin.value(1)

    def readBusy(self):
        while(self.busy_pin.value() == 1): 
            utime.sleep(0.001)
        print('busy release')
        #utime.sleep(20/1000)

    def reset(self):
        self.reset_pin.value(1)
        utime.sleep(50/1000)
        self.reset_pin.value(0)
        utime.sleep(2/1000)
        self.reset_pin.value(1)
        utime.sleep(50/1000)

    @micropython.native
    def display(self, full=False):

        start = ticks_us()

        if CUSTOM_LUT:
            self.write_lut()

        if (self.mode==MODE_FULL):
            self.sendCommand(WRITE_BW_RAM)
            self.transfer_fb()
            self.sendCommand(DISPLAY_UPDATE_CONTROL_2)
            self.sendData(0xc7)
        elif (self.mode==MODE_FAST) or (full==True):
            self.sendCommand(WRITE_BW_RAM)
            self.transfer_fb()
            if full:
                self.sendCommand(WRITE_RED_RAM)
                self.transfer_fb()
            self.sendCommand(DISPLAY_UPDATE_CONTROL_2)
            self.sendData(0xf7)
        elif self.mode==MODE_PARTIAL:


            self.sendCommand(DISPLAY_UPDATE_CONTROL_2)
            if CUSTOM_LUT:
                self.sendData(PARTIAL_LUT_DISPLAY_MODE) ### FROM V3 Driver may not work?
            else:
                self.sendData(0xff)

            # if CUSTOM_LUT:
            #     self.sendCommand(0x37);
            #     self.sendData(0x00);
            #     self.sendData(0x00);
            #     self.sendData(0x00);
            #     self.sendData(0x00);
            #     self.sendData(0x00);
            #     self.sendData(0x40); # Set ram ping pong mode
            #     self.sendData(0x00);
            #     self.sendData(0x00);
            #     self.sendData(0x00);
            #     self.sendData(0x00);

            
            self.sendCommand(WRITE_BW_RAM)
            self.transfer_fb()
            self.sendCommand(WRITE_RED_RAM)
            self.transfer_old_fb()

            #self.old_frame_buf = self.frame_buf[:]
            
            print("Transfer finished:", ticks_us()-start)

        self.turnOnDisplay()

        print("Render time:",ticks_us()-start)


    def display_partial(self): ### Experimental function

        self.temp_buf = self.frame_buf
        for i in range(self.height * self.width // 8):
            #self.frame_buf[i] |= self.old_frame_buf[i]
            self.old_frame_buf[i] |= self.frame_buf[i]

        self.sendCommand(WRITE_BW_RAM)
        self.transfer_fb()
        self.sendCommand(WRITE_RED_RAM)
        self.transfer_old_fb()

        self.sendCommand(DISPLAY_UPDATE_CONTROL_2)
        self.sendData(0xff)

        self.turnOnDisplay()

        self.old_frame_buf = self.temp_buf

    def turnOnDisplay(self):
        self.sendCommand(MASTER_ACTIVATION)
        self.readBusy()

    def sleep(self):
        self.sendCommand(DEEP_SLEEP_MODE)
        self.sendData(0x10)

        self.reset_pin.value(0)

    @micropython.native
    def transfer_fb(self):
        # Gods most optimized python function
        width = self.width
        height = self.height
        dc_pin = self.dc_pin.value
        cs_pin = self.cs_pin.value
        spi = self.spi.write
        framebufer = self.frame_buf
        txbuffer = self.tx_buf
        dc_pin(1)
        cs_pin(0)

        for j in range(width // 8):
            src = (width // 8 - 1 - j) * height
            dst = j * height
            txbuffer[dst:dst + height] = framebufer[src:src + height]

        spi(txbuffer)
        cs_pin(1)

    @micropython.native
    def transfer_old_fb(self):
        # Gods most optimized python function
        width = self.width
        height = self.height
        dc_pin = self.dc_pin.value
        cs_pin = self.cs_pin.value
        spi = self.spi.write
        old_framebuffer = self.old_frame_buf
        txbuffer = self.tx_buf
        whitebuf = self.white
        dc_pin(1)
        cs_pin(0)

        # for j in range(width // 8):
        #     src = (width // 8 - 1 - j) * height
        #     dst = j * height
        #     txbuffer[dst:dst + height] = old_framebuffer[src:src + height]

        #spi(txbuffer)
        spi(whitebuf)
        cs_pin(1) 

if __name__ == "__main__":
    display = epd213v4(MODE_PARTIAL)
    # display = epd.epd213v4(epd.MODE_PARTIAL)
    # display = epd.epd213v4(epd.MODE_FULL)
    # display = epd.epd213v4(epd.MODE_FAST)
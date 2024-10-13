# imports
import sht31 # temp/humidity sensor
from machine import Pin, I2C, PWM # import i2c and pin
import socket # for wifi comms
import time
from chamber_pid import PID

# timer
from machine import Timer
tim1 = Timer(-1)
tim2 = Timer(-1)
tim3 = Timer(-1)
tim4 = Timer(-1)
tim5 = Timer(-1)

# pin definition
p5           = Pin(5, Pin.OUT, Pin.PULL_UP) # define pins for sensors
p4           = Pin(4, Pin.OUT, Pin.PULL_UP) # and use internal pullup

air_circ_fan = Pin(13, Pin.OUT) # air circulation fan pins

mister       = Pin(14, Pin.OUT) # mister pin
mister_fan_pin   = Pin(12, Pin.OUT) # mister fan pin
# mister_fan_pwm = PWM(mister_fan_pin, 1)


daylight_led = Pin(15, Pin.OUT) # daylight pin
uvc_led      = Pin(3, Pin.OUT) # uvc pin

# start i2c at 40 kHz
i2c = I2C(scl=p5, sda=p4, freq=40000)

# define sensors
sensor_top = sht31.SHT31(i2c, addr=0x44)
sensor_bot = sht31.SHT31(i2c, addr=0x45)

# network stuff
HOST = "100.64.13.204"  # server ip address (receiving computer)
PORT = 4444  # port used by server

# init sensor data
data = b''
th_measurement_top = b''
th_measurement_bot = b''

def get_th_measurment():
    global th_measurement_top
    global th_measurement_bot

    th_measurement_top = sensor_top.get_temp_humi_bytes()
    th_measurement_bot = sensor_bot.get_temp_humi_bytes()

def send_th_measurement(c):
    gc.collect()
    # call get measurements
    get_th_measurment()

    # send measurements
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((HOST, PORT))
        s.settimeout(10)
        print('sending temperature...')
        s.sendall(th_measurement_top + th_measurement_bot)
        s.close()
    except OSError:
        print('unable to reach base station, data not sent.')

def get_humidity_control(pd) -> int:
    get_th_measurment()
    
    top_th_decoded = sht31.decode_raw_temp_humi(th_measurement_top)
    bot_th_decoded = sht31.decode_raw_temp_humi(th_measurement_bot)

    measured_humidity = min(top_th_decoded[1], bot_th_decoded[1])

    command = int(pd.get_control_saturated(measured_humidity))
    return command

def regulate_humidity(pd):
    try:
        calculated_command = get_humidity_control(pd)
    except:
        print('cannot get sensor data...')
        calculated_command = 30
    
    print('turning on mister for', calculated_command, 'seconds')
    
    mister.on()
    uvc_led.on()
    mister_fan_pin.on()
    time.sleep(calculated_command)
    mister_fan_pin.off()
    mister.off()

def circulate_air(c):
    # air circulation timer
    AIR_CIRCULATION_DELAY = 480000
    
    f = open('last_air_circ.txt')
    
    last_air_circ = int(f.read())
    time_since_last_air_circ = int(time.time()) - last_air_circ
    
    f.close()
    
    if (time_since_last_air_circ > 14400):
        print('circulating air...')
        uvc_led.on()
        air_circ_fan.on()
        time.sleep(20)
        air_circ_fan.off()
        
        f_out = open('last_air_circ.txt', 'w')
        f_out.write(str(int(time.time())))
        f_out.flush()
        f_out.close()
        
    else:
        print('last circulated air', int(time_since_last_air_circ/60), 'm', time_since_last_air_circ % 60, 's ago')

def check_daylight(c):
    # the ntp clock is 4 hours ahead of EST
    seconds_elapsed_today = (time.time() - 3600*4) % 86400
    
    # 11 am to 5 pm
    if seconds_elapsed_today > (17*3600) and seconds_elapsed_today < (23*3600):
        daylight_led.on()
    else:
        daylight_led.off()
        
def activate_uvc_sterilize(c):
    four_hour_chunk = time.time() % (3600*4)
    
    if four_hour_chunk < 300:
        uvc_led.on()
    else:
        print('4 hour counter:', four_hour_chunk)
        uvc_led.off()


# MAIN CONTROL
HUMIDITY_COMMAND = 93

# init humidity PD control
pd = PID(7, 0.00, 0.5) # PD(Kp, Ki, Kd)
pd.set_operating_point(HUMIDITY_COMMAND)
pd.set_command_limit(0, 60)

# init timers
tim1.init(period=15000, mode=Timer.PERIODIC, callback=send_th_measurement)
tim2.init(period=180000, mode=Timer.PERIODIC, callback=circulate_air)
tim3.init(period=180000, mode=Timer.PERIODIC, callback=(lambda c: regulate_humidity(pd)))
tim4.init(period=180000, mode=Timer.PERIODIC, callback=check_daylight)
tim5.init(period=180000, mode=Timer.PERIODIC, callback=activate_uvc_sterilize)

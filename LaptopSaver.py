import asyncio
from kasa import Discover, SmartPlug, Module
from Adafruit_IO import Client
import serial
import time
from datetime import datetime
import subprocess
from gpiozero import RGBLED

# Adafruit IO Credentials
ADAFRUIT_IO_KEY = 'IT IS A SECRET'  
ADAFRUIT_IO_USERNAME = 'Also A SECRET'  
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Kasa Device IP and credentials
device_ip = "192.168.1.159"  
username = "brandon" 
password = "your_password"  

# UART (serial) Communication to the Pico
uart = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=1)

# Adafruit IO Feeds
power_feed = aio.feeds("power-feed")
voltage_feed = aio.feeds("voltage-feed")
power_toggle_feed = aio.feeds("power-toggle")
led = RGBLED(red=26, green=19, blue=13)
async def send_data_to_adafruit_io_and_pico():
    # Discover and connect to the Kasa device
    dev = await Discover.discover_single(device_ip, username=username, password=password)
    kasa = SmartPlug(device_ip)

    manual = False
    await kasa.update()
    while True:
        power_toggle = aio.receive(power_toggle_feed.key).value
        if power_toggle == "ON":
                await kasa.turn_on()
                manual = True
                print("Kasa switch turned ON via Adafruit")
        if power_toggle == "OFF":
            manual = False
        
                
                
        await dev.update()  # Refresh the data
        
        if dev.has_emeter:
            emeter_data = await dev.get_emeter_realtime()
            voltage = emeter_data.get("voltage_mv", 0) / 1000  # Convert mV to V
            power = emeter_data.get("power_mw", 0) / 1000  # Convert mW to W

            # Send data to Adafruit IO
            aio.send(power_feed.key, power)
            aio.send(voltage_feed.key, voltage)

            print(f"Sent to Adafruit: Power: {power}W, Voltage: {voltage}V")

            # Send data to Pico over UART
             message = f"{power:.2f}W,{voltage:.2f}V\n"
            uart.write(message.encode())
            uart.flush()
            print(f"Sent to Pico: {message.strip()}")

            # Write to CSV
            with open("KasaSmartPlugData.csv", "a") as dataFile:
                dataFile.write(f"{voltage:.2f} , V , {power:.2f}, W , {datetime.today().strftime('%h-%d-%Y %H:%M')} \n")

            if power < 20 and manual == False:
               await kasa.turn_off()
               
            
           # rclone to OneDrive
            subprocess.run("rclone copy /home/banaya7/Documents/Old_RP_Files/KasaSmartPlugData.csv sensor:", shell=True)
            if power > 0:
                led.color = (0,1,0)
            else:
                led.color = (1,0,0)

        else:
            print("Emeter not supported on this device.")
        
        # Wait 
        await asyncio.sleep(5)

#asyncio loop to keep sending data
if __name__ == "__main__":
    asyncio.run(send_data_to_adafruit_io_and_pico())

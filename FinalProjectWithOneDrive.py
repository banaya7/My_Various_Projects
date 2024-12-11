Python 3.12.3 (v3.12.3:f6650f9ad7, Apr  9 2024, 08:18:48) [Clang 13.0.0 (clang-1300.0.29.30)] on darwin
Type "help", "copyright", "credits" or "license()" for more information.
>>> WARNING: The system preference "Prefer tabs when opening documents" is set to
"Always". This will cause various problems with IDLE. For the best experience,
change this setting when running IDLE (via System Preferences -> Dock).
import asyncio
... from kasa import SmartPlug
... from datetime import datetime
... import subprocess
... 
... 
... async def get_voltage_and_usage():
...     device_ip = "192.168.1.159"
...     kasa = SmartPlug(device_ip)
... 
...     while True:
...         # Update the device state
...         await kasa.update()
... 
...         # Retrieve data
...         if kasa.has_emeter:
...             emeter_data = kasa.emeter_realtime
...             voltage = emeter_data.get("voltage_mv", 0) / 1000
...             power = emeter_data.get("power_mw", 0) / 1000
... 
...             # Print the voltage and power
...             print(f"Voltage: {voltage:.2f}V, Power: {power:.2f}W")
... 
...             # Write the voltage and power to the file
...             with open("KasaSmartPlugData.csv", "a") as dataFile:
...                 dataFile.write(f"{voltage:.2f} , V , {power:.2f}, W , {datetime.today().strftime('%h-%d-%Y %H:%M')} \n")
...             
...             # Sync the file to OneDrive
...             subprocess.run("rclone copy /home/banaya7/Documents/Python_Files/KasaSmartPlugData.csv remote:Sensor_Data", shell=True)
... 
...         else:
...             print("Error, not reading data.")
            return

        # update every 10 seconds
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(get_voltage_and_usage())


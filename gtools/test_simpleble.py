#! /usr/bin/env python3
# -*- coding: UTF-8 -*-


# import simplepyble

# if __name__ == "__main__":
#     print(f"Running on {simplepyble.get_operating_system()}")

#     adapters = simplepyble.Adapter.get_adapters()

#     if len(adapters) == 0:
#         print("No adapters found")

#     for adapter in adapters:
#         print(f"Adapter: {adapter.identifier()} [{adapter.address()}]")
# ################################################################################


# import simplepyble

# if __name__ == "__main__":
#     adapters = simplepyble.Adapter.get_adapters()

#     if len(adapters) == 0:
#         print("No adapters found")

#     # Query the user to pick an adapter
#     print("Please select an adapter:")
#     for i, adapter in enumerate(adapters):
#         print(f"{i}: {adapter.identifier()} [{adapter.address()}]")

#     choice = int(input("Enter choice: "))
#     adapter = adapters[choice]

#     print(f"Selected adapter: {adapter.identifier()} [{adapter.address()}]")

#     adapter.set_callback_on_scan_start(lambda: print("Scan started."))
#     adapter.set_callback_on_scan_stop(lambda: print("Scan complete."))
#     adapter.set_callback_on_scan_found(lambda peripheral: print(f"Found {peripheral.identifier()} [{peripheral.address()}]"))

#     # Scan for 5 seconds
#     adapter.scan_for(5000)

#     peripherals = adapter.scan_get_results()
#     print("The following peripherals were found:")
#     for peripheral in peripherals:
#         connectable_str = "Connectable" if peripheral.is_connectable() else "Non-Connectable"
#         print(f"{peripheral.identifier()} [{peripheral.address()}] - {connectable_str}")
#         print(f'    Address Type: {peripheral.address_type()}')
#         print(f'    Tx Power: {peripheral.tx_power()} dBm')

#         manufacturer_data = peripheral.manufacturer_data()
#         for manufacturer_id, value in manufacturer_data.items():
#             print(f"    Manufacturer ID: {manufacturer_id}")
#             print(f"    Manufacturer data: {value}")

#         services = peripheral.services()
#         for service in services:
#             print(f"    Service UUID: {service.uuid()}")
#             print(f"    Service data: {service.data()}")

# # ################################################################################

# import simplepyble

# if __name__ == "__main__":
#     adapters = simplepyble.Adapter.get_adapters()

#     if len(adapters) == 0:
#         print("No adapters found")

#     # Query the user to pick an adapter
#     print("Please select an adapter:")
#     for i, adapter in enumerate(adapters):
#         print(f"{i}: {adapter.identifier()} [{adapter.address()}]")

#     choice = int(input("Enter choice: "))
#     adapter = adapters[choice]

#     print(f"Selected adapter: {adapter.identifier()} [{adapter.address()}]")

#     adapter.set_callback_on_scan_start(lambda: print("Scan started."))
#     adapter.set_callback_on_scan_stop(lambda: print("Scan complete."))
#     adapter.set_callback_on_scan_found(lambda peripheral: print(f"Found {peripheral.identifier()} [{peripheral.address()}]"))

#     # Scan for 5 seconds
#     adapter.scan_for(5000)
#     peripherals = adapter.scan_get_results()

#     # Query the user to pick a peripheral
#     print("Please select a peripheral:")
#     for i, peripheral in enumerate(peripherals):
#         print(f"{i}: {peripheral.identifier()} [{peripheral.address()}]")

#     choice = int(input("Enter choice: "))
#     peripheral = peripherals[choice]

#     print(f"Connecting to: {peripheral.identifier()} [{peripheral.address()}]")
#     peripheral.connect()

#     print("Successfully connected, listing services...")
#     services = peripheral.services()
#     for service in services:
#         print(f"Service: {service.uuid()}")
#         for characteristic in service.characteristics():
#             print(f"    Characteristic: {characteristic.uuid()}")

#     peripheral.disconnect()


# ################################################################################


# import simplepyble

# if __name__ == "__main__":
#     adapters = simplepyble.Adapter.get_adapters()

#     if len(adapters) == 0:
#         print("No adapters found")

#     # Query the user to pick an adapter
#     print("Please select an adapter:")
#     for i, adapter in enumerate(adapters):
#         print(f"{i}: {adapter.identifier()} [{adapter.address()}]")

#     choice = int(input("Enter choice: "))
#     adapter = adapters[choice]

#     print(f"Selected adapter: {adapter.identifier()} [{adapter.address()}]")

#     adapter.set_callback_on_scan_start(lambda: print("Scan started."))
#     adapter.set_callback_on_scan_stop(lambda: print("Scan complete."))
#     adapter.set_callback_on_scan_found(lambda peripheral: print(f"Found {peripheral.identifier()} [{peripheral.address()}]"))

#     # Scan for 5 seconds
#     adapter.scan_for(5000)
#     peripherals = adapter.scan_get_results()

#     # Query the user to pick a peripheral
#     print("Please select a peripheral:")
#     for i, peripheral in enumerate(peripherals):
#         print(f"{i}: {peripheral.identifier()} [{peripheral.address()}]")

#     choice = int(input("Enter choice: "))
#     peripheral = peripherals[choice]

#     print(f"Connecting to: {peripheral.identifier()} [{peripheral.address()}]")
#     peripheral.connect()

#     print("Successfully connected, listing services...")
#     services = peripheral.services()
#     service_characteristic_pair = []
#     for service in services:
#         for characteristic in service.characteristics():
#             service_characteristic_pair.append((service.uuid(), characteristic.uuid()))

#     # Query the user to pick a service/characteristic pair
#     print("Please select a service/characteristic pair:")
#     for i, (service_uuid, characteristic) in enumerate(service_characteristic_pair):
#         print(f"{i}: {service_uuid} {characteristic}")

#     choice = int(input("Enter choice: "))
#     service_uuid, characteristic_uuid = service_characteristic_pair[choice]

#     # Write the content to the characteristic
#     contents = peripheral.read(service_uuid, characteristic_uuid)
#     print(f"Contents: {contents}")

#     peripheral.disconnect()


# # ################################################################################

# import simplepyble

# if __name__ == "__main__":
#     adapters = simplepyble.Adapter.get_adapters()

#     if len(adapters) == 0:
#         print("No adapters found")

#     # Query the user to pick an adapter
#     print("Please select an adapter:")
#     for i, adapter in enumerate(adapters):
#         print(f"{i}: {adapter.identifier()} [{adapter.address()}]")

#     choice = int(input("Enter choice: "))
#     adapter = adapters[choice]

#     print(f"Selected adapter: {adapter.identifier()} [{adapter.address()}]")

#     adapter.set_callback_on_scan_start(lambda: print("Scan started."))
#     adapter.set_callback_on_scan_stop(lambda: print("Scan complete."))
#     adapter.set_callback_on_scan_found(lambda peripheral: print(f"Found {peripheral.identifier()} [{peripheral.address()}]"))

#     # Scan for 5 seconds
#     adapter.scan_for(5000)
#     peripherals = adapter.scan_get_results()

#     # Query the user to pick a peripheral
#     print("Please select a peripheral:")
#     for i, peripheral in enumerate(peripherals):
#         print(f"{i}: {peripheral.identifier()} [{peripheral.address()}]")

#     choice = int(input("Enter choice: "))
#     peripheral = peripherals[choice]

#     print(f"Connecting to: {peripheral.identifier()} [{peripheral.address()}]")
#     peripheral.connect()

#     print("Successfully connected, listing services...")
#     services = peripheral.services()
#     service_characteristic_pair = []
#     for service in services:
#         for characteristic in service.characteristics():
#             service_characteristic_pair.append((service.uuid(), characteristic.uuid()))

#     # Query the user to pick a service/characteristic pair
#     print("Please select a service/characteristic pair:")
#     for i, (service_uuid, characteristic) in enumerate(service_characteristic_pair):
#         print(f"{i}: {service_uuid} {characteristic}")

#     choice = int(input("Enter choice: "))
#     service_uuid, characteristic_uuid = service_characteristic_pair[choice]

#     # Query the user for content to write
#     content = input("Enter content to write: ")

#     # Write the content to the characteristic
#     # Note: `write_request` required the payload to be presented as a bytes object.
#     peripheral.write_request(service_uuid, characteristic_uuid, str.encode(content))

#     peripheral.disconnect()


# # ################################################################################

# import simplepyble
# import time

# if __name__ == "__main__":
#     adapters = simplepyble.Adapter.get_adapters()

#     if len(adapters) == 0:
#         print("No adapters found")

#     # Query the user to pick an adapter
#     print("Please select an adapter:")
#     for i, adapter in enumerate(adapters):
#         print(f"{i}: {adapter.identifier()} [{adapter.address()}]")

#     choice = int(input("Enter choice: "))
#     adapter = adapters[choice]

#     print(f"Selected adapter: {adapter.identifier()} [{adapter.address()}]")

#     adapter.set_callback_on_scan_start(lambda: print("Scan started."))
#     adapter.set_callback_on_scan_stop(lambda: print("Scan complete."))
#     adapter.set_callback_on_scan_found(lambda peripheral: print(f"Found {peripheral.identifier()} [{peripheral.address()}]"))

#     # Scan for 5 seconds
#     adapter.scan_for(5000)
#     peripherals = adapter.scan_get_results()

#     # Query the user to pick a peripheral
#     print("Please select a peripheral:")
#     for i, peripheral in enumerate(peripherals):
#         print(f"{i}: {peripheral.identifier()} [{peripheral.address()}]")

#     choice = int(input("Enter choice: "))
#     peripheral = peripherals[choice]

#     print(f"Connecting to: {peripheral.identifier()} [{peripheral.address()}]")
#     peripheral.connect()

#     print("Successfully connected, listing services...")
#     services = peripheral.services()
#     service_characteristic_pair = []
#     for service in services:
#         for characteristic in service.characteristics():
#             service_characteristic_pair.append((service.uuid(), characteristic.uuid()))

#     # Query the user to pick a service/characteristic pair
#     print("Please select a service/characteristic pair:")
#     for i, (service_uuid, characteristic) in enumerate(service_characteristic_pair):
#         print(f"{i}: {service_uuid} {characteristic}")

#     choice = int(input("Enter choice: "))
#     service_uuid, characteristic_uuid = service_characteristic_pair[choice]

#     # Write the content to the characteristic
#     contents = peripheral.notify(service_uuid, characteristic_uuid, lambda data: print(f"Notification: {data}"))

#     time.sleep(5)

#     peripheral.disconnect()

# # ################################################################################

# # Notification

# import simplepyble
# import time

# def main():
#     global peripheral

#     adapters = simplepyble.Adapter.get_adapters()
#     adapter  = adapters[0] # I have only 1
#     print(f"Selected adapter: {adapter.identifier()} [{adapter.address()}]")

#     adapter.set_callback_on_scan_start(lambda: print("Scan started."))
#     adapter.set_callback_on_scan_stop (lambda: print("Scan complete."))
#     adapter.set_callback_on_scan_found(lambda peripheral: print(f"Found {peripheral.identifier()} [{peripheral.address()}]"))

#     # Scan for N milliseconds
#     adapter.scan_for(1000)
#     peripherals = adapter.scan_get_results()

#     for i, peripheral in enumerate(peripherals):
#         if peripheral.identifier() == "BDM":
#             peripheral = peripherals[i]
#             break

#     print(f"Connecting to: {peripheral.identifier()} [{peripheral.address()}]")
#     peripheral.connect()

#     services = peripheral.services()
#     service_characteristic_pair = []
#     for service in services:
#         for characteristic in service.characteristics():
#             service_characteristic_pair.append((service.uuid(), characteristic.uuid()))

#     for choice in range(7, 8):
#         print("Option: ", choice)
#         try:
#             service_uuid, characteristic_uuid = service_characteristic_pair[choice]
#             # Write the content to the characteristic
#             contents = peripheral.notify(service_uuid, characteristic_uuid, lambda data: print(f"{time.time()} Notification: {data}"))
#         except Exception as e:
#             print(e)

#         time.sleep(5)


#     # for choice in range(0, 10):
#     #     print("Option: ", choice)
#     #     try:
#     #         service_uuid, characteristic_uuid = service_characteristic_pair[choice]
#     #         contents = peripheral.read(service_uuid, characteristic_uuid)
#     #         print(f"Contents: {contents}")
#     #         # Write the content to the characteristic
#     #         # contents = peripheral.notify(service_uuid, characteristic_uuid, lambda data: print(f"{time.time()} Notification: {data}"))
#     #     except Exception as e:
#     #         print(e)

#     #     time.sleep(5)



# if __name__ == "__main__":
#     global peripheral

#     try:
#         main()
#     except KeyboardInterrupt as e:
#         print()
#         print(e)

#     peripheral.disconnect()








##########################################################################################################################

# Notification

import simplepyble
import time
import datetime         as dt

peripheral = None
lasttime   = None

def longstime():
    """Return current time as YYYY-MM-DD HH:MM:SS.mmm, (mmm = millisec)"""
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # ms resolution


def main():
    global peripheral, lasttime

    adapters = simplepyble.Adapter.get_adapters()
    adapter  = adapters[0] # I have only 1
    print(f"Selected adapter: {adapter.identifier()} [{adapter.address()}]")

    adapter.set_callback_on_scan_start(lambda: print("Scan started."))
    adapter.set_callback_on_scan_stop (lambda: print("Scan complete."))
    adapter.set_callback_on_scan_found(lambda peripheral: print(f"Found {peripheral.identifier()} [{peripheral.address()}]"))

    adapter.scan_for(1000)                      # Scan for N milliseconds
    peripherals = adapter.scan_get_results()

    BDMfound = False
    for peripheral in peripherals:
        if peripheral.identifier() == "BDM":
            BDMfound = True
            break

    if not BDMfound:
        print( "Peripheral BDM not found - exiting")
        return

    print(f"Connecting to: {peripheral.identifier()} [{peripheral.address()}]")
    peripheral.connect()

    services = peripheral.services()
    service_characteristic_pair = []
    for service in services:
        for characteristic in service.characteristics():
            service_characteristic_pair.append((service.uuid(), characteristic.uuid()))

    lasttime = time.time()
    try:
        choice = 7
        service_uuid, characteristic_uuid = service_characteristic_pair[choice]
        # contents = peripheral.notify(service_uuid, characteristic_uuid, lambda data: print(f"{time.time()} Notification: {data}"))
        contents = peripheral.notify(service_uuid, characteristic_uuid, printStuff)
        print("contents: ", contents)
    except Exception as e:
        print(e)

    while True: time.sleep(1)     # stop with CTRL C


def printStuff(data):
    # print(f"{time.time():0.8f} Notification: {data}", end="   ")

    global lasttime

    defname = "printStuff: "

    nowtime   = time.time()
    durtime = 1000 * (nowtime - lasttime)
    print(f"{longstime()} {defname}Dur:{durtime:3.0f} ms  OW18E:'{data.hex(' ')}'", end = "  ")
    lasttime = nowtime

    # Owon meter logic (from: https://github.com/sercona/Owon-Multimeters/blob/main/owon_multi_cli.c)
    # convert bytes to 'reading' array
    reading =  [0, 0, 0]
    reading[0] = data[1] << 8 | data[0]
    reading[1] = data[3] << 8 | data[2]
    reading[2] = data[5] << 8 | data[4]

    # Extract data items from first field
    function = (reading[0] >> 6) & 0x0f
    scale    = (reading[0] >> 3) & 0x07
    decimal  = reading[0]        & 0x07

    # Extract and convert measurement value (sign)
    if (reading[2] < 0x7fff):     measurement = reading[2]
    else:                         measurement = -1 * (reading[2] & 0x7fff)

    print(f"meas: {measurement}  fon: {function}  scl: {scale}  dec: {decimal}", end= "  ")
    voltage = measurement / 10**decimal
    print(f"Volt: {voltage:0.3f}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        print()

    peripheral.disconnect()
    print("Disconnected")
    print()


# README.md

DataServer:
    A Python based webserver intended for running on a 'Raspberry Pi computer' (Raspi)
    serving data to GeigerLog as a:
        - 'GeigerLog WiFiServer Device' - when in the local (WiFi-)LAN
        - 'GeigerLog IoT Device'        - using MQTT from a place anywhere in the world

    DataServer can act as either one or both at the same time.

    The Raspi manages any devices connected to it; it starts them, collects their data,
    prepares the data, and sends them by the desired means.

    Supported Hardware Devices for the Raspi, which can all be run simultaeously, are:

        GMC counter, any model          by USB connection

        I2C Sensors                     by GPIO connection
            Supported I2C Sensors:
            - LM75B     temperature
            - BME280    temperature, barometric pressure, humidity
            - BH1750    visible light intensity in Lux
            - VEML6075  UV-A and UV-B intensity
            - LTR390    visible light and UV
            - GDK101    Geiger count rate

        Pulse counter                   by GPIO connection
            e.g. CAJOE counter

    DataServer can also be run on Non-Raspi computers (Windows, Linux, Mac), but then
    only the GMC counter, connected by USB, works on all of those. The I2C Sensors and
    the Pulse Counter will NOT work - if they are activated the program exits.

    To use the devices and sensors they need to be configured for usage in
    the CUSTOMIZE section in file 'rconfig.py'.

Requires Python 3.7 or later.

Start with:     path/to/dataserver
Stop  with:     CTRL-C

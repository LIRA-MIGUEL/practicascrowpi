#!/usr/bin/env python3
import HD44780MCP
import time
import MCP230XX
from DFRobot_DHT20 import DFRobot_DHT20
import smbus

# Inicialización del bus I2C y el sensor DHT20
I2C_BUS = 0x01  # Usar el bus I2C1 por defecto
I2C_ADDRESS = 0x38  # Dirección por defecto del dispositivo I2C
dht20 = DFRobot_DHT20(I2C_BUS, I2C_ADDRESS)

if not dht20.begin():
    print("Fallo en la inicialización del sensor DHT20")

# Inicializar el MCP y la pantalla LCD
i2cAddr = 0x21  # Dirección I2C del MCP23008
MCP = MCP230XX.MCP230XX('MCP23008', i2cAddr)

# Encender retroiluminación si se usa el LCD Adafruit I2C
blPin = 7  # Pin de retroiluminación cuando se usa el LCD Adafruit I2C
MCP.set_mode(blPin, 'output')
MCP.output(blPin, True)  # Encender retroiluminación

# Configuración de la pantalla LCD
LCD = HD44780MCP.HD44780(MCP, 1, -1, 2, [3, 4, 5, 6], rows=2, characters=16, mode=0, font=0)

# Definir los umbrales de temperatura
TEMP_THRESHOLD_HIGH = 30  # Temperatura máxima en °C para mostrar la advertencia "ALTA"
TEMP_THRESHOLD_LOW = 20   # Temperatura mínima en °C para mostrar el mensaje "Hace frío"

# Mostrar mensaje de bienvenida en el LCD
LCD.display_string("buenas tardes")
time.sleep(1)
LCD.display(False)  # Apagar pantalla
time.sleep(2)
LCD.display()  # Encender pantalla
LCD.set_cursor(2, 1)  # Mover el cursor a la segunda fila, primera columna
LCD.display_string("bienvenido")
time.sleep(2)

# Función para leer la temperatura y mostrar mensajes en el LCD
def check_temperature():
    T_celsius, humidity, crc_error = dht20.get_temperature_and_humidity()
    
    if crc_error:
        print("Error CRC: No se pudo leer correctamente.")
    else:
        if T_celsius > TEMP_THRESHOLD_HIGH:
            # Si la temperatura supera el umbral alto, mostrar advertencia "ALTA"
            LCD.clear_display()
            LCD.display_string(f"Temperatura ALTA!")
            time.sleep(2)
            LCD.clear_display()
            LCD.display_string(f"T: {T_celsius:.2f}°C")
            time.sleep(2)
        elif T_celsius < TEMP_THRESHOLD_LOW:
            # Si la temperatura es menor al umbral bajo, mostrar "Hace frío"
            LCD.clear_display()
            LCD.display_string("Hace frio")
            time.sleep(2)
            LCD.clear_display()
            LCD.display_string(f"T: {T_celsius:.2f}°C")
            time.sleep(2)
        else:
            # Si la temperatura está en el rango normal, mostrar solo la temperatura
            LCD.clear_display()
            LCD.display_string(f"T: {T_celsius:.2f}°C")
            time.sleep(2)

# Bucle principal
try:
    while True:
        check_temperature()  # Verificar y mostrar temperatura
        time.sleep(5)  # Esperar 5 segundos antes de la siguiente lectura
except KeyboardInterrupt:
    pass

# Apagar retroiluminación cuando el script termine
MCP.output(blPin, False)
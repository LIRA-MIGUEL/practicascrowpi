#!/usr/bin/env python3
import HD44780MCP
import time
import MCP230XX
import csv
from DFRobot_DHT20 import DFRobot_DHT20

# Inicialización del sensor DHT20
I2C_BUS = 0x01  # Usar el bus I2C1 por defecto
I2C_ADDRESS = 0x38  # Dirección I2C del sensor
dht20 = DFRobot_DHT20(I2C_BUS, I2C_ADDRESS)

if not dht20.begin():
    print("Fallo en la inicialización del sensor DHT20")

# Inicializar el MCP y la pantalla LCD
i2cAddr = 0x21  # Dirección I2C del MCP23008
MCP = MCP230XX.MCP230XX('MCP23008', i2cAddr)

# Configuración de retroiluminación de la pantalla LCD
blPin = 7  # Pin de retroiluminación
MCP.set_mode(blPin, 'output')
MCP.output(blPin, True)  # Encender retroiluminación

# Configurar la pantalla LCD (16x2)
LCD = HD44780MCP.HD44780(MCP, 1, -1, 2, [3, 4, 5, 6], rows=2, characters=16, mode=0, font=0)

# Umbrales de temperatura
TEMP_THRESHOLD_HIGH = 30  # Temperatura alta
TEMP_THRESHOLD_LOW = 20    # Temperatura baja

# Archivos CSV para almacenar datos
TEMPERATURAS_CSV = "Temperaturas.csv"
ALERTAS_CSV = "Alertas.csv"

# Función para inicializar archivos CSV con encabezados
def init_csv(file_name, headers):
    try:
        with open(file_name, mode="x", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
    except FileExistsError:
        pass  # Si el archivo ya existe, no lo sobrescribimos

# Crear archivos CSV si no existen
init_csv(TEMPERATURAS_CSV, ["Tiempo", "Temperatura (°C)", "Humedad (%)"])
init_csv(ALERTAS_CSV, ["Tiempo", "Alerta", "Temperatura (°C)"])

# Función para guardar datos en CSV
def save_to_csv(file_name, data):
    with open(file_name, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(data)

# Función para leer la temperatura y mostrar mensajes en el LCD
def check_temperature():
    T_celsius, humidity, crc_error = dht20.get_temperature_and_humidity()
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")  # Obtener la fecha y hora actual
    
    if crc_error:
        print("Error CRC: No se pudo leer correctamente.")
    else:
        # Guardar temperatura en CSV
        save_to_csv(TEMPERATURAS_CSV, [current_time, round(T_celsius, 2), round(humidity, 2)])

        if T_celsius > TEMP_THRESHOLD_HIGH:
            # Registrar alerta en CSV
            save_to_csv(ALERTAS_CSV, [current_time, "Temperatura ALTA", round(T_celsius, 2)])
            LCD.clear_display()
            LCD.display_string("ALERTA: T ALTA!")
            time.sleep(2)
            LCD.clear_display()
            LCD.display_string(f"T: {T_celsius:.2f}°C")
            time.sleep(2)

        elif T_celsius < TEMP_THRESHOLD_LOW:
            # Registrar alerta en CSV
            save_to_csv(ALERTAS_CSV, [current_time, "Hace frío", round(T_celsius, 2)])
            LCD.clear_display()
            LCD.display_string("Hace frio")
            time.sleep(2)
            LCD.clear_display()
            LCD.display_string(f"T: {T_celsius:.2f}°C")
            time.sleep(2)

        else:
            # Mostrar temperatura en la pantalla LCD sin alerta
            LCD.clear_display()
            LCD.display_string(f"T: {T_celsius:.2f}°C")
            time.sleep(2)

# Bucle principal
try:
    while True:
        check_temperature()  # Verificar temperatura y guardar datos
        time.sleep(5)  # Esperar 5 segundos antes de la siguiente lectura
except KeyboardInterrupt:
    pass  # Permite salir del programa con Ctrl+C

# Apagar retroiluminación al finalizar
MCP.output(blPin, False)
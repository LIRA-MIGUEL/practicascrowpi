import csv
from time import strftime, sleep
from DFRobot_DHT20 import DFRobot_DHT20
import smbus

# Configuración del archivo CSV
csv_filename = "Obtener_datos.c`sv"

# Abre el archivo CSV en modo de anexado para que no sobrescriba los datos cada vez
try:
    with open(csv_filename, mode="x", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Tiempo", "Temperatura C°", "Humedad (%)", "Luminosidad (lx)"])  # Cabecera
except FileExistsError:
    pass  # Si el archivo ya existe, no hace nada

# Inicialización de sensores 

# Sensor de DHT20
I2C_BUS = 0x01  # Usar el bus I2C1 por defecto
I2C_ADDRESS = 0x38  # Dirección por defecto del dispositivo I2C
dht20 = DFRobot_DHT20(I2C_BUS, I2C_ADDRESS)

if not dht20.begin():
    print("Fallo en la inicialización del sensor DHT20")

# Sensor de luminosidad
class LightSensor():
    def __init__(self):
        self.DEVICE = 0x5c  # Dirección I2C del sensor de luminosidad
        self.POWER_DOWN = 0x00  # Estado apagado
        self.POWER_ON = 0x01  # Encender el sensor
        self.RESET = 0x07  # Reiniciar
        self.ONE_TIME_HIGH_RES_MODE_1 = 0x20  # Modo de medición a 1lx

    def convertToNumber(self, data):
        # Convierte los datos de 2 bytes a un número decimal
        return ((data[1] + (256 * data[0])) / 1.2)

    def readLight(self):
        # Lee los datos de luminosidad
        data = bus.read_i2c_block_data(self.DEVICE, self.ONE_TIME_HIGH_RES_MODE_1)
        return self.convertToNumber(data)

# Configuración del bus I2C para el sensor de luminosidad
bus = smbus.SMBus(1)

sensor_luz = LightSensor()

# Función principal para leer los sensores y guardar los datos
def main():
    try:
        while True:
            # Obtener la hora actual
            current_time = strftime("%Y-%m-%d %H:%M:%S %Z")
            
            # Leer los datos del sensor de temperatura y humedad
            T_celsius, humidity, crc_error = dht20.get_temperature_and_humidity()
            
            if crc_error:
                print("Error CRC: No se pudo leer correctamente.")
            else:
                T_fahrenheit = T_celsius * 9 / 5 + 32  # Convertir a Fahrenheit si es necesario
                luminosidad = sensor_luz.readLight()  # Leer la luminosidad en lx
                
                # Imprimir los datos en consola
                print(f"{current_time}")
                print(f"Temperatura: {T_celsius:.2f}°C / {T_fahrenheit:.2f}°F")
                print(f"Humedad: {humidity:.2f}%")
                print(f"Luminosidad: {luminosidad:.2f} lx")
                print("CRC: OK\n")
                
                # Guardar los datos en el archivo CSV
                with open(csv_filename, mode="a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([current_time, T_celsius, humidity, luminosidad])
            
            # Esperar 5 segundos antes de la siguiente lectura
            sleep(10)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()

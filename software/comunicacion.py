
import serial
import time


class ComunicacionSerial:

    def __init__(self):
        self.conexion = None

    def conectar(self, puerto, velocidad=115200):
        try:
            self.conexion = serial.Serial(
                puerto,
                velocidad,
                timeout=1
            )

            time.sleep(2)
            return True

        except serial.SerialException as error:
            print("Error de conexion:", error)
            self.conexion = None
            return False

    def desconectar(self):
        if self.conexion and self.conexion.is_open:
            self.conexion.close()

        self.conexion = None

    def enviar(self, comando):
        if self.conexion and self.conexion.is_open:
            self.conexion.write(
                (comando + "\n").encode("utf-8")
            )

    def recibir(self):
        if self.conexion and self.conexion.is_open:
            if self.conexion.in_waiting:
                return self.conexion.readline().decode(
                    "utf-8",
                    errors="ignore"
                ).strip()

        return None

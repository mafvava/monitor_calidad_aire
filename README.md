
# Sistema de monitoreo de calidad del aire

## Descripcion
Sistema basado en ESP32 para monitorear variaciones en las condiciones del aire mediante sensores MQ-135 y DHT11.

El sistema permite visualizar las mediciones desde una interfaz gráfica desarrollada en Python.

## Componentes
- ESP32 DevKit V1
- Sensor MQ-135
- Sensor DHT11
- Buzzer activo
- LED verde
- LED rojo
- Ventilador de 5 V
- MOSFET o modulo controlador
- Resistencias y cables

## Funciones
- Lectura de gases.
- Medicion de temperatura.
- Medicion de humedad.
- Indicadores visuales y sonoros.
- Activacion automatica del ventilador.
- Control manual de actuadores.
- Registro de mediciones en CSV.

## Tecnologias
- C++
- Python
- PlatformIO
- Tkinter
- PySerial

## Comunicacion
La comunicacion entre el ESP32 y Python se realiza mediante USB serial a 115200 baudios.

## Ejecucion
1. Cargar el firmware al ESP32.
2. Instalar las dependencias de Python.
3. Conectar el ESP32 a la computadora.
4. Ejecutar main.py.
5. Seleccionar el puerto COM correspondiente.

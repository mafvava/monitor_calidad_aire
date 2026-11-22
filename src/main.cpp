
#include <Arduino.h>

#include "configuracion.h"

#include "Sensor.h"
#include "SensorMQ135.h"
#include "SensorDHT11.h"

#include "Actuador.h"
#include "Buzzer.h"
#include "LED.h"
#include "Ventilador.h"

#include "ComunicacionSerial.h"

// Sensores
SensorMQ135 sensorGases(MQ135_PIN);
SensorDHT11 sensorClima(DHT_PIN);

// Actuadores
Buzzer buzzer(BUZZER_PIN);
LED ledVerde(LED_VERDE_PIN);
LED ledRojo(LED_ROJO_PIN);
Ventilador ventilador(FAN_PIN);

// Comunicación
ComunicacionSerial comunicacion;

// Polimorfismo
Sensor* sensores[] = {
    &sensorGases,
    &sensorClima
};

Actuador* actuadores[] = {
    &buzzer,
    &ledVerde,
    &ledRojo,
    &ventilador
};

// Variables
int umbralGases = UMBRAL_GASES_INICIAL;
bool modoAutomatico = true;
String estadoGeneral = "NORMAL";

unsigned long tiempoAnterior = 0;

// Inicialización
void iniciarSensores() {
    for (Sensor* sensor : sensores) {
        sensor->iniciar();
    }
}

void iniciarActuadores() {
    for (Actuador* actuador : actuadores) {
        actuador->iniciar();
    }
}

// Lectura de sensores
void actualizarSensores() {
    for (Sensor* sensor : sensores) {
        sensor->actualizar();
    }
}

// Control automático
void controlarAutomatico() {
    if (sensorGases.getLectura() >= umbralGases) {
        estadoGeneral = "ALERTA";

        buzzer.encender();
        ledVerde.apagar();
        ledRojo.encender();
        ventilador.encender();
    } else {
        estadoGeneral = "NORMAL";

        buzzer.apagar();
        ledVerde.encender();
        ledRojo.apagar();
        ventilador.apagar();
    }
}

// Control de actuadores en modo manual
void procesarComando(String comando) {
    comando.trim();

    if (comando == "MODE,AUTO") {
        modoAutomatico = true;
        return;
    }

    if (comando == "MODE,MANUAL") {
        modoAutomatico = false;
        return;
    }

    if (comando.startsWith("THRESHOLD,")) {
        int nuevoUmbral = comando.substring(10).toInt();

        if (nuevoUmbral > 0 && nuevoUmbral <= 4095) {
            umbralGases = nuevoUmbral;
        }
        return;
    }

    if (modoAutomatico) {
        return;
    }

    if (comando == "BUZZER,1") {
        buzzer.encender();
    }
    else if (comando == "BUZZER,0") {
        buzzer.apagar();
    }
    else if (comando == "FAN,1") {
        ventilador.encender();
    }
    else if (comando == "FAN,0") {
        ventilador.apagar();
    }
    else if (comando == "LED_GREEN,1") {
        ledVerde.encender();
    }
    else if (comando == "LED_GREEN,0") {
        ledVerde.apagar();
    }
    else if (comando == "LED_RED,1") {
        ledRojo.encender();
    }
    else if (comando == "LED_RED,0") {
        ledRojo.apagar();
    }
}

// Recepción de comandos
void recibirComandos() {
    String comando;

    if (comunicacion.recibirComando(comando)) {
        procesarComando(comando);
    }
}

// Envío de datos
void enviarDatos() {
    comunicacion.enviarDatos(
        sensorGases.getLectura(),
        sensorClima.getTemperatura(),
        sensorClima.getHumedad(),
        modoAutomatico,
        umbralGases,
        buzzer.getEstado(),
        ledVerde.getEstado(),
        ledRojo.getEstado(),
        ventilador.getEstado(),
        estadoGeneral
    );
}

// Configuración
void setup() {
    comunicacion.iniciar(VELOCIDAD_SERIAL);

    iniciarSensores();
    iniciarActuadores();

    tiempoAnterior = millis();
}

// Ciclo principal
void loop() {
    recibirComandos();

    unsigned long tiempoActual = millis();

    if (tiempoActual - tiempoAnterior >= INTERVALO_LECTURA) {
        tiempoAnterior = tiempoActual;

        actualizarSensores();

        if (modoAutomatico) {
            controlarAutomatico();
        }

        enviarDatos();
    }
}

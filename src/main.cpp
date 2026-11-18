
#include <Arduino.h>

#include "configuracion.h"

// Libreria de sensores
#include "Sensor.h"
#include "SensorMQ135.h"
#include "SensorDHT11.h"

// Libreria de actuadores
#include "Actuador.h"
#include "Buzzer.h"
#include "LED.h"
#include "Ventilador.h"

// Libreria de comunicacion
#include "ComunicacionSerial.h"

// -------------------- OBJETOS DEL SISTEMA --------------------

// Sensores
SensorMQ135 sensorGases(MQ135_PIN);
SensorDHT11 sensorClima(DHT_PIN);

// Actuadores
Buzzer buzzer(BUZZER_PIN);
LED ledVerde(LED_VERDE_PIN);
LED ledRojo(LED_ROJO_PIN);
Ventilador ventilador(FAN_PIN);

// Comunicacion
ComunicacionSerial comunicacion;

// -------------------- POLIMORFISMO --------------------

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

// -------------------- VARIABLES DEL SISTEMA --------------------

int umbralGases = UMBRAL_GASES_INICIAL;

bool modoAutomatico = true;

String estadoGeneral = "NORMAL";

unsigned long tiempoAnterior = 0;

// -------------------- INICIALIZACION --------------------

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

// -------------------- LECTURA DE SENSORES --------------------

void actualizarSensores() {
    for (Sensor* sensor : sensores) {
        sensor->actualizar();
    }
}

// -------------------- CONTROL AUTOMATICO --------------------

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

// -------------------- ACTUALIZACION DE SALIDAS --------------------

void actualizarSalidas() {

    if (buzzer.getEstado()) {
        buzzer.encender();
    } else {
        buzzer.apagar();
    }

    if (ventilador.getEstado()) {
        ventilador.encender();
    } else {
        ventilador.apagar();
    }
}

// -------------------- PROCESAMIENTO DE COMANDOS --------------------

void procesarComando(String comando) {

    comando.trim();

    if (comando == "MODE,AUTO") {

        modoAutomatico = true;

    }
    else if (comando == "MODE,MANUAL") {

        modoAutomatico = false;

    }
    else if (comando.startsWith("THRESHOLD,")) {

        int nuevoUmbral = comando.substring(10).toInt();

        if (nuevoUmbral > 0 && nuevoUmbral <= 4095) {
            umbralGases = nuevoUmbral;
        }

    }
    else if (comando == "BUZZER,1" && !modoAutomatico) {

        buzzer.encender();

    }
    else if (comando == "BUZZER,0" && !modoAutomatico) {

        buzzer.apagar();

    }
    else if (comando == "FAN,1" && !modoAutomatico) {

        ventilador.encender();

    }
    else if (comando == "FAN,0" && !modoAutomatico) {

        ventilador.apagar();

    }
}

// -------------------- RECEPCION DE COMANDOS --------------------

void recibirComandos() {

    String comando;

    if (comunicacion.recibirComando(comando)) {
        procesarComando(comando);
    }
}

// -------------------- ENVIO DE DATOS --------------------

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

// -------------------- CONFIGURACION INICIAL --------------------

void setup() {

    comunicacion.iniciar(VELOCIDAD_SERIAL);

    iniciarSensores();
    iniciarActuadores();

    tiempoAnterior = millis();
}

// -------------------- CICLO PRINCIPAL --------------------

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

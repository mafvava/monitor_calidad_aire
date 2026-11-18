
#include <Arduino.h>
#include "SensorMQ135.h"

SensorMQ135::SensorMQ135(int pin) : Sensor(pin) {
    lectura = 0;
}

void SensorMQ135::iniciar() {
    pinMode(pin, INPUT);
    disponible = true;
}

void SensorMQ135::actualizar() {
    lectura = analogRead(pin);
}

int SensorMQ135::getLectura() const {
    return lectura;
}


#include <Arduino.h>
#include "Ventilador.h"

Ventilador::Ventilador(int pin) : Actuador(pin) {}

void Ventilador::iniciar() {
    pinMode(pin, OUTPUT);
    apagar();
}

void Ventilador::encender() {
    estado = true;
    digitalWrite(pin, HIGH);
}

void Ventilador::apagar() {
    estado = false;
    digitalWrite(pin, LOW);
}

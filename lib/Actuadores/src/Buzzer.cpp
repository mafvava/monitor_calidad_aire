
#include <Arduino.h>
#include "Buzzer.h"

Buzzer::Buzzer(int pin) : Actuador(pin) {}

void Buzzer::iniciar() {
    pinMode(pin, OUTPUT);
    apagar();
}

void Buzzer::encender() {
    estado = true;
    digitalWrite(pin, HIGH);
}

void Buzzer::apagar() {
    estado = false;
    digitalWrite(pin, LOW);
}

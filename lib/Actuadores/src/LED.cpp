
#include <Arduino.h>
#include "LED.h"

LED::LED(int pin) : Actuador(pin) {}

void LED::iniciar() {
    pinMode(pin, OUTPUT);
    apagar();
}

void LED::encender() {
    estado = true;
    digitalWrite(pin, HIGH);
}

void LED::apagar() {
    estado = false;
    digitalWrite(pin, LOW);
}

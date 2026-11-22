#include <Arduino.h>
#include "Buzzer.h"

Buzzer::Buzzer(int pin) : Actuador(pin) {}

void Buzzer::iniciar() {
    ledcSetup(canalPWM, 2500, 8);
    ledcAttachPin(pin, canalPWM);

    pwmConfigurado = true;

    apagar();
}

void Buzzer::encender() {
    if (!pwmConfigurado) {
        iniciar();
    }

    estado = true;

    // Generar sonido a 2500 Hz
    ledcWriteTone(canalPWM, 2500);
}

void Buzzer::apagar() {
    estado = false;

    if (pwmConfigurado) {
        ledcWriteTone(canalPWM, 0);
    }
}
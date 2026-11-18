
#include "Sensor.h"

Sensor::Sensor(int pin) {
    this->pin = pin;
    disponible = false;
}

int Sensor::getPin() const {
    return pin;
}

bool Sensor::getDisponible() const {
    return disponible;
}

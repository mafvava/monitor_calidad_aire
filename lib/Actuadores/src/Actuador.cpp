
#include "Actuador.h"

Actuador::Actuador(int pin) {
    this->pin = pin;
    estado = false;
}

int Actuador::getPin() const {
    return pin;
}

bool Actuador::getEstado() const {
    return estado;
}

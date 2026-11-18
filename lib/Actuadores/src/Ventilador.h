
#ifndef VENTILADOR_H
#define VENTILADOR_H

#include "Actuador.h"

class Ventilador : public Actuador {
public:
    explicit Ventilador(int pin);

    void iniciar() override;
    void encender() override;
    void apagar() override;
};

#endif

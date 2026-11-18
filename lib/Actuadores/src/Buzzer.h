
#ifndef BUZZER_H
#define BUZZER_H

#include "Actuador.h"

class Buzzer : public Actuador {
public:
    explicit Buzzer(int pin);

    void iniciar() override;
    void encender() override;
    void apagar() override;
};

#endif

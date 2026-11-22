#ifndef BUZZER_H
#define BUZZER_H

#include "Actuador.h"

class Buzzer : public Actuador {
private:
    const int canalPWM = 7;
    bool pwmConfigurado = false;

public:
    explicit Buzzer(int pin);

    void iniciar() override;
    void encender() override;
    void apagar() override;
};

#endif
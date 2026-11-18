
#ifndef LED_H
#define LED_H

#include "Actuador.h"

class LED : public Actuador {
public:
    explicit LED(int pin);

    void iniciar() override;
    void encender() override;
    void apagar() override;
};

#endif

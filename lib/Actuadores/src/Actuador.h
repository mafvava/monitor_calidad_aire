
#ifndef ACTUADOR_H
#define ACTUADOR_H

class Actuador {
protected:
    int pin;
    bool estado;

public:
    explicit Actuador(int pin);

    virtual void iniciar() = 0;
    virtual void encender() = 0;
    virtual void apagar() = 0;

    int getPin() const;
    bool getEstado() const;

    virtual ~Actuador() = default;
};

#endif

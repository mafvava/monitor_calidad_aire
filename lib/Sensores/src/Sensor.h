
#ifndef SENSOR_H
#define SENSOR_H

class Sensor {
protected:
    int pin;
    bool disponible;

public:
    explicit Sensor(int pin);

    virtual void iniciar() = 0;
    virtual void actualizar() = 0;

    int getPin() const;
    bool getDisponible() const;

    virtual ~Sensor() = default;
};

#endif

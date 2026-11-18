
#ifndef SENSOR_MQ135_H
#define SENSOR_MQ135_H

#include "Sensor.h"

class SensorMQ135 : public Sensor {
private:
    int lectura;

public:
    explicit SensorMQ135(int pin);

    void iniciar() override;
    void actualizar() override;

    int getLectura() const;
};

#endif

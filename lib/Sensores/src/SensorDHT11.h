
#ifndef SENSOR_DHT11_H
#define SENSOR_DHT11_H

#include "Sensor.h"
#include <DHT.h>

class SensorDHT11 : public Sensor {
private:
    DHT sensor;
    float temperatura;
    float humedad;

public:
    explicit SensorDHT11(int pin);

    void iniciar() override;
    void actualizar() override;

    float getTemperatura() const;
    float getHumedad() const;
};

#endif

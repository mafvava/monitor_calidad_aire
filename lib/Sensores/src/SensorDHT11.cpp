
#include <Arduino.h>
#include "SensorDHT11.h"

SensorDHT11::SensorDHT11(int pin)
    : Sensor(pin), sensor(pin, DHT11) {
    temperatura = 0.0;
    humedad = 0.0;
}

void SensorDHT11::iniciar() {
    sensor.begin();
    disponible = true;
}

void SensorDHT11::actualizar() {
    float nuevaTemperatura = sensor.readTemperature();
    float nuevaHumedad = sensor.readHumidity();

    if (!isnan(nuevaTemperatura) && !isnan(nuevaHumedad)) {
        temperatura = nuevaTemperatura;
        humedad = nuevaHumedad;
        disponible = true;
    } else {
        disponible = false;
    }
}

float SensorDHT11::getTemperatura() const {
    return temperatura;
}

float SensorDHT11::getHumedad() const {
    return humedad;
}

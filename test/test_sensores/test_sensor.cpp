
#include <Arduino.h>
#include <unity.h>

#include "Sensor.h"
#include "SensorMQ135.h"
#include "SensorDHT11.h"

void test_sensor_mq135_inicializacion() {
    SensorMQ135 sensor(34);

    sensor.iniciar();

    TEST_ASSERT_EQUAL(34, sensor.getPin());
    TEST_ASSERT_TRUE(sensor.getDisponible());
}

void test_sensor_dht11_inicializacion() {
    SensorDHT11 sensor(4);

    sensor.iniciar();

    TEST_ASSERT_EQUAL(4, sensor.getPin());
    TEST_ASSERT_TRUE(sensor.getDisponible());
}

void test_herencia_sensores() {
    SensorMQ135 sensor(34);

    Sensor* referencia = &sensor;

    TEST_ASSERT_EQUAL(34, referencia->getPin());
}

void setup() {
    delay(1000);

    UNITY_BEGIN();

    RUN_TEST(test_sensor_mq135_inicializacion);
    RUN_TEST(test_sensor_dht11_inicializacion);
    RUN_TEST(test_herencia_sensores);

    UNITY_END();
}

void loop() {
}

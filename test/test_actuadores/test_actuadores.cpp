
#include <Arduino.h>
#include <unity.h>

#include "Actuador.h"
#include "Buzzer.h"
#include "LED.h"
#include "Ventilador.h"

void test_buzzer() {
    Buzzer buzzer(25);

    buzzer.iniciar();

    TEST_ASSERT_FALSE(buzzer.getEstado());

    buzzer.encender();
    TEST_ASSERT_TRUE(buzzer.getEstado());

    buzzer.apagar();
    TEST_ASSERT_FALSE(buzzer.getEstado());
}

void test_led() {
    LED led(26);

    led.iniciar();

    TEST_ASSERT_FALSE(led.getEstado());

    led.encender();
    TEST_ASSERT_TRUE(led.getEstado());

    led.apagar();
    TEST_ASSERT_FALSE(led.getEstado());
}

void test_ventilador() {
    Ventilador ventilador(18);

    ventilador.iniciar();

    TEST_ASSERT_FALSE(ventilador.getEstado());

    ventilador.encender();
    TEST_ASSERT_TRUE(ventilador.getEstado());

    ventilador.apagar();
    TEST_ASSERT_FALSE(ventilador.getEstado());
}

void test_herencia_actuadores() {
    Buzzer buzzer(25);

    Actuador* referencia = &buzzer;

    TEST_ASSERT_EQUAL(25, referencia->getPin());
}

void setup() {
    delay(1000);

    UNITY_BEGIN();

    RUN_TEST(test_buzzer);
    RUN_TEST(test_led);
    RUN_TEST(test_ventilador);
    RUN_TEST(test_herencia_actuadores);

    UNITY_END();
}

void loop() {
}

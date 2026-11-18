
#include "ComunicacionSerial.h"

void ComunicacionSerial::iniciar(unsigned long velocidad) {
    Serial.begin(velocidad);
    comandoRecibido = "";
}

bool ComunicacionSerial::recibirComando(String &comando) {

    while (Serial.available() > 0) {

        char caracter = Serial.read();

        if (caracter == '\n') {
            comando = comandoRecibido;
            comando.trim();

            comandoRecibido = "";

            return true;
        }

        if (caracter != '\r') {
            comandoRecibido += caracter;
        }
    }

    return false;
}

void ComunicacionSerial::enviarDatos(
    int gases,
    float temperatura,
    float humedad,
    bool modoAutomatico,
    int umbral,
    bool buzzer,
    bool ledVerde,
    bool ledRojo,
    bool ventilador,
    const String &estadoGeneral
) {
    Serial.print("DATA,");

    Serial.print(gases);
    Serial.print(",");

    Serial.print(temperatura, 1);
    Serial.print(",");

    Serial.print(humedad, 1);
    Serial.print(",");

    Serial.print(modoAutomatico ? "AUTO" : "MANUAL");
    Serial.print(",");

    Serial.print(umbral);
    Serial.print(",");

    Serial.print(buzzer ? 1 : 0);
    Serial.print(",");

    Serial.print(ledVerde ? 1 : 0);
    Serial.print(",");

    Serial.print(ledRojo ? 1 : 0);
    Serial.print(",");

    Serial.print(ventilador ? 1 : 0);
    Serial.print(",");

    Serial.println(estadoGeneral);
}

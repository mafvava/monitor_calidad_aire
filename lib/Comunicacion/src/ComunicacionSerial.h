
#ifndef COMUNICACION_SERIAL_H
#define COMUNICACION_SERIAL_H

#include <Arduino.h>

class ComunicacionSerial {
private:
    String comandoRecibido;

public:
    void iniciar(unsigned long velocidad);

    bool recibirComando(String &comando);

    void enviarDatos(
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
    );
};

#endif

# Emmeti Mirai – Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![HA Version](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-blue.svg)](https://www.home-assistant.io)

Custom integration per interfacciare la pompa di calore **Emmeti Mirai** tramite **Modbus RTU over TCP** con Home Assistant.

---

## Caratteristiche

| Funzione | Dettaglio |
|----------|-----------|
| Protocollo | **Modbus RTU over TCP** |
| Configurazione | UI (Config Flow) – nessun YAML da modificare |
| Polling | Configurabile (default 30 s) |
| Registri | 65 registri reali da `modbus.yaml` inclusi nell'integrazione |
| Piattaforme HA | `sensor`, `binary_sensor`, `number`, `select`, `switch` |
| Opzioni | Aggiornabili a runtime senza riavvio |

---

## Installazione via HACS

1. Vai in **HACS → Integrazioni → ⋮ → Repository personalizzati**
2. Aggiungi l'URL: `https://github.com/germe/emmeti_mirai`
3. Categoria: **Integrazione**
4. Clicca **Aggiungi**, poi installa **Emmeti Mirai**
5. Riavvia Home Assistant

### Installazione manuale

1. Copia la cartella `custom_components/emmeti_mirai/` in `<config>/custom_components/`
2. Riavvia Home Assistant

---

## Configurazione

Vai in **Impostazioni → Dispositivi e servizi → Aggiungi integrazione → "Emmeti Mirai"**

| Campo | Descrizione | Default |
|-------|-------------|---------|
| **Host / IP** | Indirizzo IP del gateway Modbus | – |
| **Porta TCP** | Porta Modbus TCP | `502` |
| **Slave ID** | Indirizzo unità Modbus | `1` |
| **Intervallo polling** | Frequenza lettura in secondi | `30` |

---

## Entità create

### Sensori (51)

Temperature, umidità, potenze, COP, allarmi, ingressi/uscite digitali, storico allarmi, termoregolazione.

Esempi principali:

| Entità | Addr | Unità | Descrizione |
|--------|------|-------|-------------|
| `sensor.emmeti_mirai_temperatura_esterna` | 8985 | °C | Temperatura esterna |
| `sensor.emmeti_mirai_temperatura_acqua_uscita` | 8986 | °C | Acqua uscita PDC |
| `sensor.emmeti_mirai_temperatura_acqua_entrata` | 8987 | °C | Acqua entrata PDC |
| `sensor.emmeti_mirai_consumo_elettrico_pdc` | 9017 | W | Potenza assorbita |
| `sensor.emmeti_mirai_potenza_termica_riscaldamento` | 9019 | W | Potenza termica |
| `sensor.emmeti_mirai_cop` | 9023 | – | COP istantaneo |
| `sensor.emmeti_mirai_ore_lavoro_compressore` | 9033 | h | Ore compressore |

### Setpoint scrivibili – Number (14)

| Entità | Addr | Range | Descrizione |
|--------|------|-------|-------------|
| `number.emmeti_mirai_setpoint_temperatura_comfort` | 16439 | 15–30 °C | Setpoint comfort ambiente |
| `number.emmeti_mirai_heat_p1_temperatura` | 16443 | 20–60 °C | Heat P1 |
| `number.emmeti_mirai_cool_p1_temperatura` | 16450 | 7–25 °C | Cool P1 |
| `number.emmeti_mirai_acs_temperatura_mantenimento` | 16496 | 40–70 °C | ACS mantenimento |
| `number.emmeti_mirai_differenziale_setpoint_powerboost` | 16516 | 0–10 °C | PowerBoost |

---

## Aggiungere / modificare registri

Tutti i registri sono in `custom_components/emmeti_mirai/const.py`, lista `MODBUS_REGISTERS`.

```python
{
    "key": "mio_registro",
    "name": "Nome visualizzato in HA",
    "register": 9017,
    "register_type": "holding",   # holding | input | coil | discrete_input
    "data_type": "int16",         # int16 | uint16 | int32 | uint32 | float32 | bool
    "scale": 1,
    "offset": 0,
    "unit": "W",
    "device_class": "power",
    "state_class": "measurement",
    "entity_type": "sensor",      # sensor | binary_sensor | number | select | switch
    "writable": False,
}
```

Dopo ogni modifica riavvia HA.

---

## Note tecniche

- Il dispositivo Emmeti Mirai usa **Modbus RTU over TCP** (non Modbus TCP nativo)
- Tutti i registri sono di tipo **holding**, slave ID **1**
- Indirizzi nell'intervallo 8970–16516
- Testato su HA 2026.3.x con pymodbus 3.11.x e Python 3.14

---

## Licenza

MIT © 2024

# Industrial Automation – Chemical Tank Level Monitoring

## 1. Introduction

Industrial automation allows physical processes to be monitored and controlled through sensors, programmable logic controllers (PLCs), actuators, and Human-Machine Interfaces (HMIs).

The objective of this project is to design and implement an automated system for monitoring the liquid level of a chemical tank. The system uses three discrete level sensors to determine the current condition of the tank and identify both normal operating conditions and inconsistent sensor combinations.

The solution was developed in two stages:

1. Simulation and HMI implementation using **CODESYS**.
2. Validation of the same control logic using **OpenPLC and an ESP32-based physical prototype**.

The project uses Ladder Diagram (LD) according to the IEC 61131-3 programming approach.

---

# 2. Problem Description

The system monitors a tank using three digital level sensors:

- **B1:** Lower-level sensor.
- **B2:** Intermediate-level sensor.
- **B3:** Upper-level / overflow sensor.

The sensors are installed vertically in the tank.

As the liquid level increases, the sensors are activated sequentially:

B1 → B2 → B3

Therefore, only some combinations of the three sensors represent physically valid tank conditions.

The system provides five status outputs:

| Output | Description |
|---|---|
| H1 | Fill level correct |
| H2 | Fill level too low |
| H3 | Fill level too high |
| H4 | Tank empty |
| H5 | Sensor configuration error |

An additional internal variable called `SystemActive` is used to enable or disable the monitoring system.

---

# 3. System Requirements

The system must:

- Detect the state of three level sensors.
- Determine the current tank level.
- Detect impossible sensor combinations.
- Display the tank condition through an HMI.
- Allow the system to be enabled and disabled.
- Implement the control algorithm using Ladder Diagram.
- Validate the logic using CODESYS simulation.
- Reproduce the control logic in OpenPLC.
- Validate OpenPLC operation using an ESP32 and physical digital inputs/outputs.

---

# 4. Inputs and Outputs

## 4.1 Inputs

| Variable | Type | Description |
|---|---|---|
| B1 | BOOL | Lower tank sensor |
| B2 | BOOL | Middle tank sensor |
| B3 | BOOL | Upper tank sensor |
| Start | BOOL | Enables the monitoring system |
| Stop | BOOL | Disables the monitoring system |

## 4.2 Internal Variable

| Variable | Type | Description |
|---|---|---|
| SystemActive | BOOL | Indicates whether the monitoring system is enabled |

## 4.3 Outputs

| Variable | Type | Description |
|---|---|---|
| H1 | BOOL | Correct liquid level |
| H2 | BOOL | Liquid level too low |
| H3 | BOOL | Liquid level too high |
| H4 | BOOL | Tank empty |
| H5 | BOOL | Invalid sensor condition |

---

# 5. Combinational Logic Design

Three digital sensors generate:

2³ = 8

possible input combinations.

The complete truth table is shown below.

| B1 | B2 | B3 | Tank condition | Output |
|---:|---:|---:|---|---|
| 0 | 0 | 0 | Tank empty | H4 |
| 0 | 0 | 1 | Invalid condition | H5 |
| 0 | 1 | 0 | Invalid condition | H5 |
| 0 | 1 | 1 | Invalid condition | H5 |
| 1 | 0 | 0 | Fill level too low | H2 |
| 1 | 0 | 1 | Invalid condition | H5 |
| 1 | 1 | 0 | Fill level correct | H1 |
| 1 | 1 | 1 | Fill level too high | H3 |

The `000` condition is considered a valid condition because it represents an empty tank.

The other invalid combinations occur when an upper sensor is activated while a sensor located below it is inactive.

---

# 6. Boolean Logic

From the truth table, the following Boolean expressions were obtained.

## 6.1 Tank Empty – H4

H4 = ¬B1 · ¬B2 · ¬B3

This output is activated when none of the sensors detects liquid.

---

## 6.2 Fill Level Too Low – H2

H2 = B1 · ¬B2 · ¬B3

Only the lower sensor is activated.

---

## 6.3 Correct Fill Level – H1

H1 = B1 · B2 · ¬B3

The first two sensors detect liquid while the upper sensor remains inactive.

---

## 6.4 Fill Level Too High – H3

H3 = B1 · B2 · B3

All three sensors are activated.

---

## 6.5 Sensor Error – H5

The error condition can be expressed as:

H5 = (B2 · ¬B1) + (B3 · ¬B2)

This expression detects two physically inconsistent situations:

1. B2 is active while B1 is inactive.
2. B3 is active while B2 is inactive.

These conditions are sufficient to identify all invalid combinations in the truth table.

---

# 7. CODESYS Implementation

## 7.1 Development Environment

The first implementation was developed using **CODESYS V3.5** and Ladder Diagram as the PLC programming language.

Global Boolean variables were defined for the sensors, outputs, start/stop commands and system status.

The principal variables were:

```text
B1
B2
B3

H1
H2
H3
H4
H5

Start
Stop
SystemActive
```

---

# 8. Start/Stop Logic

A self-holding circuit was implemented to control `SystemActive`.

The Start signal activates the system, while the `SystemActive` contact maintains the circuit energized after Start is released.

The Stop command interrupts the circuit and disables the monitoring system.

Conceptually:

```text
        Stop
--------|/|------+------| | Start --------+
                 |                         |
                 +------| | SystemActive---+
                                           |
                                    (SystemActive)
```

This allows the level monitoring logic to operate only while the system is active.

---

# 9. Ladder Logic

Each tank condition was implemented in a separate Ladder network.

## 9.1 Empty Tank

```text
SystemActive    /B1    /B2    /B3
----| |---------|/|----|/|----|/|--------(H4)
```

---

## 9.2 Low Level

```text
SystemActive     B1    /B2    /B3
----| |---------| |----|/|----|/|--------(H2)
```

---

## 9.3 Correct Level

```text
SystemActive     B1     B2    /B3
----| |---------| |----| |----|/|--------(H1)
```

---

## 9.4 High Level

```text
SystemActive     B1     B2     B3
----| |---------| |----| |----| |--------(H3)
```

---

## 9.5 Error Detection

```text
                         B2       /B1
                       --| |------|/|---+
SystemActive              |             |
----| |-------------------+             +----(H5)
                          |             |
                       --| |------|/|---+
                         B3       /B2
```

This network detects inconsistent sensor combinations independently of the normal tank-level networks.

---

# 10. CODESYS HMI

A Human-Machine Interface was created in CODESYS to provide a graphical representation of the system.

The HMI allows the user to:

- Start the monitoring system.
- Stop the monitoring system.
- Modify the state of B1, B2 and B3 during simulation.
- Visualize whether the system is active.
- Visualize the current tank condition.
- Identify an invalid sensor configuration.

The HMI elements are directly associated with the PLC variables.

The interface provides visual feedback for:

- System Active.
- Tank Empty.
- Low Level.
- Correct Level.
- High Level.
- Sensor Error.

> **Insert Figure 1 here – CODESYS HMI**

```text
Figure 1. Tank monitoring HMI implemented in CODESYS.
```

---

# 11. CODESYS Simulation and Validation

Before implementing the physical prototype, the complete system was validated using the CODESYS simulation environment.

All eight possible sensor combinations were tested.

| Test | B1 | B2 | B3 | Expected result | Result |
|---|---:|---:|---:|---|---|
| T1 | 0 | 0 | 0 | H4 – Empty | PASS |
| T2 | 0 | 0 | 1 | H5 – Error | PASS |
| T3 | 0 | 1 | 0 | H5 – Error | PASS |
| T4 | 0 | 1 | 1 | H5 – Error | PASS |
| T5 | 1 | 0 | 0 | H2 – Low | PASS |
| T6 | 1 | 0 | 1 | H5 – Error | PASS |
| T7 | 1 | 1 | 0 | H1 – Correct | PASS |
| T8 | 1 | 1 | 1 | H3 – High | PASS |

The Start/Stop logic was also tested.

The following sequence was verified:

```text
Start activated
      ↓
SystemActive = TRUE

Start released
      ↓
SystemActive remains TRUE

Stop activated
      ↓
SystemActive = FALSE
```

The results confirmed that the CODESYS implementation behaved according to the designed truth table.

---

# 12. OpenPLC Implementation

After validating the system in CODESYS, the same control logic was implemented in **OpenPLC**.

The objective of this stage was to verify that the logic could operate on real physical hardware instead of only in simulation.

The Ladder program implemented in OpenPLC maintained the same logical behavior as the CODESYS implementation.

> **Insert Figure 2 here – OpenPLC Ladder**

```text
Figure 2. Ladder implementation in OpenPLC.
```

---

# 13. OpenPLC Variable Mapping

The physical signals were mapped to IEC addresses.

The three level sensors and system controls use digital inputs, while H1-H5 use digital outputs.

An example of the implemented mapping is shown below.

| Variable | IEC Address | Function |
|---|---|---|
| B1 | %IX0.0 | Lower sensor |
| B2 | %IX0.1 | Middle sensor |
| B3 | %IX0.2 | Upper sensor |
| Start | %IX0.3 | System start |
| Stop | %IX0.4 | System stop |
| H1 | %QX0.0 | Correct level |
| H2 | %QX0.1 | Low level |
| H3 | %QX0.2 | High level |
| H4 | %QX0.3 | Empty tank |
| H5 | %QX0.4 | Sensor error |

`SystemActive` is used internally by the control logic and can additionally be represented by a physical indicator.

> **Insert Figure 3 here – OpenPLC Variable Configuration**

```text
Figure 3. IEC variable addressing in OpenPLC.
```

---

# 14. ESP32 Pin Mapping

An ESP32 development board was used as the physical controller.

The OpenPLC hardware configuration maps IEC addresses to ESP32 GPIO pins.

The implemented level inputs were:

| IEC Address | ESP32 GPIO | Function |
|---|---:|---|
| %IX0.0 | GPIO 19 | B1 |
| %IX0.1 | GPIO 21 | B2 |
| %IX0.2 | GPIO 22 | B3 |
| %IX0.3 | GPIO 23 | Start |
| %IX0.4 | [GPIO USED FOR STOP] | Stop |

The principal physical outputs were:

| IEC Address | ESP32 GPIO | Function |
|---|---:|---|
| %QX0.0 | GPIO 2 | H1 |
| %QX0.1 | GPIO 4 | H2 |
| %QX0.2 | GPIO 15 | H3 |
| %QX0.3 | GPIO 5 | H4 |
| %QX0.4 | GPIO 18 | H5 |

> Replace `[GPIO USED FOR STOP]` with the GPIO finally used in the physical prototype.

> **Insert Figure 4 here – OpenPLC Pin Mapping**

```text
Figure 4. OpenPLC ESP32 pin mapping.
```

---

# 15. Physical Prototype

The physical prototype was assembled using:

- ESP32 development board.
- Breadboard.
- Four-position DIP switch.
- LEDs.
- Current-limiting resistors.
- Jumper wires.
- USB connection for programming and power.

The DIP switch was used to reproduce digital input conditions without requiring an actual liquid tank during laboratory validation.

Three switches represent:

```text
DIP 1 → B1
DIP 2 → B2
DIP 3 → B3
```

The remaining control is used according to the system activation configuration.

The LEDs provide a physical representation of the tank state.

> **Insert Figure 5 here – Physical Prototype**

```text
Figure 5. ESP32, DIP switches and LED indicators used for hardware validation.
```

---

# 16. Hardware Operation

The physical prototype follows the same sequence as the simulated system.

The ESP32 continuously executes the OpenPLC control logic.

The process can be summarized as:

```text
DIP switches / digital inputs
              ↓
         ESP32 GPIO
              ↓
           OpenPLC
              ↓
        Ladder Logic
              ↓
     Digital Output GPIO
              ↓
             LEDs
```

Changing one of the DIP switch positions modifies the corresponding sensor input.

OpenPLC processes the new combination and activates the appropriate output LED.

---

# 17. Physical Validation

The physical prototype was tested using the same input combinations previously tested in CODESYS.

## 17.1 Empty Tank

```text
B1 = 0
B2 = 0
B3 = 0
```

Expected result:

```text
H4 = ON
```

The system correctly identified the tank as empty.

---

## 17.2 Low Level

```text
B1 = 1
B2 = 0
B3 = 0
```

Expected result:

```text
H2 = ON
```

The system correctly identified a low liquid level.

---

## 17.3 Correct Level

```text
B1 = 1
B2 = 1
B3 = 0
```

Expected result:

```text
H1 = ON
```

The system correctly identified the normal operating level.

---

## 17.4 High Level

```text
B1 = 1
B2 = 1
B3 = 1
```

Expected result:

```text
H3 = ON
```

The system correctly detected the high-level condition.

---

## 17.5 Sensor Fault

For example:

```text
B1 = 0
B2 = 1
B3 = 0
```

This state is physically inconsistent because the middle sensor cannot detect liquid if the lower sensor does not detect it.

Expected result:

```text
H5 = ON
```

The physical implementation correctly activated the error indicator.

---

# 18. Complete Hardware Test Matrix

| B1 | B2 | B3 | Expected output | Physical result |
|---:|---:|---:|---|---|
| 0 | 0 | 0 | H4 | PASS |
| 0 | 0 | 1 | H5 | PASS |
| 0 | 1 | 0 | H5 | PASS |
| 0 | 1 | 1 | H5 | PASS |
| 1 | 0 | 0 | H2 | PASS |
| 1 | 0 | 1 | H5 | PASS |
| 1 | 1 | 0 | H1 | PASS |
| 1 | 1 | 1 | H3 | PASS |

The results obtained with the real hardware corresponded to the results obtained during the CODESYS simulation.

---

# 19. Hardware Circuit Schematic

The general hardware architecture is:

```text
                +------------------+
B1 ------------>|                  |-----> H1 LED
B2 ------------>|                  |-----> H2 LED
B3 ------------>|      ESP32       |-----> H3 LED
Start --------->|     OpenPLC      |-----> H4 LED
Stop ---------->|                  |-----> H5 LED
                |                  |-----> System Active
                +------------------+
```

Each LED is connected through a current-limiting resistor.

The DIP switches provide the digital signals required to emulate the level sensors.

> **Insert Figure 6 here – Electrical Schematic**

```text
Figure 6. Electrical connection diagram of the physical prototype.
```

---

# 20. Comparison Between Simulation and Physical Implementation

Two validation environments were used.

| Characteristic | CODESYS | OpenPLC + ESP32 |
|---|---|---|
| Ladder Logic | Yes | Yes |
| HMI | Yes | No |
| Virtual inputs | Yes | No |
| Physical inputs | No | Yes |
| Physical outputs | No | Yes |
| Error detection | Yes | Yes |
| 8 sensor states tested | Yes | Yes |

CODESYS made it possible to verify the control logic and HMI before connecting physical equipment.

OpenPLC was then used to execute equivalent control logic on the ESP32.

The two implementations generated the same logical results.

---

# 21. Results

The project successfully implemented a combinational control system for tank level monitoring.

The main results were:

- Correct identification of four valid tank conditions.
- Detection of inconsistent sensor states.
- Successful implementation using Ladder Diagram.
- Successful simulation using CODESYS.
- Successful interaction between the CODESYS Ladder program and HMI.
- Successful implementation of the same control logic in OpenPLC.
- Successful execution of OpenPLC on an ESP32.
- Successful reading of physical digital inputs.
- Successful control of physical LED outputs.
- Successful validation of all eight possible combinations of B1, B2 and B3.

The physical prototype produced the same results as the simulation.

---

# 22. Discussion

One important aspect of the system is that sensor combinations cannot be evaluated independently of their physical location.

For example:

```text
B1 = 0
B2 = 1
```

is inconsistent because B2 is physically located above B1.

Similarly:

```text
B2 = 0
B3 = 1
```

is inconsistent because the upper sensor is detecting liquid while the intermediate sensor is not.

The H5 logic therefore adds basic diagnostic capability to the monitoring system.

This is relevant in industrial automation because a PLC must not only process valid process states but should also detect information that may indicate an instrumentation or sensor failure.

---

# 23. Conclusions

The developed system demonstrated the complete workflow of a basic industrial automation application, from logical design to physical validation.

The truth table allowed all possible sensor combinations to be analyzed before implementing the PLC program.

The Boolean equations were successfully translated into Ladder Diagram networks.

CODESYS provided an effective environment for validating both the PLC program and the Human-Machine Interface before connecting physical hardware.

After validating the simulation, the logic was implemented in OpenPLC and executed on an ESP32.

The physical tests demonstrated that the OpenPLC implementation generated the same results as the CODESYS simulation for all eight sensor combinations.

The H5 error condition proved especially important because it allows the controller to distinguish between valid liquid-level states and physically inconsistent sensor combinations.

Overall, the implementation demonstrated how industrial automation can combine sensing, PLC logic, visualization and physical outputs to monitor a process reliably.

---

# 24. Future Improvements

Several improvements could be implemented in a future version:

- Replace the DIP switches with real liquid-level sensors.
- Add analog level measurement.
- Add automatic pump or valve control.
- Implement alarms for overflow conditions.
- Include an emergency stop circuit.
- Store historical level information.
- Add communication using Modbus TCP.
- Implement remote supervision using SCADA.
- Add sensor fault diagnostics and alarm history.

---

# 25. References

[1] Universidad de La Sabana, “PLC – Programming – Ladder Logic (LD): Chemical Liquid Tank Level Monitoring,” course material, 2026.

[2] CODESYS Group, “CODESYS Development System,” CODESYS Documentation.

[3] OpenPLC Project, “OpenPLC Documentation,” OpenPLC Project.

[4] IEC, “IEC 61131-3: Programmable Controllers – Part 3: Programming Languages,” International Electrotechnical Commission.

---

# Appendix A – Truth Table

| B1 | B2 | B3 | H1 | H2 | H3 | H4 | H5 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| 0 | 1 | 1 | 0 | 0 | 0 | 0 | 1 |
| 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| 1 | 1 | 1 | 0 | 0 | 1 | 0 | 0 |

---

# Appendix B – Boolean Equations

```text
H1 = B1 · B2 · ¬B3

H2 = B1 · ¬B2 · ¬B3

H3 = B1 · B2 · B3

H4 = ¬B1 · ¬B2 · ¬B3

H5 = (B2 · ¬B1) + (B3 · ¬B2)
```

All outputs are conditioned by `SystemActive`.

Therefore:

```text
Hn = SystemActive AND corresponding condition
```

where `n` represents H1 through H5.

---

# Appendix C – Evidence Checklist

The following evidence is included in the repository:

- [ ] CODESYS Ladder screenshot
- [ ] CODESYS HMI screenshot
- [ ] CODESYS simulation screenshot
- [ ] OpenPLC Ladder screenshot
- [ ] OpenPLC variable mapping screenshot
- [ ] OpenPLC ESP32 pin mapping screenshot
- [ ] Physical prototype photograph
- [ ] Electrical schematic
- [ ] Hardware testing evidence
- [ ] Video demonstration link

---

# Video Demonstration

The complete operation of the project can be observed in the following video:

**Video URL:** [ADD VIDEO LINK HERE]

The video demonstrates:

1. System objective.
2. Truth table.
3. CODESYS Ladder implementation.
4. CODESYS HMI operation.
5. Normal tank conditions.
6. Sensor error detection.


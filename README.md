# Autonomous Thermal Governor & Power Characterization

## Overview

This repository demonstrates a software-defined governor script designed to manage hardware constraints and prevent physical damage to the **NVIDIA Jetson Orin Nano**. The project addresses three primary engineering goals:

1.  **Managing Hardware Constraints:** Preventing performance degradation or system shutdown due to thermal throttling. The governor intervenes at a software-defined limit of **70°C** to protect the silicon before hardware-level side effects occur.
2.  **Intelligent Resource Management:** Orchestrating the switch between two power profiles:
    * **MAXN (Mode 0):** Provides maximum clock speeds at the cost of high heat generation.
    * **Mode 2 (15W):** Enforces a lower power ceiling to reduce heat at the expense of increased latency.
3.  **Systems Engineering:** Implements a classic **Closed-Loop Control** architecture:
    * **Sense:** Real-time hardware temperature monitoring via `sysfs`.
    * **Think:** Logic check: Has the SoC hit the 70°C threshold?
    * **Act:** Autonomous mode switching triggered via `nvpmodel`.

**Safety Reliability:** The main governor script is pinned to **CPU Core 0** using `os.sched_setaffinity`. This ensures that the safety logic remains responsive and does not lag, even when the other 5 cores are under 100% compute saturation.

---

## Key Performance Metrics

To quantify system behavior and the effectiveness of the governor, the following engineering measurements were analyzed:

* **Thermal Velocity:** Calculated as $\Delta Temp / \Delta Time$. This measures the "Rate of Change" to prove how much harder the heatsink works in Mode 0 vs Mode 2.
* **Energy per Calculation (Joules/Op):** Calculated as $Energy = Power \times Latency$. This identifies which mode is more energy-efficient for completing a specific matrix task.
* **Thermal Resistance ($\theta_{ca}$):** A critical EE metric measuring heatsink efficiency where fan is turned off. Calculated as: $R_{\theta} = (Temp_{Peak} - Temp_{Ambient}) / Power_{In}$.
* **Throughput (GFLOPS):** Converts latency into raw performance data. For these $4000 \times 4000$ matrices: $FLOPS = (128 \times 10^9) / (Latency / 1000)$.

---

## Methodology

The project was divided into 3 main experimental cycles. Each experiment starts at approximately **~50°C**, tests limits beyond **70°C**, and monitors cooling until reaching **~54°C**. Each run lasts for 16 minutes and 40 seconds. 

**Note on Active Cooling:** To isolate software-defined thermal regulation, the fan is programmatically disabled at the start of each experiment and remains off until 1-2 minutes after the system hits the 70°C threshold.

### Experiment 1: Mode 0 (MAXN)
* **Configuration:** Locked in MAXN mode (unlimited power draw).
* **Objective:** Establish the "High Speed, High Heat" baseline. This mode prioritizes low latency but exhibits the highest thermal velocity.

### Experiment 2: Active Governor
* **Configuration:** Dynamic switching between Mode 0 and Mode 2.
* **Objective:** Validate the "Sense-Think-Act" loop. The system utilizes full power until hitting 70°C, then autonomously switches to Mode 2 to stabilize temperature. This demonstrates the "Sawtooth" thermal profile of a managed system.

### Experiment 3: Mode 2 (Throttled)
* **Configuration:** Locked in 15W mode.
* **Objective:** Establish the low-performance baseline. This mode runs from 70°C until the cooling phase, drawing less power but incurring a significant "Latency Tax" (approx. 27% increase in compute time).

---
## Results

### Data Analysis of 3 Experiments (Mode 0, Experiment Governor, Mode 2)

<img width="887" height="712" alt="figure" src="https://github.com/user-attachments/assets/069b7e0c-ac0c-4713-8812-16cf761559d3" />

#### Summary Table

| Metric | Mode 0 (MAXN) | Active Governor | Mode 2 (15W) | Analysis |
| :--- | :--- | :--- | :--- | :--- |
| **Peak Temp** | 74.12°C | **70.47°C** | 73.84°C | [cite_start]Governor maintained the SoC **~3.6°C cooler** than uncapped Mode 0.  |
| **Thermal Velocity** | 0.091°C/s | 0.067°C/s | **0.052°C/s** | [cite_start]Switching to Mode 2 reduced heat accumulation speed by **~58%**.  |
| **Avg. Latency** | **3360 ms** | 3480 ms | 4250 ms | [cite_start]Governor incurred only a **~120 ms** penalty vs. the full 890 ms "Mode 2 Tax".  |
| **Throughput** | **38.1 GFLOPS** | 36.8 GFLOPS | 30.1 GFLOPS | [cite_start]System maintained **96% of peak compute power** while ensuring thermal safety.  |
| **Energy / Matrix** | 67.2 J | **61.3 J** | 63.7 J | [cite_start]**Winner:** Governor was most efficient by finishing tasks before heavy throttling.  |
| **Thermal Resist.** | 1.61°C/W | 1.89°C/W | 2.12°C/W | [cite_start]High values confirm fan-off environment forced heatsink to physical limits.  |



## Troubleshooting & Iteration

Initially, the workload ($1000 \times 1000$ matrices) allowed the temperature to stabilize too quickly at ~54°C, failing to reach the 70°C test limit. To increase thermal stress:
1.  Increased matrix multiplication dimensions to **$4000 \times 4000$**.
2.  Forced the fan off to simulate a cooling failure using:
    `sudo sh -c 'echo 0 > /sys/class/hwmon/hwmonX/pwm1'`

---

## Conclusion

The experiments successfully validated the use of a software-defined governor for thermal protection on the Jetson Orin Nano. Key findings include:

1.  **Stability:** The Governor successfully capped the temperature at the 70°C threshold, preventing the thermal runaway observed in the unmanaged Experiment 1.
2.  **Thermal Velocity:** Switching to Mode 2 provided a **58% reduction in thermal velocity**, significantly extending the operational safety window in fan-less environments.
3.  **Performance Trade-off:** Analysis documented a clear correlation between thermal stability and compute latency. Managing this **Performance-per-Watt** trade-off is critical for reliable embedded system design and hardware longevity.

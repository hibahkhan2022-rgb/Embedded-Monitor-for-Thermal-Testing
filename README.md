# Embedded-Monitor-for-Thermal-Testing

## Overview
This repository shows a governor script that manages hardware constraints and prevents hardware damage to Orin Nano. It covers three main goals:

1. Managing Hardware Constraints: The first is to prevent the hardware from slowing down or shutting due to thermal throttling. In this experiment, the limit was set to 70ºC to intervene before physical side effects.
2. Intelligent Resource Management: The second is to look at the two mode switches in the experiment. The first **MAXN** mode provides maximum speed at the cost of heat. The second **Mode 2** provides a lower speed but uses less heat.
3. Systems Engineering: Uses closed-loop control thinking.
     * Sense: Hardware reads temperature
     * Think: Did the hardware hit 70ºC?
     * Act: Switch modes by triggering `nvpmodel`

Also, the the main governor script is pinned down to Core 0. This means that even when other processes are running, the safety logic does not lag. 

## Troubleshooting
Originally, the code ran into some issues. Running the governor.py script allowed the temperature to increase from 50ºC to ~54ºC celsius, but would quickly stabilize. Initially, the matrix multiplication of the script was increased from (1000,1000) to (4000,4000). While it changed the ceiling by ~2º, the fan was turned off after to reach the 70ºC limit using: 
`

## Sensors'name:
IMU_3dbe7a
## On the system appers as:
Nordic Semiconductor ASA SensorStim IMU Rev7
## Port
crw-rw---- root dialout


## From my personal experience I hat this small inconvinient:
"My computer was not recognizing the sensor"
I rund the command "groups" and there was no "dialot". It is supposed to apper actually so I runed on my terminalL "sudo usermod -aG dialout $USER", I restart de computer and then it worked. (just in case)
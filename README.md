# pi-lightning-detect
Interfaces with the AS3935 Franklin Lightning Sensor IC.

## About
### Features working:
* Integrate with RaspberryPi-AS3935 https://github.com/pcfens/RaspberryPi-AS3935.git
* Basic features - intergrated to AS3935 & OLED screen. Detect Lightning strikes, logs to stdout
* In memory SQLite Database storing Lightning stats.
* OLED screen live data of Lightning - Distance, Energy, time since last strike.

### Features in progress
* Log out lightning detection data
* OLED screen historical stats & more info info

### Features in to-do
* Local Webseite
* Local webservices to diaply text - data, stats, etc.
* Local webservices to graphs and charts - data, stats, etc.
* Local webservices to allow configuration of pi-lightning-detect, thresholds for disturber, noise etc.
* Local webservices to allow tunning of AS3935 chip.
* Send Lightning Detection data to webservice to log, triangulate, and view on map
* Run as Daemon
* Install scripts


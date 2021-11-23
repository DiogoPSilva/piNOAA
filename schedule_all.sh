#!/bin/bash

# Update Satellite Information

wget -qr https://www.celestrak.com/NORAD/elements/weather.txt -O /home/pi/.predict/predict.txt
grep "NOAA 15" /home/pi/weather/predict/weather.txt -A 2 > /home/pi/.predict/predict.tle
grep "NOAA 18" /home/pi/weather/predict/weather.txt -A 2 >> /home/pi/.predict/predict.tle
grep "NOAA 19" /home/pi/weather/predict/weather.txt -A 2 >> /home/pi/.predict/predict.tle

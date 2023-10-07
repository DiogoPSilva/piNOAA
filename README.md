piNOAA
==============================

Automate Recording of Low Earth Orbit NOAA Weather Satellites
based on: https://github.com/DrPaulBrewer/rtlsdr-automated-wxsat-capture

These are some automation scripts I am developing in python for weather satellite hobbyist use.

License:  GPLv2 or any later version

assumptions: Linux-based computer, rtl-sdr usb dongle, stationary antenna, experienced python user

goal:  automatically record wav, decode and post on twitter the result

prerequistes:  working rtl-sdr, predict (text based, not gpredict) setup with correct ground station coordinates, sox

NO WARRANTY:  ALL USE IS AT THE RISK OF THE USER.  These are scripts I use for hobbyist purposes.  There may
be pre-requisites or system configuration differences which you will need to resolve in order to make use of these scripts in your project.  To do so requires patience and and, quite often, previous experience programming python 
and/or maintaining Linux-based rtl-sdr software.

##FILES

###LICENSE 
General Public License version 2.0, or any later version

###dotpredict-predict.tle
Modification of PREDICT's TLE file to provide orbit data for weather satellites NOAA-18,NOAA-19 
to get coverage of missing satellites into predict's default config
    
Copy as follows:  
```
mv dotpredict-predict.tle ~/.predict/predict.tle
```

    
###noaacapture.py
This is the main python script.  It will calculate the time
of the next pass for recording.  It expects to call rtl_fm to do the
recording and sox to convert the file to .wav and nooa-apt decoder to decode it into an image

###pypredict.py
This is a short python module for extracting the AOS/LOS times
of the next pass for a specified satellite and with a minimum  max elevation.  It calls predict -p and extracts
the times from the first and last lines.

###schedule_all.sh
This is a short shell script to update the tle, which are orbital
parameters needed by the predict program.
PREDICT was written by John Magliacane, KD2BD and released under the
GPL license.

import time
import pypredict
import subprocess
import os
from datetime import datetime, timezone
from PIL import Image

firstRun = 1

satellites = ['NOAA 18','NOAA 19','NOAA 15']
sat = ['noaa_18','noaa_19','noaa_15']
freqs = [137912500, 137100000, 137620000]
sample = '60000'
wavrate='11025'
gain = 0
ppm = 62
minEl = 30

                     
def runForDuration(cmdline, duration):
    try:
        child = subprocess.Popen(cmdline)
        time.sleep(duration)
        child.terminate()
    except OSError as e:
        print("OS Error during command: "+" ".join(cmdline))
        print("OS Error: "+e.strerror)

def recordFM(freq, fname, duration):
    # still experimenting with options - unsure as to best settings
    cmdline = ['timeout ',str(duration),\
               ' rtl_fm ',\
               '-f ',str(freq),\
               ' -M ','fm',\
               ' -s ',str(sample),\
               ' -p ',str(ppm),\
               ' -g ',str(gain),\
               ' -F',' 9',\
               ' -A',' fast',\
               ' -E',' deemp ',\
               fnameRAW+'.raw']
               
    new_cmdline = ''.join(cmdline)
    os.system(new_cmdline)

def transcode(fname):
    cmdline = ['sox ','-t ','raw ','-r ',str(sample),' -es ','-b16 ','-c1 ','-V1 ',fnameRAW+'.raw ',fnameWAV+'.wav rate ', str(wavrate)]
    new_cmdline = ''.join(cmdline)
    os.system(new_cmdline)

def decode(fname,currentDT,satel):
    
    cmdline = ['/home/pi/Desktop/piNOAA/noaa-apt -T /home/pi/.predict/predict.tle -m yes -s ',satel,' -t ',currentDT,' ',fnameWAV+'.wav -o ',fnamePNG+'.png']
    cmdline = ['/home/pi/Desktop/piNOAA/noaa-apt -m yes -s ',satel,' -t ',currentDT,' ',fnameWAV+'.wav -o ',fnamePNG+'.png']
    new_cmdline = ''.join(cmdline)
    os.system(new_cmdline)
    
    #/home/pi/Downloads/noaa-apt -T /home/pi/.predict/predict.tle -m yes -s noaa_18 -t 2021-11-17T11:00:11-00:00 NOAA_18_1637146812.wav -o NOAA_18_1637146812.png
    
def decode_nomap(fname,currentDT,satel):
    
    cmdline = ['/home/pi/Desktop/piNOAA/noaa-apt -T /home/pi/.predict/predict.tle -s ',satel,' -t ',currentDT,' ',fnameWAV+'.wav -o ',fnamePNGNOMAP+'.png']
    new_cmdline = ''.join(cmdline)
    os.system(new_cmdline)
    
    #/home/pi/Downloads/noaa-apt -T /home/pi/.predict/predict.tle -m yes -s noaa_18 -t 2021-11-17T11:00:11-00:00 NOAA_18_1637146812.wav -o NOAA_18_1637146812.png

def recordWAV(freq,fname,duration):
    recordFM(freq,fname,duration)
    transcode(fname)

def spectrum(fname,duration):
    cmdline = ['rtl_power','-f','137000000:138000000:1000','-i','1m','-g','40',fname+'.csv']
    runForDuration(cmdline,duration)

def findNextPass():
    predictions = [pypredict.aoslos(s,minEl) for s in satellites]
    aoses = [p[0] for p in predictions]
    nextIndex = aoses.index(min(aoses))
    return (satellites[nextIndex],\
            freqs[nextIndex],\
            predictions[nextIndex],\
            sat[nextIndex])

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    
def convertShort(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
      
    return "%d:%02d:%02d" % (hour, minutes, seconds)
    

while True:
    (satName, freq, (aosTime, losTime, maxEl, direction), satel) = findNextPass()
    #Direction = 1 --> South to North
    #Direction = 0 --> North to South
    now = time.time()
    towait = aosTime-now
    DT = datetime.now()
    
    while towait>0:
        now = time.time()
        towait = aosTime-now
        
        if towait<=0:
            break
        else:
            os.system("clear")
            
            if (direction == 1):
                print("Minimum elevation allowed:",minEl,"degrees\n"+convertShort(towait),"for "+satName,"with max elevation of",maxEl,"degrees\nSouth to North")
            else:
                print("Minimum elevation allowed:",minEl,"degrees\n"+convertShort(towait),"for "+satName,"with max elevation of",maxEl,"degrees\nNorth to South")
            time.sleep(1)
        
    passageTimestamp = time.strftime('%Y-%m-%dT%H:%M:%S%z', time.localtime(aosTime))
    passageTimestamp = passageTimestamp[:22] + ':' + passageTimestamp[22:]
    timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime(aosTime))
    
    fname = satel+'_'+timestamp+'_El'+str(maxEl)
    fnameRAW='/home/pi/Desktop/piNOAA/capture/RAW/'+satel+'_'+timestamp+'_El'+str(maxEl)
    fnamePNG='/home/pi/Desktop/piNOAA/capture/PNG/'+satel+'_'+timestamp+'_El'+str(maxEl)
    fnamePNGNOMAP='/home/pi/Desktop/piNOAA/capture/PNGNOMAP/'+satel+'_'+timestamp+'_El'+str(maxEl)
    fnameWAV='/home/pi/Desktop/piNOAA/capture/WAV/'+satel+'_'+timestamp+'_El'+str(maxEl)
    
    endTime = time.strftime('%H:%M:%S', time.localtime(losTime))
    print("beginning pass "+satName+" predicted end "+endTime)

    recordWAV(freq,fnameRAW,losTime-aosTime)
    decode(fnameWAV,passageTimestamp,satel) # make picture
    decode_nomap(fnameWAV,passageTimestamp,satel) # make picture without map
    
    print("finished pass "+satName+" at "+str(time.time()))
    
    if (direction == 1):
        rotImage  = Image.open(fnamePNG+'.png')
        rotImage2  = Image.open(fnamePNGNOMAP+'.png')
        # Rotate it by 180 degrees
        rotImage = rotImage.rotate(180)
        rotImage2 = rotImage2.rotate(180)
        rotImage.save(fnamePNG+'.png')
        rotImage2.save(fnamePNGNOMAP+'.png')
        
    cleanRAW ='rm '+fnameRAW+'.raw'
    os.system(cleanRAW)
    cleanWAV ='rm '+fnameWAV+'.wav'
    os.system(cleanWAV)
    time.sleep(10.0)


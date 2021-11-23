import time
import pypredict
import subprocess
import os
from datetime import datetime

satellites = ['NOAA 18','NOAA 19','NOAA 15']
sat = ['noaa_18','noaa_19','noaa_15']
freqs = [137912500, 137100000, 137620000]
sample = '1000000'
wavrate='11025'
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
               ' -M ',' fm -N '\
               ' -s ',sample,\
               ' -p',' 62'\
               ' -g',' 20',\
               ' -F',' 9',\
               ' -r',' 32k '\
               ' -A',' fast',\
               ' -E',' deemp ',\
               fnameRAW+'.raw']
               
    new_cmdline = ''.join(cmdline)
    os.system(new_cmdline)

def transcode(fname):
    cmdline = ['sox ','-t ','raw ','-r ',sample,' -es ','-b16 ','-c1 ','-V1 ',fnameRAW+'.raw ',fnameWAV+'.wav rate ', wavrate]
    new_cmdline = ''.join(cmdline)
    os.system(new_cmdline)

def decode(fname,currentDT,satel):
    
    cmdline = ['/home/pi/Desktop/piNOAA/noaa-apt -T /home/pi/.predict/predict.tle -s ',satel,' -t ',currentDT,' ',fnameWAV+'.wav -o ',fnamePNG+'.png']
    new_cmdline = ''.join(cmdline)
    os.system(new_cmdline)
    cmdline = ['/home/pi/Desktop/piNOAA/noaa-apt -T /home/pi/.predict/predict.tle -m yes -s ',satel,' -t ',currentDT,' ',fnameWAV+'.wav -o ',fnamePNG+'_map.png']
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
    (satName, freq, (aosTime, losTime,maxEl), satel) = findNextPass()
    now = time.time()
    towait = aosTime-now
    #print("Max Elevation: ",maxEl)
    DT = datetime.now()
    currentDT = DT.strftime('%d-%m-%Y %H:%M:%S')
    while towait>0:
        now = time.time()
        towait = aosTime-now
        
        if towait<=0:
            break
        else:
            os.system("clear")
            print("Minimum elevation allowed:",minEl,"degrees\n"+convertShort(towait),"for "+satName,"with max elevation of",maxEl,"degrees")
            time.sleep(1)
        
        
#         DT = datetime.now()
#         currentDT = DT.strftime('%d-%m-%Y %H:%M:%S')
#         print(currentDT+": Waiting "+convert(towait)+" for "+satName)
#         if towait >= 3600:
#             time.sleep(3600)
#             os.system("clear")
#         else:
#             time.sleep(towait)
        
    # dir= sat name and filename = start time
    DT = datetime.now()
    currentDT = DT.strftime('%Y-%m-%dT%H:%M:%S-00:00')
    timestamp = DT.strftime('%Y%m%d_%H%M%S')
    
    fnameRAW='/home/pi/Desktop/capture/RAW/'+satel+'_'+timestamp+'_El'+str(maxEl)
    fnamePNG='/home/pi/Desktop/capture/PNG/'+satel+'_'+timestamp+'_El'+str(maxEl)
    fnameWAV='/home/pi/Desktop/capture/WAV/'+satel+'_'+timestamp+'_El'+str(maxEl)
    print("beginning pass "+satName+" predicted end "+str(losTime))

    recordWAV(freq,fnameRAW,losTime-aosTime)
    decode(fnameWAV,currentDT,satel) # make picture
    # spectrum(fname,losTime-aosTime)
    print("finished pass "+satName+" at "+str(time.time()))
    time.sleep(60.0)


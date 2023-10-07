import time
import pypredict
import subprocess
import os
from datetime import datetime, timezone
import tweepy
from PIL import Image
from smb.SMBConnection import SMBConnection

firstRun = 1

satellites = ['NOAA 18','NOAA 19','NOAA 15']
sat = ['noaa_18','noaa_19','noaa_15']
freqs = [137912500, 137100000, 137620000]
sample = '60000'
wavrate='11025'
gain = 0
ppm = 62
minEl = 30

# Authenticate to Twitter
auth = tweepy.OAuthHandler("AuthHandler")
auth.set_access_token("Token")

api = tweepy.API(auth)

# Authenticate SMB
userID = 'ID'
password = 'password'
client_machine_name = 'pi'

server_name = 'server_name'
server_ip = '192.168.xxx.xxx'

domain_name = ''

conn = SMBConnection(userID, password, client_machine_name, server_name, domain=domain_name, use_ntlm_v2=True,
                     is_direct_tcp=True)
                     
def runForDuration(cmdline, duration):
    try:
        child = subprocess.Popen(cmdline)
        time.sleep(duration)
        child.terminate()
    except OSError as e:
        print("OS Error during command: "+" ".join(cmdline))
        print("OS Error: "+e.strerror)

def recordFM(freq, fname, duration):
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
    #print("Max Elevation: ",maxEl)
    DT = datetime.now()
    #currentDT = DT.strftime('%d-%m-%Y %H:%M:%S')
    
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
    fnameRAW='/home/pi/Desktop/capture/RAW/'+satel+'_'+timestamp+'_El'+str(maxEl)
    fnamePNG='/home/pi/Desktop/capture/PNG/'+satel+'_'+timestamp+'_El'+str(maxEl)
    fnamePNGNOMAP='/home/pi/Desktop/capture/PNGNOMAP/'+satel+'_'+timestamp+'_El'+str(maxEl)
    fnameWAV='/home/pi/Desktop/capture/WAV/'+satel+'_'+timestamp+'_El'+str(maxEl)
    
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
        
    # Upload image
    img = fnamePNG+'.png'
    media = api.media_upload(img)

    # Post tweet with image
    tweetTime = DT.strftime('%d/%m/%Y at %H:%M:%S')
    tweetTime = time.strftime('%d/%m/%Y at %H:%M:%S', time.localtime(aosTime))
    if (direction == 1):
        tweet = 'South to North\nImage received on '+tweetTime+' with a max elevation of '+str(maxEl)+' degrees from '+satName+'\nReceived at a sample rate of '+str(4*int(sample))+' S/s, a ppm correction of '+str(ppm)+' and a gain of '+str(gain)+'dB'
    else:
        tweet = 'North to South\nImage received on '+tweetTime+' with a max elevation of '+str(maxEl)+' degrees from '+satName+'\nReceived at a sample rate of '+str(4*int(sample))+' S/s, a ppm correction of '+str(ppm)+' and a gain of '+str(gain)+'dB'
    post_result = api.update_status(status=tweet, media_ids=[media.media_id])
    
    if firstRun == 1:
        conn.connect(server_ip, 445)
        firstRun = 0

    with open(fnamePNGNOMAP+'.png', 'rb') as file:
        conn.storeFile('share', 'nomap/'+fname+'.png', file)
    with open(fnamePNG+'.png', 'rb') as file:
        conn.storeFile('share', 'map/'+fname+'.png', file)
    with open(fnameWAV+'.wav', 'rb') as file:
        conn.storeFile('share', 'wav/'+fname+'.wav', file)

    #conn.close()
    
    cleanRAW ='rm '+fnameRAW+'.raw'
    os.system(cleanRAW)
    cleanWAV ='rm '+fnameWAV+'.wav'
    os.system(cleanWAV)
    cleanPNG ='rm '+fnamePNG+'.png'
    os.system(cleanPNG)
    cleanPNGNOMAP ='rm '+fnamePNGNOMAP+'.png'
    os.system(cleanPNGNOMAP)
    time.sleep(10.0)


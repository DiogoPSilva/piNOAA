sudo apt-get update
sudo apt-get upgrade -y

sudo apt install wget libncurses-dev libasound2-dev -y
wget https://www.qsl.net/kd2bd/predict-2.3.0.tar.gz
tar xvfz predict-2.3.0.tar.gz
cd predict-2.3.0
sudo ./configure /usr/bin
cd ..

chmod +rwx schedule_all.sh
sh schedule_all.sh

sudo apt-get install sox -y
sudo apt-get install rtl_sdr -y
sudo apt-get install gqrx-sdr -y



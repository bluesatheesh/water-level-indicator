# water-level-indicator
sudo apt install python3-pip
pip3 install RPi.GPIO
sudo apt-get install python3-rpi.gpio
pip3 install AWSIoTPythonSDK
---------------------------------------------------------------------------------------------------
create a start.sh file

#!/usr/bin/env bash
# stop script on error
set -e

# Check to see if AWS Device SDK for Python exists, download if not
if [ ! -d ./aws-iot-device-sdk-python ]; then
  printf "\nCloning the AWS SDK...\n"
  git clone https://github.com/aws/aws-iot-device-sdk-python.git
fi

# Check to see if AWS Device SDK for Python is already installed, install if not
if ! python -c "import AWSIoTPythonSDK" &> /dev/null; then
  printf "\nInstalling AWS SDK...\n"
  pushd aws-iot-device-sdk-python
  pip install AWSIoTPythonSDK
  result=$?
  popd
  if [ $result -ne 0 ]; then
    printf "\nERROR: Failed to install SDK.\n"
    exit $result
  fi
fi
---------------------------------------------------------------------------------------------------
create a file enpoint.json
{
	"endpointAddress" : "xxxxxxxxxxxxxxxxx-ats.iot.ap-south-1.amazonaws.com"
	}
---------------------------------------------------------------------------------------------------
sudo nano /etc/systemd/system/WaterLevelSensor.service
[Unit]
Description=WaterLevelSensorService
After=time-sync.target
[Service]
Restart=on-failure
RestartSec=30
ExecStart=sudo python3 WaterLevelSensor.py
WorkingDirectory=/home/pi/WaterLevelSensor
StandardOutput=inherit
StandardError=inherit
User=ubuntu
[Install]
WantedBy=multi-user.target
---------------------------------------------------------------------------------------------------
sudo systemctl daemon-reload
sudo systemctl enable WaterLevelSensor.service
sudo systemctl start WaterLevelSensor.service
---------------------------------------------------------------------------------------------------
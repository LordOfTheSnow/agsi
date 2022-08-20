# agsi

[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](http://perso.crans.org/besson/LICENSE.html)
[![Linux](https://img.shields.io/badge/os-Linux-green)](https://img.shields.io/badge/os-Linux-green)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://img.shields.io/badge/Python-3.10%2B-blue)
[![InfluxDB 2](https://img.shields.io/badge/InfluxDB-2-orange)](https://img.shields.io/badge/InfluxDB-2-orange)

## What is it?

A (more or less) simple script that reads data from the [AGSI/GIE (Aggregated Gas Storage Inventory)](https://agsi.gie.eu/) API and stores it in an InfluxDB for later use with Grafana or similar.

The AGSI/GIE website provides gas filling levels for various countries in Europe.

You can obtain a free API key from https://agsi.gie.eu/account. 


## Disclaimer

I am not a professional programmer (any more), thus this code will most probably not live up to current standards. 

Version 1.0 of this script has been hacked together more or less quick and dirty. I plan to add comments and clean up the code in the future, but up to now it is not well documented.

**I will take no responsibility whatsoever for any damage that may result by using this code.**

## Requirements

* Python 3.10 or higher (currently works under 3.9+)
* additional Python modules: see requirements.txt
* A free API key from https://agsi.gie.eu/account
* An InfluxDB 2.x to store the values (1.8 is not supported).
* (Grafana for visualization)

### Installation

1. Clone the git repository from https://github.com/LordOfTheSnow/agsi.git
2. Change to the created directory
3. Create a Python virtual environment with `python3 -m venv venv`
4. Activate that virtual environment with `source venv/bin/activate`
5. Install the required Python modules via pip: `pip install -r requirements.txt`
6. Rename the provided `.env.example` and put in the API key you obtained in from the website mentioned above plus the configuration to access an InfluxDB to store the values (See _Configuration values_ below).


#### Configuration values (.env)

There are various methods in InfluxDB 2 to read configuration values. I decided to stick with the .env file file because it is also possible to set the config values for InfluxDB 2 via environment variables and they will still be read with by the dotenv-python package - so it's up to you if you set those values in the .env file or as enviroment variables.

  * API_KEY = "My AGSI/GIE API Token"
  * INFLUXDB_V2_URL = "http://localhost:8086"
  * INFLUXDB_V2_ORG = "My Org"
  * INFLUXDB_V2_TOKEN = "My Token"
  * INFLUXDB_V2_BUCKET = "agsi"

The InfluxDB server and the bucket ("agsi" in this example) have to exist already, use the Influx GUI to set up your organzination, bucket and token.


### Usage 

#### Run from shell

7. From within the virtual environment, call the script for example with 

```
python app.py --country DE --From 2022-08-01 --To 2022-08-15 --size 300
python app.py --country DE --From 2022-08-01 --size 300
python app.py --Date 2022-08-17 
python app.py --From -5 --To -1
```

Run 
```
python app.py -h
```
for a help page

```
usage: app.py [-h] [-c COUNTRY] [-F FROM] [-T TO] [-D DATE] [-s SIZE] [-dnw]

options:
  -h, --help            show this help message and exit
  -c COUNTRY, --country COUNTRY
                        country for the values to be received, e.g. DE for Germany or AT for Austria
  -F FROM, --From FROM  start date for the values to be received. Format: YYYY-MM-DD or a negative offset (e.g. -1 = -1 day)
  -T TO, --To TO        end date for the values to be received. Format: YYYY-MM-DD or a negative offset (e.g. -1 = -1 day)
  -D DATE, --Date DATE  exact date for the values to be received. Format: YYYY-MM-DD or a negative offset (e.g. -1 = -1 day)
  -s SIZE, --size SIZE  maximum number of results/rows to be received
  -dnw, --do_not_write  do not write values to database
```


Options starting with a _-_ or _--_ are optional and can be omitted.

You can set a range with `--From YYYY-MM-DD` and `--To YYYY-MM-DD` or you can use `--Date YYYY-MM-DD` to get the data of a single day.

`--From` and `--To` can also be used with negative offsets, e.g. `--From -3` for -3 days starting today.

`--size` specifies the number of results (rows) to be returned at maximum. 

`--country` specifies the country to be queried, see the webpage at https://agsi.gie.eu/ for a list of available countries

`--do_not_write` will prevent writing the result to the configured database


#### Run via periodically via cron

If you want to run this script periodically via cron, you can call the wrapper script **cronscript.sh** (rename the provided `cronscript.sh.example` to `cronscript.sh` so that local changes will not be overwritten with next git pull).

8. Set execute permissions for the script: `chmod ug+x cronscript.sh`
9. Call `crontab -e` to edit the cron table (crontab), e.g.:

```
# m h  dom mon dow   command
30 14 * * * /home/pi/src/agsi/cronscript.sh
```
This will run the command at 14:30h local time on every day. Edit the path to the script to wherever you put it. 
The script assumes you have a Python virtual environment created with `python3 -m venv venv` in the same directory where you checked out the repository. The script will activate the virtual environment, call the Python interpreter with the script and will deactivate the virtual environment then.

### Files and data created

1. measurement _agsi_ in the Influx DB/bucket configured under _INFLUXDB_V2_BUCKET_ 

```
{
    "measurement": "agsi",
    "fields": {
        "gasInStorage",
        "consumption",
        "consumptionFull",
        "injection",
        "withdrawal",
        "workingGasVolume",
        "injectionCapacity",
        "withdrawalCapacity",
        "status",
        "trend",
        "full"
    },
    "time": gasDayStart
}
```
For an explanation of the fields, take a look at the documentation at https://www.gie.eu/transparency-platform/GIE_API_documentation_v006.pdf

In the current implementation, the timestamp will always be at 0:00 local time at the given date.

## Known bugs & limitations

* For some obscure reason, the command line argument parser doesn't allow using the parameter `--from`. Thus I have implemented it as an upper case parameter `--From`.

## Additional documentation used 

* https://www.gie.eu/transparency-platform/GIE_API_documentation_v006.pdf
* https://ct.de/y47m

## History

* 19-Aug-2022
  * first public version

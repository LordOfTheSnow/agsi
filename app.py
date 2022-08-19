import requests
import pandas as pd
import os
import sys
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from argparse import ArgumentParser
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from myinfluxclient import *

def main():
    logging.basicConfig()
    # logging.getLogger().setLevel(logging.DEBUG)  # optionally set level for everything.  Useful to see dependency debug info as well.
    app_log = logging.getLogger("asgi")
    app_log.setLevel(logging.DEBUG)

    url = "https://agsi.gie.eu/api"
    # load environment variables
    load_dotenv()

    # parse command line arguments    
    parser = ArgumentParser()
    parser.add_argument("-c", "--country", default="DE",
                        help="country for the values to be received, e.g. DE for Germany or AT for Austria")
    # when using lower case --from, the call to args.from fails with a syntax error, thus using the uppercase form "--From" as a workaround
    # ToDo: fix this!
    parser.add_argument("-F", "--From", 
                        help="start date for the values to be received. Format: YYYY-MM-DD or a negative offset (e.g. -1 = -1 day)")
    parser.add_argument("-T", "--To", 
                        help="end date for the values to be received. Format: YYYY-MM-DD or a negative offset (e.g. -1 = -1 day)")
    parser.add_argument("-D", "--Date", 
                        help="exact date for the values to be received. Format: YYYY-MM-DD or a negative offset (e.g. -1 = -1 day)")
    parser.add_argument("-s", "--size", default=300, 
                        help="maximum number of results/rows to be received")
    parser.add_argument("-dnw", "--do_not_write", action='store_true',
                        help="do not write values to database")

    args = parser.parse_args()

    params = {
        "country": args.country,
        "size": args.size
    }

    # get from and to date
    # first get the current date
    now = datetime.now()

    if args.From:
        if str(args.From).startswith("-"):
            from_date_ts = now + timedelta(days=int(args.From))
            from_date = from_date_ts.strftime("%Y-%m-%d")
        else:
            from_date = args.From
        app_log.debug(f"from: {from_date}")
        params["from"] = from_date

    if args.To:
        if str(args.To).startswith("-"):
            to_date_ts = now + timedelta(days=int(args.To))
            to_date = to_date_ts.strftime("%Y-%m-%d")
        else:
            to_date = args.To
        app_log.debug(f"to: {to_date}")
        params["to"] = to_date

    if args.Date:
        if str(args.Date).startswith("-"):
            date_date_ts = now + timedelta(days=int(args.Date))
            date_date = date_date_ts.strftime("%Y-%m-%d")
        else:
            date_date = args.Date
        app_log.debug(f"date: {date_date}")
        params["date"] = date_date

    headers = {
        "x-key": os.environ.get("API_KEY")
    }

    # database credentials
    influxUrl = os.environ.get('INFLUXDB_V2_URL')
    influxOrg = os.environ.get('INFLUXDB_V2_ORG', default='-')
    influxToken= os.environ.get('INFLUXDB_V2_TOKEN')
    influxBucket= os.environ.get('INFLUXDB_V2_BUCKET')

    # download data
    response = requests.get(url=url, params=params, headers=headers)
    data = response.json()

    if not data["data"]:
        exit(f"Error reading data from api at {url}. Check API key.")

    df = pd.json_normalize(data["data"])

    # all numeric fields are returned as strings :-( Convert them to their appropriate data type
    df["gasDayStart"] = pd.to_datetime(df["gasDayStart"], errors="coerce")
    df["gasInStorage"] = df["gasInStorage"].astype(float)
    df["consumption"] = df["consumption"].astype(float)
    df["consumptionFull"] = df["consumptionFull"].astype(float)
    df["injection"] = df["injection"].astype(float)
    df["withdrawal"] = df["withdrawal"].astype(float)
    df["workingGasVolume"] = df["workingGasVolume"].astype(float)
    df["injectionCapacity"] = df["injectionCapacity"].astype(float)
    df["withdrawalCapacity"] = df["withdrawalCapacity"].astype(float)
    df["trend"] = df["trend"].astype(float)
    df["full"] = df["full"].astype(float)
    print(df.head(100))

    if (not (influxUrl and influxToken and influxBucket)):
        app_log.exception("InfluxDB configuration parameters are missing. Program terminated.")
        sys.exit("InfluxDB configuration parameters are missing. Program terminated. See log file for details.")

    with InfluxDBClient(url=influxUrl, token=influxToken, org=influxOrg) as influxDbClient:
        handleData(log=app_log, df=df, args=args, influxDbClient=influxDbClient, influxBucket=influxBucket)


# helper function because it is repeated for either InfluxDB 1.8 and 2
def handleData(log, df, args, influxDbClient, influxBucket):
    if len(df):
        if not args.do_not_write:
            for index, row in df.iterrows():
                writeInfluxDBPoint(influxDbClient, influxBucket, row)  
        else:
            log.info("--do_not_write specified, no data written to database")  
    else:
        log.info(f"no data found")



if __name__ == '__main__':
    main()

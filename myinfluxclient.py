import pandas as pd
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.write_precision import *
from datetime import datetime
from time import time

def writeInfluxDBPoint(influxDbClient, bucket, row):

    # gasDayStart = row["gasDayStart"]

    # element = datetime.strptime(row["gasDayStart"],"%Y-%m-%d")
    # tuple = element.timetuple()
    # timestamp = mktime(tuple)
    # print(timestamp)


    # timestamp = datetime.strptime(gasDayStart, '%Y-%m-%d')

    with influxDbClient.write_api() as write_api:

        dict_structure = {
            "measurement": "gas",
            # "tags": {
            #     "symbol": dataPoint.symbol,
            # },
            "fields": {
                "gasInStorage": row["gasInStorage"],
                "consumption": row["consumption"],
                "consumptionFull": row["consumptionFull"],
                "injection": row["injection"],
                "withdrawal": row["withdrawal"],
                "workingGasVolume": row["workingGasVolume"],
                "injectionCapacity": row["injectionCapacity"],
                "withdrawalCapacity": row["withdrawalCapacity"],
                "status": row["status"],
                "trend": row["trend"],
                "full": row["full"],
            },
            "time": row["gasDayStart"]
        }
        print(f"dataPoint: {dict_structure}")
        point = Point.from_dict(dict_structure, WritePrecision.MS)
        write_api.write(bucket=bucket, record=point)
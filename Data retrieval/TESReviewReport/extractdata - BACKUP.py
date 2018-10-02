__author__ = 'Tom Haddon'

import datetime
import re
import pymongo
import pprint
from datetime import datetime, timedelta
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from contextlib import closing


class GraphRawData:
    def __init__(self, vehicles_in_total, vehicles_larger_than_220cm, vehicles_smaller_than_220cm, vehicles_petrol_count, vehicles_diesel_count,
                 vehicles_electric_count, vehicles_hybrid_count, vehicles_unknown_fuel_count,
                 vehicles_unknown_size_count, vehicles_time_count, start_date=None, end_date=None):

        self.vehicles_in_total = vehicles_in_total
        self.vehicles_larger_than_220cm = vehicles_larger_than_220cm
        self.vehicles_smaller_than_220cm = vehicles_smaller_than_220cm
        self.vehicles_petrol_count = vehicles_petrol_count
        self.vehicles_diesel_count = vehicles_diesel_count
        self.vehicles_electric_count = vehicles_electric_count
        self.vehicles_hybrid_count = vehicles_hybrid_count
        self.vehicles_unknown_fuel_count = vehicles_unknown_fuel_count
        self.vehicles_unknown_size_count = vehicles_unknown_size_count
        self.vehicles_time_count = vehicles_time_count
        if start_date is not None:
            self.start_date = start_date
            self.end_date = end_date

    def __str__(self):
        p = ('Vehicles in Total: {0}'.format(self.vehicles_in_total),
             'Vehicles that are larger than 220cm: {0}'.format(self.vehicles_larger_than_220cm),
             'Vehicles that are smaller than 220cm: {0}'.format(self.vehicles_smaller_than_220cm),
             'Vehicles that are Unknown in size: {0}'.format(self.vehicles_unknown_size_count),
             'Vehicles using Petrol: {0}'.format(self.vehicles_petrol_count),
             'Vehicles using Diesel: {0}'.format(self.vehicles_diesel_count),
             'Vehicles using Electricity: {0}'.format(self.vehicles_electric_count),
             'Vehicles using Hybrid engines: {0}'.format(self.vehicles_hybrid_count),
             'Vehicles using Unknown fuel: {0}'.format(self.vehicles_unknown_fuel_count),
             'Amount in hours: {0}'.format(self.vehicles_time_count))

        print(p[0])
        print(p[1])
        print(p[2])
        print(p[3])
        print(p[4])
        print(p[5])
        print(p[6])
        print(p[7])
        print(p[8])
        print(p[9])


class DataExtractor:
    # Make Connection to database and then make reference to the collection in question
    def __init__(self, start_date=None, end_date=None, cameraids=None):
        self.client = MongoClient()
        self.db = self.client['local']
        self.collection = self.db['Vehicles']
        if start_date is None:
            self.data = GraphRawData(self.__vehicle_count__(), self.__vehicle_220cm_and_more_count__(),
                                 self.__vehicle_220cm_less_count__(),
                                 self.__vehicle_petrol_count__(), self.__vehicle_diesel_count__(),
                                 self.__vehicle_electric_count__(), self.__vehicle_hybrid_count__(),
                                 self.__vehicle_unknown_fuel_count__(),
                                 (self.__vehicle_count__() - (self.__vehicle_220cm_and_more_count__() +
                                                              self.__vehicle_220cm_less_count__())))
        else:
            self.data = GraphRawData(self.__vehicle_count__(start_date, end_date),
                                     self.__vehicle_220cm_and_more_count__(start_date, end_date),
                                     self.__vehicle_220cm_less_count__(start_date, end_date),
                                     self.__vehicle_petrol_count__(start_date, end_date),
                                     self.__vehicle_diesel_count__(start_date, end_date),
                                     self.__vehicle_electric_count__(start_date, end_date),
                                     self.__vehicle_hybrid_count__(start_date, end_date),
                                     self.__vehicle_unknown_fuel_count__(start_date, end_date),
                                     (self.__vehicle_count__(start_date, end_date)
                                      - (self.__vehicle_220cm_and_more_count__(start_date, end_date)
                                      + self.__vehicle_220cm_less_count__(start_date, end_date))),
                                     self.__vehicle_time_count__(start_date, end_date), start_date, end_date)

    def __extract_graph_data__(self):
        return self.data

    def __vehicle_count__(self, start_date=None, end_date=None, cameraids=None):
        self.temp = 0
        if cameraids is not None:
            for camera in cameraids:
                if start_date is None:
                    for result_object in self.collection.find({"system_id": ObjectId(camera)}):
                        self.temp = self.temp + 1
                    return self.temp

                else:
                    for result_object in self.collection.find(
                            {"detection_datetime": {"$gte": start_date, "$lt": end_date}},
                            {"system_id": ObjectId(camera)}):
                        self.temp = self.temp + 1
                    return self.temp
        else:
            if start_date is None:
                for result_object in self.collection.find({}):
                    self.temp = self.temp + 1
                return self.temp

            else:
                for result_object in self.collection.find(
                        {"detection_datetime": {"$gte": start_date, "$lt": end_date}}):
                    self.temp = self.temp + 1
                return self.temp





    def __vehicle_time_count__(self, start_date=None, end_date=None, cameraids=None):
        self.temp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        if start_date is None:
            return 0
        else:
            for result_object in self.collection.find({"detection_datetime": {"$gte": start_date, "$lt": end_date}}):
                d = result_object['detection_datetime']
                self.temp[d.hour] = self.temp[d.hour] + 1
        return self.temp

    def __vehicle_220cm_and_more_count__(self, start_date=None, end_date=None, cameraids=None):
        self.temp = 0
        if start_date is None:
                for result_object in self.collection.find({"attributes.width": {'$exists': True}}):
                    if result_object['attributes']['width'] >= 2200:
                        self.temp = self.temp + 1
                return self.temp

        else:
            for result_object in self.collection.find({"attributes.width": {'$exists': True},
                                                       "detection_datetime": {"$gte": start_date, "$lt": end_date}}):
                if result_object['attributes']['width'] >= 2200:
                    self.temp = self.temp + 1
            return self.temp

    def __vehicle_220cm_less_count__(self, start_date=None, end_date=None, cameraids=None):
        self.temp = 0
        if start_date is None:
            for result_object in self.collection.find({"attributes.width": {'$exists': True}}):
                if result_object['attributes']['width'] < 2200:
                    self.temp = self.temp + 1
            return self.temp

        else:
            for result_object in self.collection.find({"attributes.width": {'$exists': True},
                                                       "detection_datetime": {"$gte": start_date, "$lt": end_date}}):
                if result_object['attributes']['width'] < 2200:
                    self.temp = self.temp + 1
            return self.temp

    def __vehicle_petrol_count__(self, start_date=None, end_date=None, cameraids=None):
        self.temp = 0
        if start_date is None:
            for result_object in self.collection.find({"attributes.fuel_type": {'$exists': True}}):
                if result_object['attributes']['fuel_type'] == "PETROL":
                    self.temp = self.temp + 1
            return self.temp

        else:
            for result_object in self.collection.find({"attributes.fuel_type": {'$exists': True},
                                                       "detection_datetime": {"$gte": start_date, "$lt": end_date}}):
                if result_object['attributes']['fuel_type'] == "PETROL":
                    self.temp = self.temp + 1
            return self.temp

    def __vehicle_diesel_count__(self, start_date=None, end_date=None, cameraids=None):
        self.temp = 0
        if start_date is None:
            for result_object in self.collection.find({"attributes.fuel_type": {'$exists': True}}):
                if result_object['attributes']['fuel_type'] == "DIESEL":
                    self.temp = self.temp + 1
            return self.temp

        else:
            for result_object in self.collection.find({"attributes.fuel_type": {'$exists': True},
                                                       "detection_datetime": {"$gte": start_date, "$lt": end_date}}):
                if result_object['attributes']['fuel_type'] == "DIESEL":
                    self.temp = self.temp + 1
            return self.temp

    def __vehicle_electric_count__(self, start_date=None, end_date=None, cameraids=None):
        self.temp = 0
        if start_date is None:
            for result_object in self.collection.find({"attributes.fuel_type": {'$exists': True}}):
                if result_object['attributes']['fuel_type'] == "ELECTRIC":
                    self.temp = self.temp + 1
            return self.temp

        else:
            for result_object in self.collection.find({"attributes.fuel_type": {'$exists': True},
                                                       "detection_datetime": {"$gte": start_date, "$lt": end_date}}):
                if result_object['attributes']['fuel_type'] == "ELECTRIC":
                    self.temp = self.temp + 1
            return self.temp

    def __vehicle_hybrid_count__(self, start_date=None, end_date=None, cameraids=None):
        self.temp = 0
        if start_date is None:
            for result_object in self.collection.find({"attributes.fuel_type": {'$exists': True}}):
                if result_object['attributes']['fuel_type'] == "HYBRID":
                    self.temp = self.temp + 1
            return self.temp

        else:
            for result_object in self.collection.find({"attributes.fuel_type": {'$exists': True},
                                                       "detection_datetime": {"$gte": start_date, "$lt": end_date}}):
                if result_object['attributes']['fuel_type'] == "HYBRID":
                    self.temp = self.temp + 1
            return self.temp

    def __vehicle_unknown_fuel_count__(self, start_date=None, end_date=None, cameraids=None):
        self.temp = 0
        if start_date is None:
            self.temp = self.__vehicle_count__() - (self.__vehicle_petrol_count__() + self.__vehicle_diesel_count__() +
                                                self.__vehicle_electric_count__() + self.__vehicle_hybrid_count__())
        else:
            self.temp = self.__vehicle_count__(start_date, end_date) - \
                        (self.__vehicle_petrol_count__(start_date, end_date)
                         + self.__vehicle_diesel_count__(start_date, end_date)
                         + self.__vehicle_electric_count__(start_date, end_date)
                         + self.__vehicle_hybrid_count__(start_date, end_date))
        return self.temp


if __name__ == '__main__':
    main()

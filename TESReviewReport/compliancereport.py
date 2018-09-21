__author__ = 'Tom'
__doc__ = """Tools to generate the report of the compliance level from the database"""
import argparse
import base64
import html
import io
import json
import re
import sys
import jinja2
import os
from jinja2 import Template, Environment, PackageLoader, meta
import pdfkit
from bson.objectid import ObjectId
from datetime import datetime
from extractdata import GraphRawData, DataExtractor
from piechart import create_pie_chart, create_line_chart
from PIL import ImageColor

# Default colors of the pie chart.


def export_pdf_report(startdate=None, enddate=None, cameraids=None):

    if startingdate is not None:
        if cameraids is not None:
            v = DataExtractor(startdate, enddate, cameraids).data
        else:
            v = DataExtractor(startdate, enddate).data
    elif cameraids is not None:
        v = DataExtractor(cameraids=cameraids).data
    else:
        v = DataExtractor().data

    generate_report(v)


def generate_report(data: GraphRawData):
    """
    Generates the compliance report, serializes it and writes it to the output file.
    :param data: instance of extractdata.GraphRawData
    :param output_file: file-like object were the report will be saved.
    :param output_format: selects the format of the report. The supported values are 'html', 'email', 'json', 'json_and_image'
    """

    pie_colors = {'vehicles_wider_than_220': '#ff0000',
                  'vehicles_smaller_than_220': '#06bf00',
                  'vehicles_unknown_size': '#2cade8',
                  'petrol': '#43fc00',
                  'diesel': '#000000',
                  'electrical': '#fcfc00',
                  'hybrid': '#0044ff',
                  'unknown_fuel': '#62098e'
                  }

    dimensions = [
        [data.vehicles_larger_than_220cm, pie_colors['vehicles_wider_than_220']],
        [data.vehicles_smaller_than_220cm, pie_colors['vehicles_smaller_than_220']],
        [data.vehicles_unknown_size_count, pie_colors['vehicles_unknown_size']]
    ]

    fuels = [
        [data.vehicles_petrol_count, pie_colors['petrol']],
        [data.vehicles_diesel_count, pie_colors['diesel']],
        [data.vehicles_hybrid_count, pie_colors['hybrid']],
        [data.vehicles_unknown_fuel_count, pie_colors['unknown_fuel']]
    ]

    # Pie chart image in PNG format.
    chart_bytes_dimentions = create_pie_chart(dimensions, ImageColor.getcolor('gray', 'RGBA'),
                                   ImageColor.getcolor('white', 'RGBA'), (300, 300), "widthChart")

    chart_bytes_fuels = create_pie_chart(fuels, ImageColor.getcolor('gray', 'RGBA'),
                                              ImageColor.getcolor('white', 'RGBA'), (300, 300), "fuelChart")

    create_line_chart(data.vehicles_time_count, "timeGraph")


    v = dict()

    # Remember to escape all the non-numeric fields.

    # Display Camera name?

    # Load all data from Graphrawdata and compute it into useful information
    v['n_total_vehicles'] = data.vehicles_larger_than_220cm + data.vehicles_smaller_than_220cm + data.vehicles_unknown_size_count
    v['p_total_vehicles'] = 100.0

    v['n_vehicles_larger_220'] = data.vehicles_larger_than_220cm
    v['p_vehicles_larger_220'] = (data.vehicles_larger_than_220cm / v['n_total_vehicles'])*100

    v['n_vehicles_smaller_220'] = data.vehicles_smaller_than_220cm
    v['p_vehicles_smaller_220'] = (data.vehicles_smaller_than_220cm / v['n_total_vehicles'])*100

    v['n_unknown_size'] = data.vehicles_unknown_size_count
    v['p_unknown_size'] = (data.vehicles_unknown_size_count / v['n_total_vehicles'])*100

    v['n_petrol'] = data.vehicles_petrol_count
    v['p_petrol'] = (data.vehicles_petrol_count / v['n_total_vehicles']) * 100
    v['n_diesel'] = data.vehicles_diesel_count
    v['p_diesel'] = (data.vehicles_diesel_count / v['n_total_vehicles']) * 100
    v['n_electric'] = data.vehicles_electric_count
    v['p_electric'] = (data.vehicles_electric_count / v['n_total_vehicles']) * 100
    v['n_hybrid'] = data.vehicles_hybrid_count
    v['p_hybrid'] = (data.vehicles_hybrid_count / v['n_total_vehicles']) * 100

    v['n_unknown_fuel'] = data.vehicles_unknown_fuel_count
    v['p_unknown_fuel'] = (data.vehicles_unknown_fuel_count / v['n_total_vehicles']) * 100

    if hasattr(data, "start_date"):
        v['start_date'] = data.start_date
        v['end_date'] = data.end_date
    else:
        v['start_date'] = ""
        v['end_date'] = ""

    if hasattr(data, "cameraids"):
        v['cameraids'] = data.cameraids
    else:
        v['cameraids'] = " "



    # Load HTML file into jinja2 template to be streamed to file (same location as the py script)
    template_loader = jinja2.FileSystemLoader(searchpath="./")
    template_env = jinja2.Environment(loader=template_loader)
    TEMPLATE_FILE = "template.html"
    template = template_env.get_template(TEMPLATE_FILE)

    template.stream(n_total_vehicles=v['n_total_vehicles'], p_total_vehicles=int(v['p_total_vehicles']),
                    n_vehicles_larger_220='{:5}'.format(v['n_vehicles_larger_220']),
                    p_vehicles_larger_220='{0:.3}'.format(v['p_vehicles_larger_220']),
                    n_vehicles_smaller_220=v['n_vehicles_smaller_220'],
                    p_vehicles_smaller_220='{0:.3}'.format(v['p_vehicles_smaller_220']),
                    n_petrol=v['n_petrol'], p_petrol='{0:.3}'.format(v['p_petrol']),
                    n_diesel=v['n_diesel'], p_diesel='{0:.3}'.format(v['p_diesel']),
                    n_hybrid=v['n_hybrid'], p_hybrid='{0:.3}'.format(v['p_hybrid']),
                    n_electric=v['n_electric'], p_electric='{0:.3}'.format(v['p_electric']),
                    n_unknown=v['n_unknown_fuel'], p_unknown='{0:.3}'.format(v['p_unknown_fuel']),
                    petrolColor=pie_colors['petrol'], dieselColor=pie_colors['diesel'],
                    electricColor=pie_colors['electrical'], hybridColor=pie_colors['hybrid'],
                    widerColor=pie_colors['vehicles_wider_than_220'], smallerColor=pie_colors['vehicles_smaller_than_220'],
                    unknownWidthColor=pie_colors['vehicles_unknown_size'], unknownFuelColor=pie_colors['unknown_fuel'],
                    StartDate=v['start_date'], EndDate=v['end_date'], CustomerName="Transport For London").dump("Report.html")

    time = datetime.now()

    name = "export/Automated Report " + str(time.date()) + "--" + str(time.hour) + "-" + str(time.minute) \
           + "-" + str(time.second) + ".pdf"

    pdfkit.from_file("report.html", name)

    # Clear up directory by removing un needed files
    if os.path.exists("Report.html"):
        os.remove("Report.html")

    if os.path.exists("Images/fuelChart.png"):
        os.remove("Images/fuelChart.png")

    if os.path.exists("Images/widthChart.png"):
        os.remove("Images/widthChart.png")

    if os.path.exists("Images/timeGraph.png"):
        os.remove("Images/timeGraph.png")


def parse_datetime_string(s):
    """
    Converts YYYY-MM-DD hh:mm:ss or YYYY-MM-DD string into a datetime object.
    :param s: string in YYYY-MM-DD hh:mm:ss or YYYY-MM-DD format.
    :return: datetime object or None.
    """
    if isinstance(s, datetime):
        return s

    res = re.match('(?P<year>[0-9]{4,})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})\s*' +
                   '(?P<hh>[0-9]{2}):(?P<mm>[0-9]{2}):(?P<ss>[0-9]{2})', s)

    if res is not None:
        v = res.groupdict()
        return datetime(
            int(v['year']), int(v['month']), int(v['day']),
            int(v['hh']), int(v['mm']), int(v['ss']))
    else:
        res = re.match('(?P<year>[0-9]{4,})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})', s)

        if res is not None:
            v = res.groupdict()
            return datetime(int(v['year']), int(v['month']), int(v['day']))

    return None


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--startdate', help='Start date/time of the report. Format: YYYY-MM-DD hh:mm:ss')
    parser.add_argument('--stopdate', help='Stop date/time of the report. Format: YYYY-MM-DD hh:mm:ss')
    parser.add_argument('--cameraids', help='ids of the camera that are to be queried in the report, format = String')
    args = vars(parser.parse_args())

    startingdate = args.get('startdate')
    if not isinstance(startingdate, datetime):
        startingdate = parse_datetime_string(str(startingdate))

    endingdate = args.get('stopdate')
    if not isinstance(endingdate, datetime):
        endingdate = parse_datetime_string(str(endingdate))

    cameraids = args.get('cameraids')

    #-----------DEBUGGING HELPER-----------#
    startingdate = datetime(2018, 7, 31, 0, 0, 0)
    endingdate = datetime(2018, 8, 1, 0, 0, 0)
    cameraids = {"5b59e576c493820f68746f0e", "5b59e576c493820f68746f0a"}
    #------------------END-----------------#

    if startingdate is not None:
        if cameraids is not None:
            export_pdf_report(startingdate, endingdate, cameraids)
        else:
            export_pdf_report(startingdate, endingdate)
    elif cameraids is not None:
        export_pdf_report(cameraids=cameraids)
    else:
        export_pdf_report()





    # Get the list of e-mail recipients.
    # Extract the statistics.
    #stat_extractor = CdmStatsExtractor(host=host, port=port, database=db, user_id=user_id, pwd=pwd)
    #stat = stat_extractor.get_statistics(start_time, stop_time)
    # Generate the html report.
    #generate_report(stat, sys.stdout, out_format)

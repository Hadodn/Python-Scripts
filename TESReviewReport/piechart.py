__author__ = 'Christian'

from PIL import Image, ImageDraw, ImageColor
import numpy as np
import matplotlib.pyplot as plt
import io
import os

def create_pie_chart(values, pie_color, bg_color, image_size, imagename):

    scale = 3.0
    image_size = [int(image_size[0] * scale), int(image_size[1] * scale)]

    #Creates the image.
    im = Image.new('RGBA', image_size, bg_color)

    #Empty pie chart.
    draw = ImageDraw.Draw(im)
    draw.ellipse([0, 0, image_size[0]-1, image_size[1]-1], fill=pie_color)

    #Calculates the sum of all values.
    sum = 0
    for v, color in values:
        assert (v >= 0)
        sum += v

    #Draw all sectors.
    pie_size = [0, 0, image_size[0] - 1, image_size[1] - 1]

    if sum > 0:
        angle_offset = 0
        for v, color in values:
            perc = 360 * float(v) / sum
            start = angle_offset
            stop = start + perc

            #From counterclockwise to clockwise. Rotate the chart to start from the vertical axis.
            start, stop = [270 - stop, 270 - start]

            draw.pieslice(pie_size, int(start), int(stop), fill=color)
            angle_offset += perc



    #Scale down with interpolation.
    im = im.resize((int(image_size[0] / scale), int(image_size[1] / scale)), resample=Image.ANTIALIAS)
    currentdir = os.path.dirname(__file__)
    filename = os.path.join(currentdir, '\TESReviewReport/Images/'+imagename)
    directory = os.path.join(currentdir, '\TESReviewReport/Images')
    if not os.path.exists(directory):
        os.makedirs(directory)
    im.save(filename + ".png", format='PNG')
    stream = io.BytesIO()
    return stream.getvalue()


def create_line_chart(values, imagename):
    # Make Line Graph
    x = values
    plt.figure(figsize=(15, 5))
    plt.xticks(range(24))
    plt.plot(x, color='green', marker='o')
    for a in range(24):
        plt.text(a-0.5, x[a]+10, x[a])
    plt.title("Traffic Count per hour")
    plt.ylabel('Vehicle Count')
    plt.xlabel('Time')

    # Export Line Graph to image
    currentdir = os.path.dirname(__file__)
    filename = os.path.join(currentdir, '\TESReviewReport/Images/' + imagename)
    directory = os.path.join(currentdir, '\TESReviewReport/Images')
    if not os.path.exists(directory):
        os.makedirs(directory)
    plt.savefig(filename + ".png", dpi=600)
    stream = io.BytesIO()
    return stream.getvalue()




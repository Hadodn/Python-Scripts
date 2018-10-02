import json
from glob import glob
import os
import cv2 as cv
import xml.etree.ElementTree as ET


jpg = glob('*.jpg')

for j in jpg:
    fileName = os.path.splitext(j)[0]
    fileExtension = os.path.splitext(j)[1]
    with open('C:/Users\Thomas Haddon\Documents\TFS\Projects\FixedCamera\RedRoutePluginTest/bin/x64\Debug\darkflowmaster\TES_Model/temp/000000_car.xml') as xml_file:
        data = xml_file.readlines()
        data[2] = '  <filename>' + fileName + fileExtension + '</filename>\n'
        img = cv.imread(fileName + fileExtension)
        height, width = img.shape[:2]

        data[5] = '    <width>' + str(width) + '</width>\n'
        data[6] = '    <height>' + str(height) + '</height>\n'
        data[7] = '    <depth>3</depth>'

        data[17] = '      <xmax>' + str(width) + '</xmax>\n'
        data[18] = '      <ymax>' + str(height) + '</ymax>\n'
        with open(fileName + '_car.xml', 'w') as file:
            file.writelines(data)




#my_file = open(filename, "r")
#lines_of_file = my_file.readlines()
#lines_of_file.insert(-1, "This line is added one before the last line")
#my_file.writelines(lines_of_file)

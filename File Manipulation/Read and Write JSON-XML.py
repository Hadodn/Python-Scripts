import json
from glob import glob
import os
import xml.etree.ElementTree as ET


xml = glob('./*.xml')

for j in xml:
    with open(j) as xml_file:
        data = xml_file.readlines()
        print(data)
        data[1] = '  <folder>wheel_data/images</folder>\n'

        with open(j, 'w') as file:
            file.writelines(data)




#my_file = open(filename, "r")
#lines_of_file = my_file.readlines()
#lines_of_file.insert(-1, "This line is added one before the last line")
#my_file.writelines(lines_of_file)

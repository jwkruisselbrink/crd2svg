import svgwrite
import os
import re
import math

def readShape(filename):
    coordinates = []
    xyz = open(filename)
    name = os.path.splitext(os.path.basename(filename))[0]
    regex = re.compile(r"^\s*name:", re.IGNORECASE)
    for line in xyz:
        if regex.match(line):
            name = regex.sub('', line).strip()
        else:
            x,y = line.split()
            coordinates.append([float(x), float(y)])
    xyz.close()
    return {
        "name": name,
        "coordinates": coordinates
    }

def printShape(shape):
    print("name: %s" % shape['name'])
    for record in shape['coordinates']:
        print("(%10.5f,%10.5f)"% (record[0], record[1]))

def drawPoint(dwg, point, stroke_width):
    point = dwg.add(dwg.circle(
        center = point,
        r = 2 * stroke_width,
        stroke = svgwrite.rgb(0, 0, 0, '%'),
        fill='black',
        stroke_width = stroke_width
    ))
    return point

def drawSegment(dwg, p1, p2, stroke_width):
    line = dwg.add(dwg.line(p1, p2,
        stroke = svgwrite.rgb(0, 0, 0, '%'),
        stroke_width = stroke_width
    ))
    return line

def drawPolygon(dwg, shape, stroke_width):
    g = dwg.add(svgwrite.container.Group(id=shape['name']))
    polygon = g.add(svgwrite.shapes.Polygon(
        points = shape['coordinates'],
        stroke = svgwrite.rgb(0, 0, 0, '%'),
        stroke_width = stroke_width
    ))
    polygon.fill('green', opacity=0.5)
    text = g.add(dwg.text(shape['name'],
        insert=centroid(shape['coordinates']),
        font_size=12*stroke_width,
        font_family="Arial")
    )
    return polygon

def createSvg(shapes, filename):
    xMin, xMax, yMin, yMax = minimax(shapes)
    viewMarginX = .1 * (xMax - xMin) if xMax > xMin else 10
    viewMarginY = .1 * (yMax - yMin) if yMax > yMin else 10
    viewWidth = (xMax - xMin) + 2 * viewMarginX
    viewHeight = (yMax - yMin) + 2 * viewMarginY
    strokeWidth = min(viewHeight, viewWidth) * .003
    dwg = svgwrite.Drawing(filename=filename)
    dwg.viewbox(xMin - viewMarginX, yMin - viewMarginY, viewWidth, viewHeight)
    for shape in shapes:
        points = shape['coordinates']
        if len(points) == 1:
            drawPoint(dwg, points[0], strokeWidth)
        if len(points) == 2:
            drawSegment(dwg, points[0], points[1], strokeWidth)
        elif len(points) > 2:
            drawPolygon(dwg, shape, strokeWidth)
    dwg.save(pretty=True)

def minimax(shapes):
    xMin, xMax, yMin, yMax = (math.inf, -math.inf, math.inf, -math.inf)
    for shape in shapes:
        points = shape['coordinates']
        for point in points:
            xMin = xMin if xMin < point[0] else point[0]
            xMax = xMax if xMax > point[0] else point[0]
            yMin = yMin if yMin < point[1] else point[1]
            yMax = yMax if yMax > point[1] else point[1]
    xMax = xMax if xMin < xMax else xMax
    yMax = yMax if yMin < yMax else yMax
    return (xMin, xMax, yMin, yMax)

def centroid(vertexes):
    _x_list = [vertex [0] for vertex in vertexes]
    _y_list = [vertex [1] for vertex in vertexes]
    _len = len(vertexes)
    _x = sum(_x_list) / _len
    _y = sum(_y_list) / _len
    return(_x, _y)

import argparse
from os import listdir
from os.path import isfile, join

parser = argparse.ArgumentParser()
parser.add_argument("--directory", "-d", help="Directory containig coordinate files")
parser.add_argument("--output", "-o", help="Output filename")

args = parser.parse_args()
folder = args.directory if args.directory else './'
output = args.output if args.output else 'coordinates.svg'

filenames = [f for f in listdir(folder) if isfile(join(folder, f))]

shapes = []
for filename in filenames:
    if filename.endswith(".crd"):
        shape = readShape(join(folder,filename))
        shapes.append(shape)

createSvg(shapes, output)

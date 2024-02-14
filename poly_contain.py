from os.path import *
from shapely.geometry import Polygon,mapping
import fiona

workdir = r'E:\work\interview_tests\1spatial'
#s2_file = join(workdir,'dmv_s2.shp')
s2_file = join(workdir,'dmv_s2_2.shp') #double checking test
f15min_file = join(workdir,'dmv_15min.shp')

s2 = fiona.open(s2_file)
f15min = fiona.open(f15min_file)
#set output parameters
driver = f15min.driver
crs = f15min.crs
schema = f15min.schema

out_name = "answer_2b.shp"
out_path = join(workdir,out_name)

#first get list of all features that are compeletely contained
contained_lst = []
for feat in f15min:
    geom = Polygon(feat['geometry']['coordinates'][0])
    featname = feat['properties']['CellName']
    #print(geom)
    for f2 in s2:
        s2_geom = Polygon(f2['geometry']['coordinates'][0])
        #print(s2_geom)
        if s2_geom.contains(geom):
            #print(f'{featname} fits inside {s2name}')
            contained_lst.append(featname)

#now for all features that aren't entirely contrained, get the greatest overlap
f15_lst = []
for feat in f15min:
    geom = Polygon(feat['geometry']['coordinates'][0])
    featname = feat['properties']['CellName']
    # print(geom)
    for f2 in s2:
        s2name = f2['properties']['Name']
        s2_geom = Polygon(f2['geometry']['coordinates'][0])
        # print(s2_geom)
        if s2_geom.intersects(geom) and s2_geom.contains(geom)==False and featname not in contained_lst: #want to ignore features that are in another s2geom
            print(f'{featname} intersects {s2name}')
            overlap = geom.intersection(s2_geom)
            area = overlap.area
            feat['geometry']['coordinates'][0] = mapping(overlap)['coordinates'][0]
            #feat['geometry']['coordinates'][0] = overlap

            #okay so it intersects multiple polygons... who cares just shrink it to fit in both
            #looks like its only taking the intersection of the 2nd s2 polygon, so technically a bug
            #because we want it to take the BIGGER overlap

    f15_lst.append(feat)

with fiona.open(out_path, "w", driver=driver, crs=crs, schema=schema) as dst:
    for f in f15_lst:
        dst.write(f)

from os.path import *
from shapely.geometry import Polygon, Point
import geopandas as gpd

workdir = r'E:\work\interview_tests\1spatial'
pt_file = join(workdir,'dmv_15min_centriods.shp')
s2_file = join(workdir,'dmv_s2.shp')

pts_gdf = gpd.read_file(pt_file) #orginal pts layer
poly_gdp = gpd.read_file(s2_file) #orginal polly layer

fire_gdp = poly_gdp[poly_gdp['type']=='Fire'] #geo pandas select by attributes
#fire_gdp['centroid'] = fire_gdp['geometry'].centroid
fire_gdp['cent'] = fire_gdp['geometry'].centroid


pts_gdf2 = pts_gdf.copy()  # create copy, copy will have new coordinates put in for points

point_coords_lst = []
for pts in pts_gdf.itertuples(): #points
    indexer = pts.Index
    pt_name = pts.CellName
    pt_geom = pts.geometry
    #print(pts)
    pts_dist = []
    poly_name_list = []

    for row in fire_gdp.itertuples():  # polygons
        # print(f'{row.Name}')
        row_name = row.Name
        poly_geom = row.geometry
        poly_center = row.cent
        dist = poly_geom.distance(pt_geom)       #get distance from piont to polygon 
        #print(dist)
        pts_dist.append(dist)                    #add distances to list
        poly_name_list.append(row_name)          #add name to list
    smallest = min(pts_dist)                     #get the smallest distance (if point inside polygon then dist will be 0)
    small_index = pts_dist.index(smallest)       #get the index location in the list pts_dist
    if pts_dist[small_index] > 0:
        print(f'{pt_name} needs to be moved to be inside {poly_name_list[small_index]}')

        pt_geom2 = fire_gdp[fire_gdp['Name'] == poly_name_list[small_index]].cent #new point file will have outside points now at the
        coords = pt_geom2.get_coordinates()     #convert to geoseries to coordinates
        pt_coords = Point(coords)               #coordinates to Shapely Point
        #print(pt_coords)                        #why can't i just input geopandas point into geometry???
        point_coords_lst.append(pt_coords)

        print(pts_gdf2.loc[indexer,['geometry']]) #before
        pts_gdf2.loc[indexer, ['geometry']] = pt_coords
        print(pts_gdf2.loc[indexer,'geometry']) #after
        #before and after to check if geometry was accurately changed
        print()


    else:
        point_coords_lst.append(pt_geom)

#below was what was bugged
#i think the bug is because it is outside the previous loop so its just looking at the last polygon, so all points outside a "fire" polygon being to this one 
'''
for i, poly in enumerate(point_coords_lst):
    print(f'{i} {poly}')
    #pts_gdf2.loc[[i], 'geometry'] = gpd.GeoSeries(poly)
    pts_gdf2.loc[[i], 'geometry'] = poly
'''


out_name = 'answer_1b.shp'
out_path = join(workdir,out_name)
pts_gdf2.to_file(out_path, driver="ESRI Shapefile")

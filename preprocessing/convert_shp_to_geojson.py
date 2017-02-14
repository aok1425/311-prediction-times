# https://gist.github.com/frankrowe/6071443

import shapefile
# read the shapefile
reader = shapefile.Reader("data/shape-files/cb_2015_25_bg_500k.shp")
fields = reader.fields[1:]
field_names = [field[0] for field in fields]
buffer = []
for sr in reader.shapeRecords():
    atr = dict(zip(field_names, sr.record))
    if atr['COUNTYFP'] == '025':
        geom = sr.shape.__geo_interface__
        buffer.append(dict(type="Feature", geometry=geom, properties=atr)) 

from json import dumps
geojson = open("data/shape-files/cb_2015_25_bg_500k.geojson", "w")
geojson.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
geojson.close()        
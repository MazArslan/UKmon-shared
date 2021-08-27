#
# Google maps with python
#
import sys
import os
import configparser
import gmplot
import xmltodict
import glob
from cryptography.fernet import Fernet


def munchKML(fname):
    with open(fname) as fd:
        x = xmltodict.parse(fd.read())
        cname = x['kml']['Folder']['name']
        coords = x['kml']['Folder']['Placemark']['MultiGeometry']['Polygon']['outerBoundaryIs']['LinearRing']['coordinates']
        coords = coords.split('\n')
        lats = []
        lngs = []
        for lin in coords:
            s = lin.split(',')
            lngs.append(float(s[0]))
            lats.append(float(s[1]))

    return cname, lats, lngs


def decodeApiKey(enckey):
    key = open(os.path.expanduser('~/.ssh/gmap.key'), 'rb').read()
    f = Fernet(key)
    apikey = f.decrypt(enckey.encode('utf-8'))
    return apikey.decode('utf-8')


if __name__ == '__main__':
    kmlsource = sys.argv[2]
    outdir = sys.argv[3]
    if len(sys.argv) > 4:
        showMarker=True
    else:
        showMarker=False

    config = configparser.ConfigParser()
    config.read(sys.argv[1])
    apikey = decodeApiKey(config['maps']['apikey'])
    kmltempl = config['maps']['kmltemplate']

    gmap = gmplot.GoogleMapPlotter(52, -1.0, 5, apikey=apikey, 
        title='Camera Coverage', map_type='satellite')

    flist = glob.glob1(kmlsource, kmltempl)
    cols = list(gmplot.color._HTML_COLOR_CODES.keys())
    i=0
    for col, fn in zip(cols,flist):
        cn, lats, lngs = munchKML(os.path.join(kmlsource,fn))
        print(cn, fn)
        gmap.polygon(lats, lngs, color=col, edge_width=1)
        if showMarker is True:
            gmap.text((max(lats)+min(lats))/2, (max(lngs)+min(lngs))/2, cn)

    # Draw the map to an HTML file:
    gmap.draw(os.path.join(outdir, 'coverage.html'))

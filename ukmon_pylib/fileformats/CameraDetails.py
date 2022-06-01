# Create a data type for the camera location details
import numpy
import sys
import os
import numpy as np


# defines the data content of a UFOAnalyser CSV file
CameraDetails = numpy.dtype([('Site', 'S32'), ('CamID', 'S32'), ('LID', 'S16'),
    ('SID', 'S8'), ('Camera', 'S16'), ('Lens', 'S16'), ('xh', 'i4'),
    ('yh', 'i4'), ('Longi', 'f8'), ('Lati', 'f8'), ('Alti', 'f8'), 
    ('camtyp', 'i4'), ('dummycode','S6'),('active','i4')])


class SiteInfo:
    def __init__(self, fname=None):
        if fname is None:
            datadir = os.getenv('DATADIR')
            if datadir is None:
                print('export DATADIR first')
                exit(1)
            fname = os.path.join(datadir, 'consolidated', 'camera-details.csv')

        self.camdets = numpy.loadtxt(fname, delimiter=',', skiprows=1, dtype=CameraDetails)
        #print(self.camdets)

    def getCameraOffset(self, statid):
        spls=statid.split('_')
        statid = statid.encode('utf-8')
        cam = numpy.where(self.camdets['CamID'] == statid) 
        if len(cam[0]) == 0:
            statid = statid.upper()
            cam = numpy.where(self.camdets['CamID'] == statid) 
        if len(cam[0]) == 0:
            cam = numpy.where(self.camdets['dummycode'] == statid) 
        if len(cam[0]) ==0:
            cam = numpy.where(numpy.logical_and(self.camdets['LID']==spls[0].encode('utf-8'), self.camdets['SID']==spls[1].encode('utf-8')))

        # if we can't find the camera, assume its inactive
        if len(cam[0]) == 0:
            return -1
        else:
            c = cam[0][0]
            return c

    def GetSiteLocation(self, camname):
        camname = camname.encode('utf-8')
        eles = camname.split(b'_')
        if len(eles) > 2:
            lid = eles[0].strip() + b'_' + eles[1].strip()
        else:
            lid = eles[0].strip()
        if len(eles) > 1:
            sid = camname.split(b'_')[len(eles)-1].strip()
            # print(lid, sid)
            cam = numpy.where((self.camdets['LID'] == lid) & (self.camdets['SID'] == sid))
            if len(cam[0]) == 0:
                sid = sid.upper()
                lid = lid.upper()
                cam = numpy.where((self.camdets['LID'] == lid) & (self.camdets['SID'] == sid))

        else:
            cam = numpy.where((self.camdets['LID'] == lid))
        if len(cam[0]) == 0:
            cam = numpy.where((self.camdets['dummycode'] == lid))
            if len(cam[0]) == 0:
                return 0, 0, 0, 0, camname.decode('utf-8')
        #print(cam)
        c = cam[0][0]
        longi = self.camdets[c]['Longi']
        lati = self.camdets[c]['Lati']
        alti = self.camdets[c]['Alti']
        tz = 0  # camdets[c]['tz']
        site = self.camdets[c]['Site'].decode('utf-8').strip()
        camid = self.camdets[c]['CamID'].decode('utf-8').strip()
        if camid == '':
            return lati, longi, alti, tz, site
        else:
            return lati, longi, alti, tz, site + '/' + camid

    def getDummyCode(self, lid, sid):
        lid = lid.encode('utf-8')
        sid = sid.encode('utf-8')
        cam = numpy.where((self.camdets['LID'] == lid) & (self.camdets['SID'] == sid))   
        if len(cam[0]) == 0:
            sid = sid.upper()
            lid = lid.upper()
            cam = numpy.where((self.camdets['LID'] == lid) & (self.camdets['SID'] == sid))
        if len(cam[0]) == 0:
            return 'Unknown'
        else:
            c = cam[0][0]
            return self.camdets[c]['dummycode'].decode('utf-8').strip()

    def getFolder(self, statid):
        c = self.getCameraOffset(statid)
        if c < 0:
            return 'Unknown'
        else:
            site = self.camdets[c]['Site'].decode('utf-8').strip()
            camid = self.camdets[c]['CamID'].decode('utf-8').strip()
            return site + '/' + camid

    def checkCameraActive(self, statid):
        c = self.getCameraOffset(statid)
        if c < 0:
            return 'Unknown'
        else:
            if self.camdets[c]['active'] == 0: 
                return False
            return True

    def getActiveCameras(self):
        return self.camdets[self.camdets['active']==1]

    def getCameraType(self, statid):
        c = self.getCameraOffset(statid)
        if c < 0:
            return -1
        else:
            return self.camdets[c]['camtyp'] 

    def getAllCamsAndFolders(self, isactive=False):
        # fetch camera details from the CSV file
        fldrs = []
        cams = []

        for row in self.camdets:
            if isactive is True and row['active'] == 0: 
                continue
            if row[0][:1] != '#':
                # print(row)
                if row[1] == '':
                    fldrs.append(row[0].decode('utf-8'))
                else:
                    fldrs.append(row[0].decode('utf-8') + '/' + row[1].decode('utf-8'))
                if int(row[11]) == 1:
                    cams.append(row[2].decode('utf-8') + '_' + row[3].decode('utf-8'))
                else:
                    cams.append(row[2].decode('utf-8'))
        return cams, fldrs

    def getAllCamsStr(self, onlyActive=False):
        if onlyActive is False:
            cams, _ = self.getAllCamsAndFolders()
            cams.sort()
            tmpcams = ''
            for cam in cams:
                tmpcams = tmpcams + cam + ' ' 
            return tmpcams.strip()
        else:
            cams = self.getActiveCameras()
            tmpcams = ''
            for cam in cams:
                cname = cam['CamID'].decode('utf-8')
                if ' ' not in cname:
                    tmpcams = tmpcams + cname + ' ' 
            #tcc = tmpcams.split()
            #tcc.sort()
            #tmpcams = ''
            #for cname in tcc:
            #    tmpcams = tmpcams + cname + ' ' 
            return tmpcams.strip()

    def getAllLocsStr(self, onlyActive=False):
        if onlyActive is False:
            _, locs = self.getAllCamsAndFolders()
            locs.sort()
            tmpcams = ''
            for loc in locs:
                loc = loc.split('/')
                tmpcams = tmpcams + loc + ' ' 
            return tmpcams.strip()
        else:
            cams = self.getActiveCameras()
            tmpcams = ''
            for cam in cams:
                if cam['active']==1:
                    cname = cam['Site'].decode('utf-8')
                    if ' ' not in cname:
                        tmpcams = tmpcams + cname + ' ' 
            return tmpcams.strip()

    def saveAsR(self, outfname):
        with open(outfname, 'w') as outf:
            outf.write('stations <- list(\n')
            cams = numpy.unique(self.camdets['Site'])
            for cam in cams:
                outf.write('"{}",c('.format(cam.decode('utf-8')))
                rws = self.camdets[self.camdets['Site'] == cam]
                for rw in rws:
                    if rw['camtyp'] == 1:
                        outf.write('"{}_{}"'.format(rw['LID'].decode('utf-8'), rw['SID'].decode('utf-8')))
                    else:
                        outf.write('"{}"'.format(rw['LID'].decode('utf-8')))
                    if rw != rws[-1]:
                        outf.write(',')
                    else:
                        outf.write(')')
                if cam != cams[-1]:
                    outf.write(',\n')
                else:
                    outf.write('\n)')
    
    def getStationsAtSite(self, sitename, onlyactive=False):
        idlist = []
        bsite = sitename.encode('utf-8')
        fltred = self.camdets[self.camdets['Site'] == bsite]
        if onlyactive is True:
            fltred = fltred[fltred['active']==1]
        for rw in fltred:
            if int(rw['camtyp']) == 1:
                idlist.append(rw['LID'].decode('utf-8') + '_' + rw['SID'].decode('utf-8'))
            else:
                idlist.append(rw['LID'].decode('utf-8'))
        return idlist

    def getSites(self, onlyactive=True):
        sites=[]
        silist=self.camdets['Site']
        silist = np.unique(silist)
        sites = [si.decode('utf-8') for si in silist]
        return sites

    def getUFOCameras(self, onlyactive=False):
        camlist=[]
        ufo=self.camdets[self.camdets['camtyp']==1]
        if onlyactive is True:
            ufo = ufo[ufo['active'] == 1]
        for rw in ufo:
            ufoname = rw['LID'].decode('utf-8') + '_' + rw['SID'].decode('utf-8') 
            camlist.append({'Site':rw['Site'].decode('utf-8'), 'CamID':rw['CamID'].decode('utf-8'), 'dummycode':rw['dummycode'].decode('utf-8'), 'ufoid':ufoname})
        return camlist



def main(sitename):
    ci = SiteInfo()
    spls = sitename.split('_')
    sid = spls[0]
    if len(spls) ==1:
        lid = ''
    else:
        lid = spls[1]
    print(ci.getDummyCode(sid, lid))

    #lati, longi, alti, tz, site = ci.GetSiteLocation(site.encode('utf-8'))
    #print(site, lati, longi, alti, tz)


if __name__ == '__main__':
    main(sys.argv[1])

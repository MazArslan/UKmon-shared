#
# python module to read the IMO Working Shower short List
#

import xmltodict
import datetime

majorlist=['QUA','LYR','ETA','SDA','CAP','PER','AUR','SPE','OCT','DRA',
    'EGE','ORI','STA','NTA','LEO','MON','GEM','URS']


class IMOshowerList:

    def __init__(self, fname):
        with open(fname) as fd:
            tmplist = xmltodict.parse(fd.read())
            self.showerlist = tmplist['meteor_shower_list']['shower']

    def getShowerByCode(self, iaucode):
        for shower in self.showerlist:
            if shower['IAU_code'] == iaucode:
                return shower

    def getStart(self, iaucode, yr=None):
        shower = self.getShowerByCode(iaucode)
        now = datetime.datetime.today().year
        if yr is not None:
            now = yr
        startdate = datetime.datetime.strptime(shower['start'], '%b %d')
        startdate = startdate.replace(year=now)
        return startdate

    def getEnd(self, iaucode, yr=None):
        shower = self.getShowerByCode(iaucode)
        now = datetime.datetime.today().year
        if yr is not None:
            now = yr
        if iaucode == 'QUA':
            now = now + 1
        enddate = datetime.datetime.strptime(shower['end'], '%b %d')
        enddate = enddate.replace(year=now)
        return enddate

    def getPeak(self, iaucode, yr=None):
        shower = self.getShowerByCode(iaucode)
        now = datetime.datetime.today().year
        if yr is not None:
            now = yr
        if iaucode == 'QUA':
            now = now + 1
        enddate = datetime.datetime.strptime(shower['peak'], '%b %d')
        enddate = enddate.replace(year=now)
        return enddate

    def getRvalue(self, iaucode):
        shower = self.getShowerByCode(iaucode)
        return shower['r']

    def getName(self, iaucode):
        shower = self.getShowerByCode(iaucode)
        return shower['name']

    def getVelocity(self, iaucode):
        shower = self.getShowerByCode(iaucode)
        return shower['V']

    def getZHR(self, iaucode):
        shower = self.getShowerByCode(iaucode)
        zhr = shower['ZHR']
        if zhr is None:
            return -1
        else:
            return int(zhr)

    def getRaDec(self, iaucode):
        shower = self.getShowerByCode(iaucode)
        return float(shower['RA']), float(shower['DE'])

    def getActiveShowers(self, datetotest, majonly=False):
        activelist = []
        for shower in self.showerlist:
            shwname = shower['IAU_code']
            yr = datetotest.year
            if shwname == 'QUA':
                yr = yr-1
            start = self.getStart(shwname, yr)
            end = self.getEnd(shwname, yr) + datetime.timedelta(days=3)
            if datetotest > start and datetotest < end:
                if majonly is False or (majonly is True and shwname in majorlist):
                    activelist.append(shwname)
        return activelist

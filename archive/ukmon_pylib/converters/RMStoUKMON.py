""" 
Convert the FTPdetectinfo format to ukmon-specific CSV file containing data 
about single station detections 
"""
# Copyright (C) 2018-2023 Mark McIntyre

from __future__ import print_function, division, absolute_import

import os
import argparse
import datetime
import json
import numpy as np
import pytz
import glob

#import RMS.Astrometry.ApplyAstrometry
from RMS.Astrometry.Conversions import datetime2JD, altAz2RADec
from RMS.Formats import FTPdetectinfo
from RMS.Formats import FFfile
#import RMS.Formats.Platepar
#from RMS.Formats import UFOOrbit
from RMS import Math
import Utils.ShowerAssociation as sa
import RMS.ConfigReader as cr
from RMS.Routines import GreatCircle
import reports.CameraDetails as cc


def findUnprocessedFolders(dir_path, station_list, db, dbtime):
    """ Go through directories and find folders with unprocessed data. """
    processing_list = []
    nowdt = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')
    nowdtint = int(datetime.datetime.now().strftime('%Y%m%d'))
    print(f'{nowdt}: starting findUnprocessedFolders')
    # Go through all station directories
    for station_name in station_list:

        station_path = os.path.join(dir_path, station_name)

        # Go through all directories in stations
        if os.path.isdir(station_path):
            for night_name in os.listdir(station_path):

                night_path = os.path.join(station_path, night_name)
                #print(f'checking {night_path}')
                if night_path not in db: 
                    print('adding', night_path)
                    processing_list.append(night_path)                
                else:
                    spls = night_name.split('_')
                    if int(spls[1]) > nowdtint - 14:
                        ftpf = glob.glob1(night_path, 'FTPdetect*') 
                        if len(ftpf) > 0:
                            ftpd = os.path.getmtime(os.path.join(night_path, ftpf[0]))
                            if ftpd > dbtime:
                                print('ftp newer, adding', night_path)
                                processing_list.append(night_path)                
    nowdt = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')
    print(f'{nowdt}: finished findUnprocessedFolders')
    return processing_list


def loadStations(dir_path):
    """ Load the station names in the processing folder. """

    nowdt = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')
    print(f'{nowdt}: starting loadStations')
    station_list = []

    camdets = cc.SiteInfo()
    cams = camdets.getActiveCameras()['CamID']
    for c in cams:
        station_list.append(c.decode('utf-8'))

    nowdt = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')
    print(f'{nowdt}: finished loadStations')
    return station_list


class PlateparDummy:
    def __init__(self, **entries):
        """ This class takes a platepar dictionary and converts it into an object. """

        self.__dict__.update(entries)
        if not hasattr(self, 'UT_corr'):
            self.UT_corr = 0


def writeUkmonCsv(dir_path, file_name, data):
    """ Write the a Ukmon specific CSV file for single-station data. 

    Arguments:
        dir_path: [str] Directory where the file will be written to.
        file_name: [str] Name of the UFOOrbit CSV file.
        data: [list] A list of meteor entries.

    """
    with open(os.path.join(dir_path, file_name), 'w') as f:

        # Write the header
        f.write("Ver,Y,M,D,h,m,s,Mag,Dur,Az1,Alt1,Az2,Alt2,Ra1,Dec1,Ra2,Dec2,ID,Long,Lat,Alt,Tz,AngVel,Shwr,Filename,Dtstamp\n")

        # Write meteor data to file
        for line in data:

            dt, peak_mag, duration, azim1, alt1, azim2, alt2, ra1, dec1, ra2, dec2, cam_code, lon, lat, \
                elev, UT_corr, shwr, fname, angvel = line

            # Convert azimuths to the astronomical system (+W of due S)
            azim1 = (azim1 - 180) % 360
            azim2 = (azim2 - 180) % 360

            # cater for the possibility that secs+microsecs > 59.99 and would round up to 60
            # causing an invalid time to be written eg 20,55,60.00, instead of 20,56,0.00
            secs = round(dt.second + dt.microsecond / 1000000, 2)
            if secs > 59.99: 
                tmpdt = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, 0, 0, 
                    tzinfo=pytz.UTC) 
                # add 60 seconds on to the datetime
                dt = tmpdt + datetime.timedelta(seconds = secs)
            dtstamp = dt.timestamp()

            f.write('{:s},{:4d},{:2d},{:2d},{:2d},{:2d},{:4.2f},{:.2f},{:.3f},{:.7f},{:.7f},{:.7f},{:.7f},{:.7f},{:.7f},{:.7f},{:.7f},{:s},{:.6f},{:.6f},{:.1f},{:.1f},{:7f},{:s},{:s},{:.6f}\n'.format(
                'UM1', dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second + dt.microsecond/1000000, 
                peak_mag, duration, azim1, alt1, azim2, alt2, ra1, dec1, ra2, dec2, cam_code, lon, lat, 
                elev, UT_corr, angvel, shwr, fname, dtstamp))


def FTPdetectinfo2UkmonCsv(dir_path, out_path):
    """ Convert the FTPdetectinfo file into a ukmon specific CSV file. 
        
    Arguments:
        dir_path: [str] Path of the directory which contains the FTPdetectinfo file.
        out_path: [str] Path of the directory to save the results into

    """
    # Load the FTPdetectinfo file

    ftpdetectinfo_name = None
    for name in os.listdir(dir_path):
        # Find FTPdetectinfo
        if name.startswith("FTPdetectinfo") and name.endswith('.txt') and \
                ("backup" not in name) and ("uncalibrated" not in name):
            ftpdetectinfo_name = name
            break
    if ftpdetectinfo_name is None:
        print('no ftpdetect file - cannot continue')
        return 

    ppfilename = os.path.join(dir_path, 'platepars_all_recalibrated.json')
    if not os.path.isfile(ppfilename):
        print('no platepar file - cannot continue')
        return 

    with open(ppfilename) as f:
        try:
            platepars_recalibrated_dict = json.load(f)
        except:
            print('malformed platepar file - cannot continue')
            return 


    # Load the FTPdetectinfo file
    try:
        meteor_list = FTPdetectinfo.readFTPdetectinfo(dir_path, ftpdetectinfo_name)
    except Exception:
        print('Malformed FTPdetect file') 
        return 
    if len(meteor_list) == 0:
        print('no meteors')
        return
    
    # load a default config file then overwrite the bits of importance
    config = cr.loadConfigFromDirectory('.config', '.')

    fflst = list(platepars_recalibrated_dict.keys())
    if len(fflst) > 0: 
        ff1 = fflst[0]
        pp1 = platepars_recalibrated_dict[ff1]
        config.latitude = pp1['lat']
        config.longitude = pp1['lon']
        config.elevation = pp1['elev']
        # get the shower associations
        color_map='gist_ncar'
        shwrs, _ = sa.showerAssociation(config, [os.path.join(dir_path,ftpdetectinfo_name)], color_map=color_map)
    else:
        print('platepar file empty')
        return 
    # Init the UFO format list
    ufo_meteor_list = []

    # Go through every meteor in the list
    for meteor in meteor_list:

        ff_name, cam_code, meteor_No, n_segments, fps, hnr, mle, binn, px_fm, rho, phi, \
            meteor_meas = meteor

        # Load the platepar from the platepar dictionary
        if ff_name in platepars_recalibrated_dict:
            pp_dict = platepars_recalibrated_dict[ff_name]
            pp = PlateparDummy(**pp_dict)

        else:
            print('Skipping {:s} because no platepar was found for this FF file!'.format(ff_name))
            continue
        
        # Convert the FF file name into time
        dt = FFfile.filenameToDatetime(ff_name)
        try: 
            shwrdets = shwrs[(ff_name,meteor_No)]
            if shwrdets[1] is not None:
                shwr = shwrdets[1].name
            else:
                shwr='spo'
        except KeyError:
            shwr='spo'

        # Extract measurements
        calib_status, frame_n, x, y, ra, dec, azim, elev, inten, mag = np.array(meteor_meas).T

        # If the meteor wasn't calibrated, skip it
        if not np.all(calib_status):
            print('Meteor {:d} was not calibrated, skipping it...'.format(meteor_No))
            continue

        # Compute the peak magnitude
        peak_mag = np.min(mag)

        # Compute the total duration
        first_frame = np.min(frame_n)
        last_frame = np.max(frame_n) 
        duration = (last_frame - first_frame)/fps


        # Compute times of first and last points
        dt1 = dt + datetime.timedelta(seconds=first_frame/fps)
        dt2 = dt + datetime.timedelta(seconds=last_frame/fps)

        
        # Fit a great circle to Az/Alt measurements and compute model beg/end RA and Dec ###

        # Convert the measurement Az/Alt to cartesian coordinates
        # NOTE: All values that are used for Great Circle computation are:
        #   theta - the zenith angle (90 deg - altitude)
        #   phi - azimuth +N of due E, which is (90 deg - azim)
        x, y, z = Math.polarToCartesian(np.radians((90 - azim) % 360), np.radians(90 - elev))

        # Fit a great circle
        C, theta0, phi0 = GreatCircle.fitGreatCircle(x, y, z)

        # Get the first point on the great circle
        phase1 = GreatCircle.greatCirclePhase(np.radians(90 - elev[0]), np.radians((90 - azim[0]) % 360), 
            theta0, phi0)
        alt1, azim1 = Math.cartesianToPolar(*GreatCircle.greatCircle(phase1, theta0, phi0))
        alt1 = 90 - np.degrees(alt1)
        azim1 = (90 - np.degrees(azim1)) % 360

        # Get the last point on the great circle
        phase2 = GreatCircle.greatCirclePhase(np.radians(90 - elev[-1]), np.radians((90 - azim[-1]) % 360),
            theta0, phi0)
        alt2, azim2 = Math.cartesianToPolar(*GreatCircle.greatCircle(phase2, theta0, phi0))
        alt2 = 90 - np.degrees(alt2)
        azim2 = (90 - np.degrees(azim2)) % 360

        # Compute RA/Dec from Alt/Az
        ra1, dec1 = altAz2RADec(azim1, alt1, datetime2JD(dt1), pp.lat, pp.lon)
        ra2, dec2 = altAz2RADec(azim2, alt2, datetime2JD(dt2), pp.lat, pp.lon)

        angLength = Math.angularSeparation(np.radians(ra1), np.radians(dec1), np.radians(ra2), np.radians(dec2))
        angVel = np.degrees(angLength)/duration

        ufo_meteor_list.append([dt1, peak_mag, duration, azim1[0], alt1[0], azim2[0], alt2[0], 
            ra1[0], dec1[0], ra2[0], dec2[0], cam_code, pp.lon, pp.lat, pp.elev, pp.UT_corr, 
            shwr, ff_name, angVel[0]])


    # Construct a file name for the UFO file, which is the FTPdetectinfo file without the FTPdetectinfo 
    #   part
    ufo_file_name = ftpdetectinfo_name.replace('FTPdetectinfo_', 'ukmon_').replace('.txt', '') + '.csv'

    # Write the UFOorbit file
    writeUkmonCsv(out_path, ufo_file_name, ufo_meteor_list)


def processManyFolders(in_dir, out_dir):
    stations = loadStations(in_dir)
    dbfile = os.path.join(in_dir, 'processed_single.txt')
    if not os.path.isfile(dbfile):
        open(dbfile, 'w').close()
    lastmtime = os.path.getmtime(dbfile)
    with open(dbfile, 'r', newline=None) as inf:
        db = inf.readlines()
    db = [li.strip() for li in db]
    processing_list = findUnprocessedFolders(in_dir, stations, db, lastmtime)

    nowdt = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')
    print(f'{nowdt}: starting FTPdetectinfo2UkmonCsv loop')

    for fldr in processing_list:
        print(fldr)
        FTPdetectinfo2UkmonCsv(fldr, out_dir)
        with open(dbfile, 'a+') as outf:
            outf.write('{:s}\n'.format(fldr))

    nowdt = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')
    print(f'{nowdt}: finished FTPdetectinfo2UkmonCsv loop')
    return


if __name__ == "__main__":

    # Init the command line arguments parser
    arg_parser = argparse.ArgumentParser(description="Converts the given FTPdetectinfo or folder of files into a ukmon-specific data format.")

    arg_parser.add_argument('file_path', nargs='+', metavar='FILE_PATH', type=str, 
        help='Path to one or more FTPdetectinfo files.')

    arg_parser.add_argument('out_path', nargs='+', metavar='OUT_PATH', type=str, 
        help='Where to save the output.')

    # Parse the command line arguments
    cml_args = arg_parser.parse_args()

    processManyFolders(cml_args.file_path[0], cml_args.out_path[0])

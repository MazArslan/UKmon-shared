import pandas as pd
import boto3
import shutil
import sys
import os
from traj.pickleAnalyser import getAllMp4s


def getBestNMp4s(yr, mth, numtoget):
    datadir=os.getenv('DATADIR')
    mf = os.path.join(datadir, 'matched', f'matches-full-{yr}.csv')
    matches = pd.read_csv(mf)
    matches = matches[matches._Y_ut == int(yr)]
    matches = matches[matches._M_ut == int(mth)]
    sepdata = matches.sort_values(by=['_mag'])
    sorteddata = sepdata.head(numtoget)

    tmpdir = os.getenv('TMP')
    wsbucket = os.getenv('WEBSITEBUCKET')[5:]
    s3 = boto3.resource('s3')
    mp4df = pd.DataFrame()
    for traj in sorteddata.url:
        trdir = traj[traj.find('reports'):]
        trdir, _ = os.path.split(trdir)
        _, trname = os.path.split(trdir)
        picklefile = trname[:15] + '_trajectory.pickle'
        key = trdir + '/' + picklefile
        locdir = os.path.join(tmpdir, trname)
        os.makedirs(locdir, exist_ok=True)
        key = trdir + '/' + picklefile
        locfname = os.path.join(locdir, picklefile)
        s3.meta.client.download_file(wsbucket, key, locfname)
        key = trdir + '/mpgs.lst'
        locfname = os.path.join(locdir, 'mpgs.lst')
        try:
            s3.meta.client.download_file(wsbucket, key, locfname)
            newdf = getAllMp4s(locdir)
            mp4df = pd.concat([mp4df, newdf])
        except:
            pass
        shutil.rmtree(locdir)

    mp4df = mp4df.drop_duplicates()
    mp4df = mp4df.sort_values(by=['mag']).head(numtoget)
    return list(mp4df.mp4)


if __name__ == '__main__':
    lst = getBestNMp4s(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
    for li in lst:
        print(li)

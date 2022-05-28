import os
import sys
import glob
import shutil

from wmpl.Trajectory.CorrelateRMS import TrajectoryReduced, DatabaseJSON 
#from wmpl.Trajectory.CorrelateRMS import MeteorObsRMS, PlateparDummy, MeteorPointRMS # noqa: F401


# support class so i can add any paired obs objects
class dummyMeteorObsRMS(object):
    def __init__(self, station_code, id):
        self.station_code = station_code
        self.id = id


# merge a distributed engine DB back into the master DB
def mergeDatabases(srcdir, srcdb, masterpth, masterfile):
    newdb = os.path.join(srcdir, srcdb)
    mergedb = DatabaseJSON(newdb)
    mastdb = DatabaseJSON(masterfile)
    mastdb.db_file_path = masterfile
    # merge successful trajectories
    for traj in mergedb.trajectories:
        traj_obj = TrajectoryReduced(traj, json_dict = mergedb.trajectories[traj].__dict__)
        traj_file_path = traj_obj.traj_file_path
        traj_file_path = masterpth + '/' + traj_file_path[traj_file_path.find('trajectories'):]
        traj_obj.traj_file_path = traj_file_path
        mastdb.addTrajectory(traj_file_path, traj_obj=traj_obj)
    # merge failed trajectories 
    for traj in mergedb.failed_trajectories:
        traj_obj = TrajectoryReduced(traj, json_dict = mergedb.failed_trajectories[traj].__dict__)
        traj_file_path = traj_obj.traj_file_path
        traj_file_path = masterpth + '/' + traj_file_path[traj_file_path.find('trajectories'):]
        traj_obj.traj_file_path = traj_file_path
        mastdb.addTrajectory(traj_file_path, traj_obj=traj_obj, failed=True)
    # merge paired obs data
    for p in mergedb.paired_obs:
        ids = mergedb.paired_obs[p]
        for id in ids:
            met_obs = dummyMeteorObsRMS(p, id)
            mastdb.addPairedObservation(met_obs)
    # save the master DB again
    mastdb.save()
    return


# utility to patch the database to have the right trajectory folder
def patchTrajDB(dbfile, targpath, oldstr='/home/ec2-user/data/RMSCorrelate'):

    with open(dbfile, 'r') as inf:
        with open(os.path.join('/tmp/processed_trajectories.json'), 'w') as outf:
            for lin in inf:
                outf.write(lin.replace(oldstr, targpath))
    shutil.copyfile('/tmp/processed_trajectories.json', dbfile)
    return 


# utility to count how many of each type of observation was in a database 
def countDataInDb(path_to_db):
    mergedb = DatabaseJSON(path_to_db)
    trajs = len(mergedb.trajectories)
    failed = len(mergedb.failed_trajectories)
    pairs = len(mergedb.paired_obs)
    print(path_to_db, trajs, failed, pairs)
    return 


# utility to dump the detection dates (JDs) to a file
def dumpJDs(path_to_db, fname):
    mergedb = DatabaseJSON(path_to_db)
    with open(fname,'w') as outf:
        outf.write('traj\n')
        for t in mergedb.trajectories:
            outf.write(f'{t}\n')
        outf.write('failed\n')
        for t in mergedb.failed_trajectories:
            outf.write(f'{t}\n')


# utility to compare two databases and dump the JDs of any new events
def dumpNewEntries(db1, db2, fname):
    olddb = DatabaseJSON(db1)
    newdb = DatabaseJSON(db2)
    newtraj = set(newdb.trajectories) - set(olddb.trajectories)
    newfail = set(newdb.failed_trajectories) - set(olddb.failed_trajectories)
    print(len(newtraj), len(newfail))
    with open(fname,'w') as outf:
        outf.write('traj\n')
        for t in newtraj:
            outf.write(f'{t}\n')
        outf.write('failed\n')
        for t in newfail:
            outf.write(f'{t}\n')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: consolidateDistTraj folder_containing_srcdbs full_path_to_targb')
        exit(0)
    srcdir = sys.argv[1]
    masterdb = sys.argv[2]

    # real path to the trajectories as per the master database
    masterpth = '/home/ec2-user/ukmon-shared/matches/RMSCorrelate'

    flist = glob.glob1(srcdir, '2*.json')
    flist.sort()
    for fl in flist:
        #countDataInDb(os.path.join(srcdir, fl))
        print(fl)
        mergeDatabases(srcdir, fl, masterpth, masterdb)
    patchTrajDB(masterdb, masterpth, oldstr='/home/ec2-user/prod/data/distrib')

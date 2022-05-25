#
# Run the distributed solver
#
# Parameters
#   [int] (optional) days ago to run for
#   [int] (optional) days to check
# for example passing in 2 and 3 will run for two days ago, and scan three days of data for updates
#
# Consumes
#   All single-station data
#
# Produces
#   Solved trajectories
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the configuration
source $here/../config/config.ini >/dev/null 2>&1

if [ $# -gt 0 ] ; then
    if [ "$1" != "" ] ; then
        echo "selecting range"
        MATCHSTART=$1
    fi
    if [ "$2" != "" ] ; then
        MATCHEND=$(( $MATCHSTART - $2 ))
    else
        echo "matchend was not supplied, using 2"
        MATCHEND=$(( $MATCHSTART - 2 ))
    fi
fi
begdate=$(date --date="-$MATCHSTART days" '+%Y%m%d')
rundate=$(date --date="-$MATCHEND days" '+%Y%m%d')

source $SERVERAWSKEYS
AWS_DEFAULT_REGION=eu-west-2 

logger -s -t runMatching "checking correlation server status and starting it"
stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text)
if [ $stat -eq 80 ]; then 
    aws ec2 start-instances --instance-ids $SERVERINSTANCEID
fi
logger -s -t runMatching "waiting for the server to be ready"
while [ "$stat" -ne 16 ]; do
    sleep 5
    echo "checking"
    stat=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State.Code --output text)
done
logger -s -t runMatching "ready to use"

logger -s -t runDistrib "running phase 1 for dates ${begdate} to ${rundate}"
source ~/venvs/${WMPL_ENV}/bin/activate

logger -s -t runDistrib "creating the run script"
execMatchingsh=/tmp/execdistrib.sh
python -m traj.createDistribMatchingSh $MATCHSTART $MATCHEND $execMatchingsh
chmod +x $execMatchingsh

logger -s -t runMatching "get server details"
privip=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].PrivateIpAddress --output text)
while [ "$privip" == "" ] ; do
    sleep 5
    echo "getting ipaddress"
    privip=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].PrivateIpAddress --output text)
done

logger -s -t runMatching "deploy the script to the server and run it"

scp -i $SERVERSSHKEY $execMatchingsh ec2-user@$privip:/tmp
while [ $? -ne 0 ] ; do
    # in case the server isn't responding to ssh sessions yet
    sleep 10
    echo "server not responding yet, retrying"
    scp -i $SERVERSSHKEY $execMatchingsh ec2-user@$privip:/tmp
done 
ssh -i $SERVERSSHKEY ec2-user@$privip $execMatchingsh

logger -s -t runMatching "monitoring and waiting for completion"
source $SERVERAWSKEYS
targdir=$MATCHDIR/distrib
python -c "from traj.distributeCandidates import monitorProgress as mp; mp('${rundate}','${targdir}'); "

logger -s -t runDistrib "merging in the new json files"
mkdir -p $DATADIR/distrib
cd $DATADIR/distrib
cp -f $targdir/*.json $DATADIR/distrib
cp -f $DATADIR/distrib/processed_trajectories.json $DATADIR/distrib/prev_processed_trajectories.json

python -m traj.consolidateDistTraj $DATADIR/distrib $DATADIR/distrib/processed_trajectories.json

cp $DATADIR/distrib/processed_trajectories.json $targdir
gzip < $DATADIR/distrib/processed_trajectories.json > $DATADIR/distrib/processed_trajectories.json.${rundate}.gz

logger -s -t runDistrib "compressing the processed data"
if [ ! -d $targdir/done ] ; then mkdir $targdir/done ; fi
mv $targdir/${rundate}.pickle $DATADIR/distrib
tar czvf ${rundate}.tgz ${rundate}*.json ${rundate}.pickle
cp ${rundate}.tgz $targdir/done
rm -f $targdir/${rundate}*.json ${rundate}*.json ${rundate}.pickle
logger -s -t runDistrib "done"


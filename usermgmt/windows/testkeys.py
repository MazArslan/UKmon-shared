# Copyright (C) 2018-2023 Mark McIntyre
# test that the keys provide read and write access

import boto3
import os
import glob



def readKeyFile(filename):
    if not os.path.isfile(filename):
        print('credentials file missing, cannot continue')
        exit(1)
    with open(filename, 'r') as fin:
        lis = fin.readlines()
    vals = {}
    for li in lis:
        if li[0]=='#':
            continue
        if '=' in li:
            valstr = li.split(' ')[1]
            data = valstr.split('=')
            val = data[1].strip()
            if val[0]=='"':
                val = val[1:len(val)-1]
            vals[data[0]] = val
    if 'S3FOLDER' not in vals and 'CAMLOC' in vals:
        vals['S3FOLDER'] = f'archive/{vals["CAMLOC"]}'
    if 'S3FOLDER' in vals and vals['S3FOLDER'][-1] == '/':
        vals['S3FOLDER'] = vals['S3FOLDER'][:-1]
    if 'ARCHBUCKET' not in vals:
        vals['ARCHBUCKET'] = 'ukmon-shared'
    if 'LIVEBUCKET' not in vals:
        vals['LIVEBUCKET'] = 'ukmon-live'
    if 'WEBBUCKET' not in vals:
        vals['WEBBUCKET'] = 'ukmeteornetworkarchive'
    if 'ARCHREGION' not in vals:
        vals['ARCHREGION'] = 'eu-west-2'
    if 'LIVEREGION' not in vals:
        vals['LIVEREGION'] = 'eu-west-1'
    if 'MATCHDIR' not in vals:
        vals['MATCHDIR'] = 'matches/RMSCorrelate'
    #print(vals)
    return vals


def uploadTest(keyfile):
    myloc = os.path.split(os.path.abspath(__file__))[0]
    myloc = 'f:/videos/meteorcam/usermgmt'
    filename = os.path.join(myloc, 'keys', keyfile)
    keys = readKeyFile(filename)
    target = keys['ARCHBUCKET']
    archreg = keys['ARCHREGION']
    livereg = keys['ARCHREGION']
    awskey = keys['AWS_ACCESS_KEY_ID']
    awssec = keys['AWS_SECRET_ACCESS_KEY']

    with open('/tmp/test.txt', 'w') as f:
        f.write('test')
    try:
        conn = boto3.Session(aws_access_key_id=awskey, aws_secret_access_key=awssec, region_name=archreg) 
        s3 = conn.resource('s3')
        target='ukmon-shared'
        s3.meta.client.upload_file('/tmp/test.txt', target, 'archive/test.txt')
        key = {'Objects': []}
        key['Objects'] = [{'Key': 'archive/test.txt'}]
        s3.meta.client.delete_objects(Bucket=target, Delete=key)
        print(f'{keyfile} archive test successful')
    except Exception:
        print(f'{keyfile} archive test FAILED')

    try:
        conn = boto3.Session(aws_access_key_id=awskey, aws_secret_access_key=awssec, region_name=livereg) 
        s3 = conn.resource('s3')
        target = 'ukmon-live'
        s3.meta.client.upload_file('/tmp/test.txt', target, 'test.txt')
        key = {'Objects': []}
        key['Objects'] = [{'Key': 'test.txt'}]
        s3.meta.client.delete_objects(Bucket=target, Delete=key)
        print(f'{keyfile} live test successful')
    except Exception:
        print(f'{keyfile} live test FAILED')

    os.remove('/tmp/test.txt')


if __name__ == '__main__':
    keys = glob.glob1('f:/videos/meteorcam/usermgmt/keys','*.key')
    for k in keys:
        uploadTest(k)

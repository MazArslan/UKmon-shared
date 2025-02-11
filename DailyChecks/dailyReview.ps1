# simple script to copy then display the most recent CMN/RMS meteor captures
# if RMS is installed it will also run some postprocessing to generate
# shower maps, JPGs and a UFO-Orbit-compatible detection file
# Copyright (C) 2018-2023 Mark McIntyre

set-location $PSScriptRoot
# load the helper functions
. .\helperfunctions.ps1
# read the inifile
if ($args.count -eq 0) {
    write-output "ini file missing, can't continue"
    exit 1
}
$inifname = $args[0]

$ini=get-inicontent $inifname
$hostname=$ini['camera']['hostname']
$maxage=$ini['camera']['maxage']
$localfolder=$ini['camera']['localfolder']
$binviewer_exe_loc=$ini['python']['binviewer_exe_loc']
$binviewer_pyt_loc=$ini['python']['binviewer_pyt_loc']
$binviewer_env=$ini['python']['binviewer_env']
$USE_EXE=$ini['python']['USE_EXE']
$RMS_INSTALLED=$ini['rms']['rms_installed']
$rms_loc=$ini['rms']['rms_loc']
$rms_env=$ini['rms']['rms_env']

# copy the latest data from the Pi
$srcpath='\\'+$hostname+'\RMS_share\ArchivedFiles'
$destpath=$localfolder+'\ArchivedFiles'
if ((test-path $destpath) -eq 0) { mkdir $destpath}
$age=[int]$maxage
robocopy $srcpath $destpath /dcopy:DAT /tee /v /s /r:3 /maxage:$age /xf *.bz2

# find the latest set of data on the local drive
$path=(get-childitem $destpath -directory | sort-object creationtime | select-object -last 1).name
$myf = $destpath + '\'+$path

# Use the Python version of binviewer, or the compiled binary?
if ($USE_EXE -eq 1){
    set-location $binviewer_exe_loc
    & .\CMN_binviewer.exe $myf -c | out-null
}
else {
    conda activate $binviewer_env
    set-location $binviewer_pyt_loc
    python CMN_BinViewer.py $myf -c
}
set-location $PSScriptRoot
.\uploadToCmnRejected.ps1 $myf

# switch RMS environment to do some post processing
if ($RMS_INSTALLED -eq 1){
    # reprocess the ConfirmedFiles folder to generate JPGs, shower maps, etc
    conda activate $RMS_ENV
    set-location $RMS_LOC
    $destpath=$localfolder+'\ArchivedFiles'
    $mindt = (get-date).AddDays(-$age)
    $dlist = (Get-ChildItem  -directory $destpath | Where-Object { $_.creationtime -gt $mindt }).name
    foreach ($path in $dlist) {
        $myf = $destpath + '\'+$path
        $ftpfil=$myf+'\FTPdetectinfo_'+$path+'.txt'
        #$platepar=$myf+ '\platepar_cmn2010.cal'

        $ufo=$myf+'\*radiants.txt'
        $isdone=(get-childitem $ufo).Name
        $ftpexists=test-path $ftpfil
        if ($isdone.count -eq 0 -and $ftpexists -ne 0){
            # generate the UFO-compatible CSV, shower association map 
            # convert fits to jpeg and create a stack
            # python -m Utils.RMS2UFO $ftpfil $platepar
            python -m Utils.ShowerAssociation $ftpfil -x -p gist_ncar
            # python -m Utils.BatchFFtoImage $myf jpg
            #stack them if more than one to stack
            # $fits = $myf  + '\FF*.fits'
            # $nfits=(get-childitem $fits).count
            # if ($nfits -gt 1)
            # {
            #    python -m Utils.StackFFs $myf jpg -s -b -x   
            # }
            # mp4 generation is not yet in the main RMS codebase
            # $mp4gen=$rms_loc+'/Utils/GenerateMP4s.py'
            # if (test-path $mp4gen ){
            #    python -m Utils.GenerateMP4s $myf
            # }
        }
        else{
            write-output skipping' '$myf
        }
    }    
    $destpath=$localfolder+'\ConfirmedFiles'
    $dlist = (Get-ChildItem  -directory $destpath | Where-Object { $_.creationtime -gt $mindt }).name
    foreach ($path in $dlist) {
        $myf = $destpath + '\'+$path
        $ftpfil=$myf+'\FTPdetectinfo_'+$path+'.txt'
        # $platepar=$myf+ '\platepar_cmn2010.cal'

        $ufo=$myf+'\*radiants.txt'
        $isdone=(get-childitem $ufo).Name
        $ftpexists=test-path $ftpfil
        if ($ftpexists -ne 0){
            # generate the UFO-compatible CSV, shower association map 
            # convert fits to jpeg and create a stack
            # python -m Utils.RMS2UFO $ftpfil $platepar
            python -m Utils.ShowerAssociation $ftpfil -x -p gist_ncar
            # python -m Utils.BatchFFtoImage $myf jpg
            #stack them if more than one to stack
            # $fits = $myf  + '\FF*.fits'
            # $nfits=(get-childitem $fits).count
            # if ($nfits -gt 1)
            # {
            #    python -m Utils.StackFFs $myf jpg -s -b -x   
            # }
            # mp4 generation is not yet in the main RMS codebase
            # $mp4gen=$rms_loc+'\Utils\GenerateMP4s.py'
            # if (test-path $mp4gen ){
            #    python -m Utils.GenerateMP4s $myf
            # }
            $allplates = $localfolder + '\ArchivedFiles\' + $path + '\platepars_all_recalibrated.json'
            copy-item $allplates $destpath
        }
        else{
            write-output skipping' '$myf
        }
    }    
}
set-location $PSScriptRoot
# .\reorgByYMD.ps1 $args[0]
# .\UploadToUkMon.ps1 $args[0]


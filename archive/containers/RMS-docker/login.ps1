# powershell script to login to docker container
# Copyright (C) Mark McIntyre

if ($args.count -lt 1) {
    write-output "usage: .\login.ps1 path\to\rmsdata"
    exit 1
}
$configloc=$args[0]

$contid=(get-content ${configloc}/containerid.txt)
docker exec -it $contid bash
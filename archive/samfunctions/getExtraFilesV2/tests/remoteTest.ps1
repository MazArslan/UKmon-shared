# test 
aws lambda invoke --profile ukmonshared --function-name getExtraOrbitFilesV2 --log-type Tail --cli-binary-format raw-in-base64-out --payload file://tests/testEvent.json  --region eu-west-2 ./ftpdetect.log

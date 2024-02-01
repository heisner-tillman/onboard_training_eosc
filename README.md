This is a script to onboard galaxy to onboard GTN training to the EOSC Portal - https://github.com/galaxyproject/training-material/issues/4647
# It does the following:
1: Create/restructure folders in the current directory to store resources

2: Fetch all the training materials from the API of GTN - https://training.galaxyproject.org/api/

3: Check if:
- there are any changes or new additions to the resources that where generated the last time the script was run
- check if there where any failures the last time resources where validated against or uploaded to the EOSC Provider API - https://providers.eosc-portal.eu/openapi

4: Proccess any resources that where identified in step 3 to adhere to the format the EOSC Provider API requires, when creating or updating training resources - https://wiki.eoscfuture.eu/display/PUBLIC/F.+EOSC+Training+Resource+Profile

5: Validate the processed training resources against the EOSC Provider API \
POST: `https://api.eosc-portal.eu/trainingResource/validate`

6: Proccess the validated resources to prepare them for uploading or mark them as failed

7: TODO - Update or upload the resources to the EOSC Portal via the Provider API \
POST\PUT: `https://api.eosc-portal.eu/trainingResource`

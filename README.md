# FaaSpot create client


## Purpose

Python client to create FaaS app from a given repo


## Prerequisite

- Ensure that there is a [default] profile for boto3 to find: nano ~/.aws/credentials

- Fill in required configuration in the faascli/commnads/config.py file


## Sample Usage

After adding to the GitHub repo, at given branch, the `./faaspot/faaspot.yml` config file, run:

```
faascli apps create -r GITHUB-REPO-URL -b BRANCH-NAME -v
```

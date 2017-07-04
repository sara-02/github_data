# github_data
A PoC to collect the requirement.txt and package.json from Github.

Note: We cannot the rawfiles directly as they are blacklisted in the robot.txt of Github.
So we have use go the hard way of scrapping the data.

## How to set the environment

```
virtualenv --python /usr/bin/python2.7 env
source env/bin/activate
pip install -r requirements.txt
cp config.py.template config.py
#make necessary changes in config.py or add a .env with the env variables
```

cuckoo
======

TW stock notifier

# Prepare for the environment
```
pip install -r requirements.txt
```

# Run daily job
Parse the daily stock price
```
./run
```

# Run finance report job
Parse the finance report
```
./run_weekly
```

# Transfer data
Data could store at local and firebase. For the first time use, you could transfer all data from firebase to local to get the historical result. 

```
[cchan@cchan cuckoo (master)]$ python transfer.py
Read from? (local/firebase): firebase
Save to? (local/firebase): local
firebase --> local
This will OVERWRITE data in "local". Are you sure? [y/n]
y
```
Storing in local json files is much faster but could not be shared. However, putting data in firebase could be single point of failure and data would be overwritten by each other. Please double check before overwriting data in firebase.

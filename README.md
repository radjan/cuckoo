cuckoo
======

TW stock notifier

# Prepare for the environment
```
sudo apt-get install libxml2-dev libxslt-dev python-dev
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
$ python transfer.py
Read from? (local/firebase): firebase
Save to? (local/firebase): local
firebase --> local
This will OVERWRITE data in "local". Are you sure? [y/n]
y
```
Storing in local json files is much faster but could not be shared. However, putting data in firebase could be single point of failure and data would be overwritten by each other. Please double check before overwriting data in firebase.

# Filtered result
```
$ python show_filter_result.py
fileter: kazuyo_katsuma
     5211 蒙恬, 4953 緯軟, 1537 廣隆, 5285 界霖
fileter: old_brother
     2107 厚生, 6216 居易, 5490 同亨, 2458 義隆, 4952 凌通
```

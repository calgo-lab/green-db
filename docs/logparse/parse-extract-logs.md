# parse unknown sustainability strings from extract logfile

1. Download kubernetes logfile e.g. via (adjust pod id, timestamps and filename):
```bash
kubectl -n greendb logs extract-workers-687c7557c4-rvqg8 --since-time=2023-02-22T18:00:00Z | awk '$0 < "2023-02-28T18:00:00Z"' > extract-logs-2023-02-28.txt
```

2. Run [`parse-unknown-labels.py`](./parse-unknown-labels.py) to create a JSON file with unknown labels in the same directory as 
   the logfile
```bash
python parse-unknown-labels.py -f "D:/GitHub/green-db/docs/logparse/extract-logs-2023-02-28.txt"
```

3. Add manually the unknown labels (and certificate mappings) in the corresponding extractors in 
   [`extract.extract.extractors.<shop-name>_<country>.py`](../extract/extract/extractors)
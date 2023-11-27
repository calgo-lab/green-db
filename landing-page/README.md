to rebuild the landing page run `python landing-page.py --no-cache` and push index.html

make sure to portforward the postgres pod if you pass --no-cache.
if you run `python landing-page.py` (without --no-cache), it will use old data and it will be alot faster. use it for quickly testing things.
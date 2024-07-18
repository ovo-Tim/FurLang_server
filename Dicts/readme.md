# Dictionary for dictionaries
This is a dictionary for dictionaries. Try to download MDict file [hare](https://mdict.org/) and use [mdict2sql](https://github.com/ovo-Tim/mdict2sql) to convert mdict file to sqlite(.db) file.

## Why don't we use MDict instead of Sqlite?
MDict has aleady been used widely, but it's low efficiency. To be specific, loading the whole MDict file to memory costs a lot of memary and time. I have tried to [use Cython to make it faster](https://github.com/ovo-Tim/faster-readmdict), but that still can't meet my needs.
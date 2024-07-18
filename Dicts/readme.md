# Dictionary for dictionaries
This is a dictionary for dictionaries. Try to download MDict file [hare](https://mdict.org/) and use [mdict2sql](https://github.com/ovo-Tim/mdict2sql) to convert mdict file to sqlite(.db) file.

If the program can't download the dict automatically, you can try to download [hare](https://gitcode.net/2401_82938926/cdn/-/blob/master/dict.db).

## Why don't we use MDict instead of Sqlite?
MDict has aleady been used widely, but it's low efficiency. To be specific, loading the whole MDict file to memory costs a lot of memary and time. I have tried to [use Cython to make it faster](https://github.com/ovo-Tim/faster-readmdict), but that still can't meet my needs.
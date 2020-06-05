import json
from multiprocessing.dummy import Pool as ThreadPool
from tar_tools import *
from glob import glob
from ttictoc import TicToc
#Start Time Counter
t = TicToc()
t.tic()

#===================LOAD CONFIG FILE=======================================
with open('converterCfg.json') as json_file:
    cfg = json.load(json_file)

path = cfg['path']
rounds = cfg['tar_rounds']
thread_pool_size = cfg['thread_pool_size']


dir_list = glob(path+'/*/')

#===================RUN TAR3===============================================
print("Starting Treatment Learning...")

list_approach = []
list_rounds = []
#prepara task list for multithreading
for run_dir in dir_list:
	for i in range(1,rounds+1):
		list_approach.append(run_dir)
		list_rounds.append(i)

pool = ThreadPool(thread_pool_size)

results = pool.starmap(tarThread, zip(list_approach, list_rounds))

print("TAR Total Time elapsed: %.2fs" %(t.toc()))

import subprocess
import pandas as pd 
import os
from shutil import copyfile

def export_tar_files(df, classes, threshold, dataset_name, path):
#Generate names, config and data files needed to run tar3

	new_path = path+'/'+dataset_name+'-'+str(threshold)
	try:
		os.mkdir(new_path)
	except FileExistsError:
		pass
	

	#Exclude unecessary columns for treatment learner
	df_tar = df.drop(['caseid', 'event', 'discovery'], axis=1)

	cols = list(df_tar.columns.values) #Make a list of all of the columns in the df
	cols.pop(cols.index('class')) #Remove class from list
	df_tar = df_tar[cols+['class']] #Add Class attribute to the end 

	rows = len(df_tar.index)
	#count non-zero values per column
	s = df_tar.astype(bool).sum(axis=0)
	#calculate the ratio of non-zero values
	s = s.apply(lambda x: x/rows)
	#leave only attribute names
	s.drop(['class'], inplace=True)
	#filter features below the threshold (to be excluded)
	s = s[s < threshold]
	df_tar = df_tar.drop(s.index, axis=1)
	# ========End Feature Selection====
	df_tar.to_csv(new_path+'/run.data', header=False, index=False, columns=df_tar.columns)
	#Write to cfg file group classes 
	cfg = ','.join(classes)+"\n\n"
	#Write to cfg file attributes and types (Assuming all continuous now)
	# for col in selectedColumnsToDataSet:
	for col in df_tar.columns:
		if col != 'class': #Class Attribute must not be considered in feature's list
			cfg= cfg+col+':continuous\n'
	
	f = open(new_path+'/run.names','w')
	f.write(cfg)
	f.close()

	copyfile('base.cfg', new_path+'/run.cfg')
	
def tarThread(run_dir, round):
#Run tar3 as external program
	approach = run_dir.split('\\')[-2]
	# print(approach+', round: '+str(round))
	fc = open(run_dir+'run-controller-'+str(round)+'.txt', 'w')
	subprocess.run(["tar3", "run"], stdout=fc, cwd=run_dir)
	fm = open(run_dir+'run-monitor-'+str(round)+'.txt', 'w')
	subprocess.run(["tar3", "-r", "run"], stdout=fm, cwd=run_dir)	
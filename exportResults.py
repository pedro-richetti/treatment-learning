import re
import os.path
from pathlib import Path
import pandas as pd 
import json

#===================LOAD CONFIG FILE=======================================
with open('converterCfg.json') as json_file:
    cfg = json.load(json_file)

#==============INPUT PARAMETERS===========================================
result_path = cfg['path']

#==============END INPUT PARAMETERS===========================================
print("Exporting Results...")

def listDir(path):
	filenames = []
	basepath = Path(path)
	for entry in basepath.iterdir():
		if entry.is_dir():
			# print("Dir "+entry.name)
			filenames.append(listDir(path+entry.name+"/"))
		if entry.is_file():
			# print("File "+entry.name)
			if re.match(".*run.*txt$", entry.name):
				filenames.append(path+entry.name)
	return filenames

def fileAsArray(filename):
	rows = []
	file = open(filename)

	for line in file:
		rows.append(line)

	return rows

filenames_list = listDir(result_path+'/')

filenames = []
for sublist in filenames_list:
	for item in sublist:
		filenames.append(item)

results=[]


for filename in filenames:

	rows = fileAsArray(filename)
	
	file = open(filename)

	for line in file:

		if re.match("^\s1\sworth.*", line):
			res1 = file.name.split("/")
			
			approach = res1[-2]			
			res2 = res1[-1].replace(".txt","").split("-")
			
			view = res2[1]
			run =  res2[2]
			
			res3 =  line.split("\t")
			worth = res3[0].replace(" 1 worth=","")
			treatment = res3[1].replace(" \n","")

			# Get class distribution for the best treatment
			treament_idx = [i for i, item in enumerate(rows) if item.startswith(' Treatment:[')]
			treatment_args = treatment.split(" ")
			treatment_args.sort()
			treatment_args_count = len(treatment_args)
			start_line = treament_idx[1] + treatment_args_count+1
			
			class_dist = []
			class_line = "  " #initialize to enter in the first loop
			i = 0
			while i >= 0:
				class_line = rows[start_line+i]
				if len(class_line) > 1: #stops on the subsequent blank line
					res4 = class_line.split(":")
					class_name = res4[0].strip()
					class_values = re.search(r'\[.*\]', res4[1]).group(0).replace("[","").replace("]","").split("-")
					class_abs = class_values[0].strip()
					class_pct = class_values[1].strip()
					class_dist.append([class_name,class_abs, class_pct])
					# print(class_line)
					i = i+1
				else:
					i = -1

			#sort results by class name
			class_dist.sort(key=lambda x: x[0])

			column_names = ['approach','view','run','treatment','worth']
			results_line = [approach,view,run,str(" ").join(treatment_args),worth]
			for item in class_dist:
				column_names.append(item[0]+"_abs")
				column_names.append(item[0]+"_pct")
				results_line.append(item[1])
				results_line.append(item[2])

			# print(class_dist)
			# print(str(treament_idx[1])+" "+ str(treatment_args_count))
			# print(results_line)

			results.append(results_line)



df=pd.DataFrame(results,columns=column_names)

# print(df)

df.to_csv(result_path+'/results.csv',index=False)
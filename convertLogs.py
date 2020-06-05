from ttictoc import TicToc
#Start Time Counter
t_main = TicToc()
t_main.tic()

t_discovery = TicToc()
t = TicToc()

import pandas as pd 
import numpy as np
import string
import json
from discovery_tools import *
from tar_tools import *


#===================LOAD CONFIG FILE=======================================
with open('converterCfg.json') as json_file:
    cfg = json.load(json_file)

#==============INPUT PARAMETERS===========================================

#Set discovery strategies
boa_discovery = cfg['boa_discovery']
bigram_discovery = cfg['bigram_discovery']
trigram_discovery = cfg['trigram_discovery']
maximal_repeat_sequence_discovery = cfg['maximal_repeat_sequence_discovery']
maximal_repeat_alphabet_discovery = cfg['maximal_repeat_alphabet_discovery']
declare_discovery = cfg['declare_discovery']

verbose = cfg['verbose']
path = cfg['path']
event_log_filename = cfg['event_log_filename']
instance_attributes_filename = cfg['instance_attributes_filename']

#It is mandatory for Treatment Learning to define the order of class values
#Starting from the worst value and ending with the best value
# classes = ['long', 'regular', 'short', 'very short']
classes = cfg['classes']

user_role_with_event = cfg['user_role_with_event']
#==============LOADING DATA===============================================

df2, event_list_names = datasetFromEventLog(path, event_log_filename, user_role_with_event)

df2 = addInstanceAttributeToDf(df2, path, instance_attributes_filename)

#=================== DISCOVER PATTERNS AND EXPORT TO TAR3 ================
print("Starting Data Discovery...")

if boa_discovery == True:
	t_discovery.tic()
	print("Starting Bag of Activities Discovery...")
	dataset_name = 'boa'
	df_boa = df2.copy()	
	df_boa = discover_bag_of_activities(df_boa, event_list_names, t, verbose)
	df_boa = remove_rows_all_equal(df_boa)
	export_tar_files(df_boa, classes, 0.00, dataset_name, path)	
	df_boa.to_csv(path+'/'+dataset_name+'.dataframe.csv')
	del df_boa
	print("Time elapsed: %.2fs" %(t_discovery.toc()))

if bigram_discovery == True:
	t_discovery.tic()
	print("Starting Bigram Discovery...")
	dataset_name = 'bigram'
	df_bigram = df2.copy()
	df_bigram = discover_bigram(df_bigram, event_list_names, t, verbose)
	df_bigram = remove_rows_all_equal(df_bigram)
	export_tar_files(df_bigram, classes, 0.00, dataset_name, path)	
	df_bigram.to_csv(path+'/'+dataset_name+'.dataframe.csv')
	del df_bigram
	print("Time elapsed: %.2fs" %(t_discovery.toc()))

if trigram_discovery == True:
	t_discovery.tic()
	print("Starting Trigram Discovery...")
	dataset_name = 'trigram'
	df_trigram = df2.copy()
	df_trigram = discover_trigram(df_trigram, event_list_names, t, verbose)
	df_trigram = remove_rows_all_equal(df_trigram)
	export_tar_files(df_trigram, classes, 0.00, dataset_name, path)	
	df_trigram.to_csv(path+'/'+dataset_name+'.dataframe.csv')
	del df_trigram
	print("Time elapsed: %.2fs" %(t_discovery.toc()))

if maximal_repeat_sequence_discovery == True or maximal_repeat_alphabet_discovery == True:
	t_discovery.tic()
	print("Starting Suffix Tree generation...")
	maximal_repeats_sequence = generate_maximal_repeats_sequence(df2, t)
	print("Total Time elapsed: %.2fs" %(t_discovery.toc()))

if maximal_repeat_sequence_discovery == True:	
	t_discovery.tic()
	print("Starting Maximal Repeat Sequence Discovery...")
	dataset_name = 'mrs'
	df_mrs = df2.copy()
	df_mrs = discover_maximal_repeats_sequence(df_mrs, maximal_repeats_sequence, t, verbose)
	df_mrs = remove_rows_all_equal(df_mrs)
	export_tar_files(df_mrs, classes, 0.00, dataset_name, path)	
	df_mrs.to_csv(path+'/'+dataset_name+'.dataframe.csv')
	del df_mrs
	print("Time elapsed: %.2fs" %(t_discovery.toc()))

if maximal_repeat_alphabet_discovery == True:	
	t_discovery.tic()
	print("Starting Maximal Repeat Alphabet Discovery...")
	dataset_name = 'mra'
	df_mra = df2.copy()
	df_mra = discover_maximal_repeats_alphabet(df_mra, maximal_repeats_sequence, t, verbose)
	df_mra = remove_rows_all_equal(df_mra)
	export_tar_files(df_mra, classes, 0.00, dataset_name, path)	
	df_mra.to_csv(path+'/'+dataset_name+'.dataframe.csv')
	del df_mra
	print("Time elapsed: %.2fs" %(t_discovery.toc()))

if declare_discovery == True:
	t_discovery.tic()
	print("Starting Declare Discovery...")
	dataset_name = 'declare'
	negation_constraints = False
	df_declare = df2.copy()
	df_declare = discover_declare_existence_constraints(df_declare, event_list_names, t, verbose)
	df_declare = discover_declare_unordered_constraints(df_declare, event_list_names, negation_constraints, t, verbose)
	df_declare = discover_declare_ordered_constraints(df_declare, event_list_names, negation_constraints, t, verbose)
	df_declare = remove_rows_all_equal(df_declare)
	
	export_tar_files(df_declare, classes, 0.00, dataset_name, path)
	export_tar_files(df_declare, classes, 0.02, dataset_name, path)
	export_tar_files(df_declare, classes, 0.05, dataset_name, path)
	df_declare.to_csv(path+'/'+dataset_name+'.dataframe.csv')
	del df_declare
	print("Time elapsed: %.2fs" %(t_discovery.toc()))

#Stop Time counter
print("Total Time elapsed: %.2fs" %(t_main.toc()))
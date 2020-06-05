import pandas as pd 
import numpy as np
import string
import re
import itertools
from itertools import chain
from ttictoc import TicToc
from suffix_tree import Tree
from multiprocessing.dummy import Pool as ThreadPool

def getDescription(event_list,idx):
	return event_list[idx]

#N-gram approach
def unique(list1):       
    # insert the list to the set 
    list_set = set(list1) 
    # convert the set to the list 
    unique_list = (list(list_set))
    return unique_list

def find_ngrams(input_list, n):
    return list(zip(*[input_list[i:] for i in range(n)]))


def remove_rows_all_equal(df):
	#Remove columns with all 0 or 1 values
	df = df.loc[:, (df != 0).any(axis=0)]
	df = df.loc[:, (df != 1).any(axis=0)]
	return df

def datasetFromEventLog(path, filename, userRoleWithEvent):
	#df = raw data from event log
	#df2 = dataframe for preprocessing and discovery

	#Mandatory columns: caseid, role, event
	df = pd.read_csv(path+'/'+filename, sep=',')

	df['event'] = df['event'].str.capitalize()
	df['event'] = df['event'].replace(' ', '_', regex = True)

	# Remove uninteresting events without leaving gaps
	df = df.loc[(df['event'] != 'Expressive') & (df['event'] != 'Declarative')]

	#Event is defined as the concatenation of user role and the uttered speech act
	if userRoleWithEvent == True:
		df['event'] = df['role']+df['event']

	#Transpose event in rows to columns, grouped by case id
	groupby_columns = ['caseid'] 
	df2 = df.groupby(groupby_columns)['event'].apply(' '.join).reset_index()

	# get unique list of events
	event_list_names = df.event.unique()

	return df2, event_list_names

def addInstanceAttributeToDf(df, path, filename):
	#Add instance level attributes
	#csv format: caseid,variable
	#caseid must be the index of df_var dataframe
	#Class Variable for Treatment Learning must be named "class"
	#Any other variable will have its name preserved and will be treated as another instance attribute
	df_var = pd.read_csv(path+'/'+filename, sep=',')
	# df_var.drop(['id'], axis=1, inplace=True)
	df = df.merge(df_var, on=('caseid'))

	return df

def discover_pattern_occurrence(event_string, regex_pattern):	
	# print(regex_pattern+' --> '+event_string)
	x = re.findall(regex_pattern, event_string)
	return len(x)

def discover_declare_existence_constraints(df, event_list_names, tictoc, verbose):
	#Existence Constraints
	for event_arg in event_list_names:
		tictoc.tic()
		
		idx = 'a'
		not_idx = 'x' 

		df['discovery'] = df['event']

		##replace events that are not target
		event_list_not_target = event_list_names[event_list_names != event_arg]
		
		df['discovery'] = df['discovery'].replace(event_list_not_target, not_idx, regex = True)

		#replace events that are target
		df['discovery'] = df['discovery'].replace(event_arg, idx, regex = True)

		#remove filling spaces
		df['discovery'] = df['discovery'].replace(' ', '', regex = True)

		pattern_name = 'exactly'
		attribute_name = pattern_name+'('+event_arg+')'
		regex_pattern = idx		
		df[attribute_name] = df['discovery'].apply(discover_pattern_occurrence, args=[regex_pattern])
		
		pattern_name = 'init'
		attribute_name = pattern_name+'('+event_arg+')'
		regex_pattern = '^'+idx+'.*'
		df[attribute_name] = df['discovery'].apply(discover_pattern_occurrence, args=[regex_pattern])
		
		pattern_name = 'last'
		attribute_name = pattern_name+'('+event_arg+')'
		regex_pattern = '.*'+idx+'+$'
		df[attribute_name] = df['discovery'].apply(discover_pattern_occurrence, args=[regex_pattern])

		pattern_name = 'participation'
		attribute_name = pattern_name+'('+event_arg+')'
		regex_pattern = '(.)*('+idx+')+(.)*'
		df[attribute_name] = df['discovery'].apply(discover_pattern_occurrence, args=[regex_pattern])

		pattern_name = 'uniqueness'
		attribute_name = pattern_name+'('+event_arg+')'
		regex_pattern = '^[^'+idx+']*('+idx+'?[^'+idx+']*){1}$'
		df[attribute_name] = df['discovery'].apply(discover_pattern_occurrence, args=[regex_pattern])

		if verbose==True:
			print("Mining Existence Constraints for: "+event_arg+ ".\t Processing Time: %.2fs" %(tictoc.toc()))

	return df

# Relation Constraints

def discover_declare_unordered_constraints(df, event_list_names, negation_constraints, tictoc, verbose):
# Unordered Existence and Not-Coexistence
# Pair-wise Combination without repetition
	event_pairs = list(itertools.combinations(event_list_names, 2))

	for event_pair in event_pairs:
		
		tictoc.tic()

		event_a = event_pair[0]
		event_b = event_pair[1]

		event_arg = '('+event_a+';'+event_b+')' 
		
		idx_a = 'a'
		idx_b = 'b'
		not_idx = 'x' 

		df['discovery'] = df['event']

		#replace events that are not target
		event_list_not_target = event_list_names[(event_list_names != event_a) & (event_list_names != event_b)]
		df['discovery'] = df['discovery'].replace(event_list_not_target, not_idx, regex = True)

		#replace events that are event a
		df['discovery'] = df['discovery'].replace(event_a, idx_a, regex = True)

		#replace events that are event b
		df['discovery'] = df['discovery'].replace(event_b, idx_b, regex = True)

		#remove filling spaces
		df['discovery'] = df['discovery'].replace(' ', '', regex = True)


		pattern_name = 'co_existence'
		attribute_name = pattern_name+event_arg
		regex_pattern = '^(?=.*?'+idx_a+')(?=.*?'+idx_b+').*$'
		df[attribute_name] = df['discovery'].apply(discover_pattern_occurrence, args=[regex_pattern])
		
		if negation_constraints == True:
			pattern_name = 'not_co_existence'
			attribute_name = pattern_name+event_arg
			regex_pattern = '^((?=.*?'+idx_a+')(?!.*?'+idx_b+')|(?!.*?'+idx_a+')(?=.*?'+idx_b+')).*$'
			df[attribute_name] = df['discovery'].apply(discover_pattern_occurrence, args=[regex_pattern])

		if verbose==True:
			print("Mining Unordered Relation Constraints for: "+event_a+", "+event_b+ ".\t Processing Time: %.2fs" %(tictoc.toc()))
	
	return df

def discover_declare_ordered_constraints(df, event_list_names, negation_constraints, tictoc, verbose):
#Ordered Constraints
	for event_a in event_list_names:
		for event_b in event_list_names:
			if event_a != event_b:
				tictoc.tic()

				event_arg = '('+event_a+';'+event_b+')'

				idx_a = 'a'
				idx_b = 'b'
				not_idx = 'x' 

				df['discovery'] = df['event']

				#replace events that are not target
				event_list_not_target = event_list_names[(event_list_names != event_a) & (event_list_names != event_b)]

				df['discovery'] = df['discovery'].replace(event_list_not_target, not_idx, regex = True)

				#replace events that are event a
				df['discovery'] = df['discovery'].replace(event_a, idx_a, regex = True)

				#replace events that are event b
				df['discovery'] = df['discovery'].replace(event_b, idx_b, regex = True)

				#remove filling spaces
				df['discovery'] = df['discovery'].replace(' ', '', regex = True)

				pattern_name = 'responded_existence'
				attribute_name = pattern_name+event_arg
				df[attribute_name] = 0
				regex_pattern = '^(?=.*?'+idx_a+')[^'+idx_a+']*(('+idx_a+'.*'+idx_b+'.*)|('+idx_b+'.*'+idx_a+'.*))?$'
				df[attribute_name] = df['discovery'].apply(discover_pattern_occurrence, args=[regex_pattern])
				# print(attribute_name +' ok')

				pattern_name = 'response'
				attribute_name = pattern_name+event_arg
				df[attribute_name] = 0				
				regex_pattern = '^[^'+idx_a+']*('+idx_a+'.*'+idx_b+')[^'+idx_a+']*$'
				# regex_pattern = '^(?=.*?'+idx_a+')[^'+idx_a+']*('+idx_a+'.*'+idx_b+')*[^'+idx_a+']*$'
				df[attribute_name] = df['discovery'].apply(discover_pattern_occurrence, args=[regex_pattern])
				# print(attribute_name +' ok')

				pattern_name = 'alternate_response'
				attribute_name = pattern_name+event_arg
				df[attribute_name] = 0
				regex_pattern = '^(?=.*?'+idx_a+')[^'+idx_a+']*('+idx_a+'[^'+idx_a+']*'+idx_b+'[^'+idx_a+']*)*$'
				df[attribute_name] = df['discovery'].apply(discover_pattern_occurrence, args=[regex_pattern])
				# print(attribute_name +' ok')

				pattern_name = 'chain_response'
				attribute_name = pattern_name+event_arg
				df[attribute_name] = 0
				regex_pattern = '^(?=.*?'+idx_a+')[^'+idx_a+']*('+idx_a+idx_b+'[^'+idx_a+']*)*$'
				df[attribute_name] = df['discovery'].apply(discover_pattern_occurrence, args=[regex_pattern])
				# print(attribute_name +' ok')

				pattern_name = 'precedence'
				attribute_name = pattern_name+event_arg
				df[attribute_name] = 0
				regex_pattern = '^(?=.*?'+idx_b+')[^'+idx_b+']*('+idx_a+'.*'+idx_b+')*[^'+idx_b+']*$'
				df[attribute_name] = df['discovery'].apply(discover_pattern_occurrence, args=[regex_pattern])
				# print(attribute_name +' ok')

				pattern_name = 'alternate_precedence'
				attribute_name = pattern_name+event_arg
				df[attribute_name] = 0
				regex_pattern = '^(?=.*?'+idx_b+')[^'+idx_b+']*('+idx_a+'[^'+idx_b+']*'+idx_b+'[^'+idx_b+']*)*$'
				df[attribute_name] = df['discovery'].apply(discover_pattern_occurrence, args=[regex_pattern])
				# print(attribute_name +' ok')

				pattern_name = 'chain_precedence'
				attribute_name = pattern_name+event_arg
				df[attribute_name] = 0
				regex_pattern = '^(?=.*?'+idx_b+')[^'+idx_b+']*('+idx_a+idx_b+'[^'+idx_b+']*)*$'
				df[attribute_name] = df['discovery'].apply(discover_pattern_occurrence, args=[regex_pattern])
				# print(attribute_name +' ok')

				pattern_name = 'succession'
				attribute_name = pattern_name+event_arg
				df[attribute_name] = 0
				df.loc[(df['response'+event_arg] == 1) & (df['precedence'+event_arg] == 1), [attribute_name]] = 1
				# print(attribute_name +' ok')
				
				pattern_name = 'alternate_succession'
				attribute_name = pattern_name+event_arg
				df[attribute_name] = 0
				df.loc[(df['alternate_response'+event_arg] == 1) & (df['alternate_precedence'+event_arg] == 1), [attribute_name]] = 1
				# print(attribute_name +' ok')
				
				pattern_name = 'chain_succession'
				attribute_name = pattern_name+event_arg
				df[attribute_name] = 0
				df.loc[(df['chain_response'+event_arg] == 1) & (df['chain_precedence'+event_arg] == 1), [attribute_name]] = 1
				# print(attribute_name +' ok')
				
				if verbose==True:
					print("Mining Ordered Relation Constraints for: "+event_a+", "+event_b+ ".\t Processing Time: %.2fs" %(tictoc.toc()))
	return df

def discover_bag_of_activities(df, event_list_names, tictoc, verbose):
# Bag of Activities (BOA)
	for event_arg in event_list_names:
		tictoc.tic()
		
		idx = 'a'
		not_idx = 'x' 

		df['discovery'] = df['event']

		##replace events that are not target
		event_list_not_target = event_list_names[event_list_names != event_arg]
		df['discovery'] = df['discovery'].replace(event_list_not_target, not_idx, regex = True)

		#replace events that are target
		df['discovery'] = df['discovery'].replace(event_arg, idx, regex = True)

		#remove filling spaces
		df['discovery'] = df['discovery'].replace(' ', '', regex = True)

		pattern_name = 'boa'
		attribute_name = pattern_name+'('+event_arg+')'
		regex_pattern = idx
		df[attribute_name] = df['discovery'].apply(discover_pattern_occurrence, args=[regex_pattern])
	
		if verbose==True:
			print("Mining Bag of Activities for: "+event_arg+ ".\t Processing Time: %.2fs" %(tictoc.toc()))

	return df

def discover_bigram(df, event_list_names, tictoc, verbose):
	#bigram
	df['bigrams'] = df['event'].map(lambda x: find_ngrams(x.split(" "), 2))
	bigrams = df['bigrams'].tolist()
	bigrams = list(chain(*bigrams))
	bigrams_unique = unique(bigrams)
	# print(len(bigrams_u))

	for event_pair in bigrams_unique:
		tictoc.tic()

		event_a = event_pair[0]
		event_b = event_pair[1]

		event_arg = '('+event_a+';'+event_b+')' 
		
		idx_a = 'a'
		idx_b = 'b'
		not_idx = 'x' 

		df['discovery'] = df['event']

		#replace events that are not target
		event_list_not_target = event_list_names[(event_list_names != event_a) & (event_list_names != event_b)]
		df['discovery'] = df['discovery'].replace(event_list_not_target, not_idx, regex = True)
		#replace events that are event a
		df['discovery'] = df['discovery'].replace(event_a, idx_a, regex = True)
		#replace events that are event b
		df['discovery'] = df['discovery'].replace(event_b, idx_b, regex = True)
		#remove filling spaces
		df['discovery'] = df['discovery'].replace(' ', '', regex = True)


		pattern_name = 'bigram'
		attribute_name = pattern_name+event_arg
		regex_pattern = idx_a+idx_b
		df[attribute_name] = df['discovery'].apply(discover_pattern_occurrence, args=[regex_pattern])

		if verbose==True:
			print("Mining Bigrams for: "+event_arg+ ".\t Processing Time: %.2fs" %(tictoc.toc()))

	df = df.drop(['bigrams'], axis=1)

	return df	


def discover_trigram(df, event_list_names, tictoc, verbose):
	#trigram
	df['trigrams'] = df['event'].map(lambda x: find_ngrams(x.split(" "), 3))
	trigrams = df['trigrams'].tolist()
	trigrams = list(chain(*trigrams))
	# bigram_counts = Counter(bigrams)
	trigrams_unique = unique(trigrams)
	# print(len(bigrams_u))

	for event_triple in trigrams_unique:
		tictoc.tic()

		event_a = event_triple[0]
		event_b = event_triple[1]
		event_c = event_triple[2]

		event_arg = '('+event_a+';'+event_b+';'+event_c+')' 
		
		idx_a = 'a'
		idx_b = 'b'
		idx_c = 'c'
		not_idx = 'x' 

		df['discovery'] = df['event']

		#replace events that are not target
		event_list_not_target = event_list_names[(event_list_names != event_a) & (event_list_names != event_b) & (event_list_names != event_c)]
	
		df['discovery'] = df['discovery'].replace(event_list_not_target, not_idx, regex = True)
		#replace events that are event a
		df['discovery'] = df['discovery'].replace(event_a, idx_a, regex = True)
		#replace events that are event b
		df['discovery'] = df['discovery'].replace(event_b, idx_b, regex = True)
		#replace events that are event c
		df['discovery'] = df['discovery'].replace(event_c, idx_c, regex = True)
		#remove filling spaces
		df['discovery'] = df['discovery'].replace(' ', '', regex = True)


		pattern_name = 'trigram'
		attribute_name = pattern_name+event_arg
		regex_pattern = idx_a+idx_b+idx_c
		df[attribute_name] = df['discovery'].apply(discover_pattern_occurrence, args=[regex_pattern])

		if verbose==True:
			print("Mining Trigrams for: "+event_arg+ ".\t Processing Time: %.2fs" %(tictoc.toc()))

	df = df.drop(['trigrams'], axis=1)

	return df

def generate_maximal_repeats_sequence(df, tictoc):
	tictoc.tic()
	
	df_tree = df.event.value_counts().reset_index()

	#Count variants and then duplicate variants with count > 1
	#This way we can creat a tree based on variants instead of adding each trace
	#When count > 1 it is sufficient to have only two variants for maximal repeats to be discovered
	df_tree.columns=['event','count']
	to_duplicate = df_tree['count'] > 1
	df_to_duplicate = df_tree[to_duplicate]
	df_tree = df_tree.append([df_to_duplicate],ignore_index=True)
	
	dict_tree = {}

	for index, row in df_tree.iterrows():
		dict_tree[index] = row['event'].split(" ") 
	
	tree = Tree(dict_tree)
	
	maximal_repeats_sequence = []
	for C, path in sorted (tree.maximal_repeats ()):
		sfx = str(path)
		# Only repeats with two or more elements
		if len(sfx.split(' ')) > 0:	
			maximal_repeats_sequence.append(sfx)

	print("Suffix Tree generated.\t Processing Time: %.2fs" %(tictoc.toc()))	

	return maximal_repeats_sequence


def discover_maximal_repeats_sequence(df, maximal_repeats_sequence, tictoc, verbose):
	
	for event_arg in maximal_repeats_sequence:
		tictoc.tic()
		
		idx = '@'

		df['discovery'] = df['event']		
		df['discovery'] = df['discovery'].replace(event_arg, idx, regex = True)

		event_arg = '('+event_arg.replace(' ',';')+')'

		pattern_name = 'mrs'
		attribute_name = pattern_name+event_arg
		regex_pattern = idx
		df[attribute_name] = df['discovery'].apply(discover_pattern_occurrence, args=[regex_pattern])

		if verbose==True:
			print("Mining Maximal Repeat Sequences for: "+event_arg+ ".\t Processing Time: %.2fs" %(tictoc.toc()))

	return df

def discover_maximal_repeats_alphabet(df, maximal_repeats_sequence, tictoc, verbose):
	maximal_repeat_alphabet = []
	for mrs in maximal_repeats_sequence:
		mrs_list = mrs.split(" ")
		mrs_list.sort()
		mrs_sorted = ' '.join(mrs_list)
		maximal_repeat_alphabet.append(mrs_sorted)

	#Merge list sequences and alphabet in a single dataframe
	df_mra = pd.DataFrame(list(zip(maximal_repeat_alphabet,maximal_repeats_sequence)), columns=['alphabet','sequence'])

	# print(df_mra)

	#Get unique alphabet list set
	mra_unique = unique(maximal_repeat_alphabet)

	for mra in mra_unique:
		tictoc.tic()
		# print(mra)
		mra_item = df_mra[df_mra.alphabet.eq(mra)] 
		# print(mra_item['sequence'])
		
		df['discovery'] = df['event']	

		pattern_name = 'mra'
		attribute_name = pattern_name+'('+mra.replace(' ',';')+')'
		regex_pattern = '('+'|'.join(mra_item['sequence'])+')'
		df[attribute_name] = df['discovery'].apply(discover_pattern_occurrence, args=[regex_pattern])

		if verbose==True:
			print("Mining Maximal Repeat Alphabets for: "+mra+ ".\t Processing Time: %.2fs" %(tictoc.toc()))	

	return df
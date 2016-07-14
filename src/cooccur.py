import sys
import os
import collections
import string
import re
import pickle
import operator
import argparse
import time
import multiprocessing
from multiprocessing import Process, Pool, Queue
from collections import Counter
import glob

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class MySentences(object):
 
     def __init__(self, fname):
        self.fname = fname
 
     def __iter__(self):
            for line in open(self.fname):
		#print line.split()
                yield line.split()              
 
#Extract file words into a dictionary 
def extract_dict(filename) :

	d = collections.defaultdict(int)
	file_contents = open(filename, 'r')
	words = []
	for c in file_contents :
		c = c.strip()
		d[c] = 1
		#print c
	return d 

#Collect cooccurance counts for unigrams and bigrams and store them in a dictionary : {instance_word context_word} (key) -> cooccur count(value)
def process_file(filename) :

	sentences = MySentences(filename)
	print multiprocessing.current_process().name, 'reading', filename

	unigram_cooccur =  collections.defaultdict(int)
	bigram_cooccur =  collections.defaultdict(int)

	for num, sent_tokens in enumerate(sentences) :

		#print num
		for index, t in enumerate(sent_tokens) :
			
			if( not t.count("/")  == 1 ) :
				continue 

			first_word = t.split("/")[0]
			first_tag = t.split("/")[1]	
			
			unigram_present = 0
			bigram_present = 0

			if( index < len(sent_tokens)-1 and sent_tokens[index+1].count("/") == 1) :
				sec_word = sent_tokens[index+1].split("/")[0]            		
				bigram = first_word + "_" + sec_word
				if( args.bigrams and bigrams_dict[bigram] == 1 ) :
					bigram_present = 1

			#print first_word, " and ", first_tag		

			if( args.unigrams and unigrams_dict[first_word] == 1 and ( "jj" in first_tag or "nn" in first_tag )  ) :
				unigram_present = 1
				

			if( unigram_present or bigram_present ) :
	
				begin = index - window
                        	if( begin < 0 ) :
					begin = 0

				end = index + 1 + window

				if( end >= len(sent_tokens) ) :
					end = len(sent_tokens)-1				

				while( begin <= end ) :

					context_word = sent_tokens[begin].split("/")[0]

					if(  contexts_list[context_word] == 1 ) :
						if( bigram_present and not ( begin == index or begin == index+1 ) ) :
							bigram_cooccur[bigram + " " + context_word] += 1
							#print bigram + " " + context_word
						 
						if( unigram_present ) :
							unigram_cooccur[first_word + " " + context_word] += 1 
							#print first_word + " " + context_word
						
					begin += 1

				
	
	unigrams_queue.put(unigram_cooccur)
	bigrams_queue.put(bigram_cooccur)	

				

#Save the cooccurence counts in a file ( in dense matrix form )
#Input - word_dict ( {instance_word context_word} (key) -> cooccur count(value) ) , instance_type("bigrams" or "unigrams")
def save_matrix ( word_dict, instance_type ) :

	if( len(word_dict) == 0 ) :
		return

	current_dir = os.getcwd()
	outfile_location = current_dir + '/dict' 
	if not os.path.exists(outfile_location):
    		os.makedirs(outfile_location)
	
	outfile = open(outfile_location + "/"+ instance_type + ".txt", "wb") 
	for key, val in word_dict.items() :
		outfile.write(key+" " + str(val) + "\n")
	outfile.close()

#Reduce the dictionaries in a multiprocessing queue into a single dictionary of cooccurence counts
def reduce_dicts(q) :

	word_counts = Counter()
	while not q.empty(): 		
    		dict = q.get()
		if( len(dict) > 0 ) :
			word_counts += Counter(dict)
	
	return word_counts
		
 
#Reduce the dictionaries and save the final coocurence counts 
def process_dict(queue, instance_type) :

	word_counts = reduce_dicts(queue )
	save_matrix(word_counts, instance_type ) 


if __name__ == "__main__":	
	
	start_time = time.time()
	window = 5
	nproc = 8

	unigrams_queue = Queue()
	bigrams_queue = Queue()		
	
	parser = argparse.ArgumentParser()
	parser.add_argument("corpus", help="Corpus filepath")
	parser.add_argument("contexts", help="Context words file")

	parser.add_argument("--window", help="Context window size", type=int)
	parser.add_argument("--unigrams", help="Unigrams file")
	parser.add_argument("--bigrams", help="Bigrams file")
	parser.add_argument("--nproc", help="Number of processes ", type=int)
	
	args = parser.parse_args()

	filename = args.corpus
	context_file = args.contexts

	input_files = glob.glob(args.corpus+'/*')
	contexts_list = extract_dict(context_file)

	if args.nproc :
		nproc = args.nproc

	if args.unigrams :
		unigrams_dict = extract_dict(args.unigrams) # Create a list of unigrams		
		
	if args.bigrams :
		bigrams_dict = extract_dict(args.bigrams) # Create a list of bigrams		

	pool = Pool(processes=nproc) 
	pool.map(process_file, input_files)	

	if args.unigrams :
		process_dict(unigrams_queue, "unigrams_cooccur")

	if args.bigrams :
		process_dict(bigrams_queue, "bigrams_cooccur")	
	
	print "Execution time (in secs)", (time.time() - start_time)	
	
	
	

	

	
	

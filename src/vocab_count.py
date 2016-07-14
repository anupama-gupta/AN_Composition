''' 
Tool to extract word counts

Command line usage: 

python vocab_count.py /path/corpus_folder --nproc 8 --unigrams 60000 --bigrams 100000 --contexts 10000

 Where :
 
 /path/corpus_folder - Folder containing corpus file(s) 
--unigrams 60000 - top n(60000) most frequent unigrams ( nouns and adjectives )
--bigrams 100000 - top n(100000) most frequent bigrams ( adjective noun compounds )
--contexts 10000 - top n(10000) most frequent context words 

Download link ( ukwac corpus location )
/home/anupama/tensor/corpus/ukwac/chunks

'''

import sys
import os
import collections
import string
import operator
import argparse
import time
import glob
import multiprocessing
from multiprocessing import Process, Pool, Queue
from collections import Counter

#Process the input file (fname) line by line ( one sentence = one line)
#Returns the sentence tokens
class MySentences(object):
 
     def __init__(self, fname):
        self.fname = fname
 
     def __iter__(self):
            for line in open(self.fname):
		  yield line.split() 	

#Input - word_counts ( dictionary : word(key) -> frequency(value) ), instance_type ( "unigrams", "bigrams" or "contexts" )
#Saves the vocab words in the folder "dict" created in the current directory
def save_list ( word_counts, instance_type ) :

	current_dir = os.getcwd()
	outfile_location = current_dir + '/dict' 
	if not os.path.exists(outfile_location):
    		os.makedirs(outfile_location)
	
	outfile = open(outfile_location + "/"+ instance_type + "_vocab.txt", "wb") 
	for word, freq in word_counts.items()  :
		outfile.write(word+"\n")
	outfile.close()

#Input - word_counts ( dictionary : word(key) -> frequency(value) ), topn ( top n words to extract )
#Returns the dictionary of word counts ( with the top n most frequent words )
def truncate_words(word_counts, topn)  :

	if( topn <= 0 ) :
		print "Threshold should be greater than 0 !"
		return

	sorted_words = sorted(word_counts.items(), key=operator.itemgetter(1), reverse=True)
	
	# Only taking the top n  words 
	topn_counts = dict(sorted_words[0:topn])

	return topn_counts  
		
#Collects the frequency counts of words in the input file and creates a dictionary : word(key) -> frequency(value)
#Appends the created dictionary to the multiprocessing queue
def process_file( filename ) :
	
	sentences = MySentences(filename)
	print multiprocessing.current_process().name, 'reading', filename

	unigram_freq =  collections.defaultdict(int)
	bigram_freq =  collections.defaultdict(int)
	context_freq =  collections.defaultdict(int)

	
	for num, sent_tokens in enumerate(sentences) :

		#print "processing sentence no. ", num
		for index, t in enumerate(sent_tokens)  :
			
			if( not t.count("/")  ) :
				continue
			
			first_word = t.split("/")[0]
			first_tag = t.split("/")[1]			
		
			if(  args.unigrams ) :
				if( "nn" in first_tag or "jj" in first_tag  ) :
					unigram_freq[first_word] += 1

			
			if( args.bigrams and (index < len(sent_tokens) - 1) ) :
				if( index < len(sent_tokens) - 1 and sent_tokens[index+1].count("/") ) :
					sec_word = sent_tokens[index+1].split("/")[0]
					sec_tag = sent_tokens[index+1].split("/")[1] 
					if( "jj" in first_tag and "nn" in sec_tag  ) :
						bigram_freq[first_word+"_"+sec_word] += 1

			if( args.contexts ) :
				context_freq[first_word] += 1


	unigrams_queue.put(unigram_freq)
	bigrams_queue.put(bigram_freq)
	contexts_queue.put(context_freq)	
	
#Reduces the dictionaries in the multiprocessing queue (q) and returns the final word counts dictionary
def reduce_dicts(q) :

	word_counts = Counter()
	while not q.empty(): 		
    		dict = q.get()	
		#print dict
		word_counts += Counter(dict)
	
	return word_counts

#Given a multiprocessing queue of word count dictionaries the following 3 tasks are implemented:
#1. Reduces all the dictionaries to a single dictionary
#2. Truncates the words in the dictionary using topn (top n words to extract)
#3. Saves the truncated dictionary words 
def process_dict(queue, topn, instance_type) :

	word_counts = reduce_dicts(queue )
	topn_words = truncate_words(word_counts, topn)	  
	save_list(topn_words, instance_type ) #Save the topn words
	

def print_dict(d) :
	for k, v in d.items() :
		print k, " and ", v		

		
if __name__ == "__main__":

	start_time = time.time()
	nproc = 8

	parser = argparse.ArgumentParser()
	parser.add_argument("corpus", help="File path of corpus")
	parser.add_argument("--unigrams", help="Top n : nouns and adjs", type=int)
	parser.add_argument("--bigrams", help="Top n : bigrams/compounds ", type=int)
	parser.add_argument("--contexts", help="Top n ", type=int)
	parser.add_argument("--nproc", help="Number of processes ", type=int)	
	
	args = parser.parse_args()

	input_files = glob.glob(args.corpus+'/*')

	if args.unigrams :
		unigrams_queue = Queue()
	
	if args.bigrams :
		bigrams_queue = Queue()

	if args.contexts :
		contexts_queue = Queue()

	if args.nproc :
		nproc = args.nproc

	pool = Pool(processes=nproc) 
	pool.map(process_file, input_files)
	
	if args.unigrams :
		process_dict(unigrams_queue, args.unigrams, "unigrams")

	if args.bigrams :
		process_dict(bigrams_queue, args.bigrams, "bigrams")
	
	if args.contexts :
		process_dict(contexts_queue, args.contexts, "contexts")		
	
	print "Execution time (in secs)", (time.time() - start_time)

	
	

	

	

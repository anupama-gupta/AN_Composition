
from composes.semantic_space.space import Space
from composes.matrix.sparse_matrix import SparseMatrix
from composes.utils import io_utils
from composes.composition.lexical_function import LexicalFunction
from composes.similarity.cos import CosSimilarity

import os
import sys
import codecs
import argparse
import collections
import pickle

# Load the space 
def load_space ( space_filename ) :
	return io_utils.load( space_filename)

# Extract adjectives (which have >= 50 unique bigram/compound instances) from a given bigram space 
def extract_adj(bigram_space) :

	adj_list = []

	bigram_freq = collections.defaultdict(int)
	
	rows = bigram_space.id2row
	
	for bigrams in rows :
		#print bigrams
		adj = bigrams.split("_")[0]
		bigram_freq[adj] += 1

	for adj, freq in bigram_freq.items() :
		if( freq >= 50 ) :
			adj_list.append(adj)

	return adj_list
	
#Save the created space 
def save_space(space, space_type, folder_name) :

	current_dir = os.getcwd()
	outfile_location = current_dir + '/' + folder_name 
	if not os.path.exists(outfile_location):
    		os.makedirs(outfile_location)
	
	outfilename = outfile_location + "/"+ space_type + ".pkl" 
	io_utils.save(space, outfilename) 
	

# Learn ADJ matrices using an adjective list ('adj_list')
def learn_ADJ_matrices (  ) :

	bigram_space = load_space(args.function[2])

	train_data=[]
	
	adj_list = extract_adj(bigram_space)
	
        for bigram in bigram_space.id2row  :
	    	pair = bigram.split('_')
            	if( pair[0] in adj_list ) :
			
			train_data.append(("ADJ"+"_"+pair[0], pair[1], bigram)) 
			# eg ( "ADJ_good", boy, good_boy ) , where "ADJ_good" -> matrix to learn, boy -> unigram , good_boy -> bigram
			        	 
    
        my_comp=LexicalFunction()
        my_comp.train(train_data, unigram_space, bigram_space)
	#unigram_space -> for "boy" , bigram_space -> for "good_boy"

        save_space(my_comp, "ADJ_matrices", "matrices")


# Learn Tensor matrix using a list of adjectives : adj_list
def learn_TENSOR_matrix (  ) :

	bigram_space = load_space(args.function[2])
	my_comp_list = []
	id2row_list = []
	adj_list = extract_adj(bigram_space)

	for adj in adj_list :        
        	
           	train_data=[]		

        	for bigram in bigram_space.id2row :

	    		pair = bigram.split('_')
            		if( not pair[0] == adj ) :
				continue
	    		train_data.append(("ADJ"+"_"+adj, pair[1], bigram))
			# eg ( "ADJ_good", "boy", "good_boy"), where "ADJ_good" -> matrix to learn, boy -> unigram , good_boy -> bigram
				

		my_comp=LexicalFunction()  # 1)

		#Learn ADJ matrix for each adjective
        	my_comp.train(train_data, unigram_space, bigram_space)
        	my_comp_list.append(my_comp.function_space.cooccurrence_matrix)
        	id2row_list.append(my_comp.function_space.id2row)

        my_mat_id2row=id2row_list.pop()
	my_mat_space=Space(my_comp_list.pop(),my_mat_id2row,[])

	#Create a new space using the ADJ matrices created
	for i in range(len(id2row_list)):
    		my_mat_id2row.extend(id2row_list[i])
    		my_mat_space=Space(my_mat_space.cooccurrence_matrix.vstack(my_comp_list[i]),my_mat_id2row,[])
    		my_mat_space._element_shape = my_comp.function_space.element_shape

	#Use the ADJ matrices space to learn the tensor matrix
	train_data=[('tens_adj',adj,"ADJ"+"_"+adj) for adj in adj_list] 
        # eg ( "tens_adj", good, ADJ_good ) 
        #where "tens_adj" -> tensor matrix to learn, good -> unigram , ADJ_good -> adjective matrix learnt by 'my_comp' in 1)


	my_tens_adj=LexicalFunction()
	my_tens_adj.train(train_data, unigram_space, my_mat_space)
	# unigram_space -> for "good" , my_mat_space -> for "ADJ_good"

	save_space(my_tens_adj, "TENSOR_matrix", "matrices")



# Creates a new semantic space where : AN/Compound = ADJ * noun 
# The list of bigrams constituting the space vectors are obtained from "bigram_space"
def compose_space_ADJ (  ) :

	bigram_space = load_space(args.function[2])
	ADJ_matrices = load_space(args.function[3])
	
	predicted_bigrams = []

	for bigram in bigram_space.id2row :
		
		adj = bigram.split('_')[0]
		noun = bigram.split('_')[1]	
		predicted_bigrams.append(("ADJ_"+adj, noun, "predicted_"+bigram) )
		# eg : ( "ADJ_good", "boy", "predicted_good_boy")
		# ADJ_good -> adjective matrix , boy -> unigram, predicted_good_boy -> to compute ( using : ADJ_good * boy )

	# Predicted composition =>  ADJ * noun
	composed_space = ADJ_matrices.compose( predicted_bigrams, unigram_space )
	save_space(composed_space, "composed_space_ADJ" , "composed_space")
	#print len(composed_space.id2row)

# Create new semantic space where : AN/Compound = (TENSOR * adj) * noun
def compose_space_TENSOR (  ) :

	bigram_space = load_space(args.function[2])
	TENSOR_matrix = load_space(args.function[3])
	
	predicted_ADJs = []
	predicted_bigrams = []
	adj_list = extract_adj(bigram_space)

	for adj in adj_list :
		predicted_ADJs.append(("tens_adj", adj, "predicted_ADJ_"+adj) ) 
		# eg ( "tens_adj", "good", "predicted_ADJ_good") 
		#tens_adj -> Tensor matrix , good -> unigram, predicted_ADJ_good -> to compute ( using  tens_adj * good )

	# Obtain the ADJ matrices using => TENSOR * adj
	composed_space_1 = TENSOR_matrix.compose(predicted_ADJs, unigram_space )

	expanded_model = LexicalFunction(function_space=composed_space_1,
        intercept=TENSOR_matrix._has_intercept)
		
	for bigram in bigram_space.id2row :
		
		adj = bigram.split('_')[0]
		noun = bigram.split('_')[1]
	
		predicted_bigrams.append(("predicted_ADJ_"+adj, noun, "predicted_"+bigram) )
		# eg ( "predicted_ADJ_good", "boy" , "predict_good_boy" ) 
		#predicted_ADJ_good -> ADJ_good matrix computed above, boy -> unigram, predicted_good_boy -> to compute (predicted_ADJ_good * boy )
	

	# Predicted composition =  predicted_ADJ * noun  ( where predicted_ADJ = TENSOR * adj )
	composed_space_2 = expanded_model.compose(predicted_bigrams, unigram_space ) 

	save_space(composed_space_2, "composed_space_TENSOR" , "composed_space")	



# Given compound: "good_job", returns it's predicted vector ( using : GOOD * job )
def predict_using_ADJ ( compound, ADJ_matrices, unigram_space ) :
	
	adj = compound.split('_')[0]
	noun = compound.split('_')[1]

	return ADJ_matrices.compose( [("ADJ_"+adj, noun, compound)], unigram_space )
	# eg : ( "ADJ_good", "boy", "good_boy")
	# ADJ_good -> adjective matrix , boy -> unigram, good_boy -> to compute ( using : ADJ_good * boy )


# Given compound eg: "good_job" , returns it's predicted vector using the equation : (TENSOR * good) * job
def predict_using_TENSOR ( compound, TENSOR_matrix, unigram_space ) :
	
	adj = compound.split('_')[0]
	noun = compound.split('_')[1]
			
	composed_space_1 = TENSOR_matrix.compose([("tens_adj", adj, "predicted_ADJ_"+adj)], unigram_space )
	# eg ( "tens_adj", "good", "predicted_ADJ_good") 
	#tens_adj -> Tensor matrix , good -> unigram, predicted_ADJ_good -> to compute ( using  tens_adj * good )
	
	#print composed_space_1.id2row
	expanded_model = LexicalFunction(function_space=composed_space_1,
        intercept=TENSOR_matrix._has_intercept)

	
	composed_space_2 = expanded_model.compose([("predicted_ADJ_"+adj, noun, compound)], unigram_space )
	# eg ( "predicted_ADJ_good", "boy" , "good_boy" ) 
	#predicted_ADJ_good -> ADJ_good matrix computed above, boy -> unigram, good_boy -> to compute ( predicted_ADJ_good * boy )
		
	return composed_space_2

# Return the topn nearest neighbours for a given compound(eg:"good_job") 
# space_1 contains the given compound 
# space_2 contains it's neighbours
def find_nearest( compound, space_1, space_2, topn=20  ) :
	
	return space_1.get_neighbours(compound, topn, CosSimilarity(), space2 = space_2 )

# find nearest neighbours of a compound vector obtained/predicted using ADJ matrix
def neighbours_ADJ(  ) :
	
	compound = args.function[2]
	space_2 = load_space(args.function[3])
	ADJ_matrices = load_space(args.function[4])

	adj = compound.split("_")[0]
	if( "ADJ_"+adj  not in ADJ_matrices.id2row ) :
		print adj , " matrix not found ! "
		return
	composed_space = predict_using_ADJ ( compound, ADJ_matrices, unigram_space )
	predicted_neighbours =  find_nearest(compound, composed_space, space_2 )	
	print "\n\nPredicted neighbours :\n", predicted_neighbours

# find nearest neighbours of a compound vector obtained/predicted using TENSOR matrix
def neighbours_TENSOR(  ) :

	compound = args.function[2]
	space_2 = load_space(args.function[3])
	TENSOR_matrix = load_space(args.function[4])

	composed_space = predict_using_TENSOR ( compound, TENSOR_matrix, unigram_space )
	predicted_neighbours =  find_nearest(compound, composed_space, space_2 )	
	print "\n\nPredicted neighbours : \n", predicted_neighbours

# find nearest neighbours of a compound vector present in the bigram_space ( corpus derived vector )
def neighbours_bigrams(  ) :

	compound = args.function[1]
	space_2 = load_space(args.function[2])
	bigram_space = load_space(args.function[3])

	predicted_neighbours =  find_nearest(compound, bigram_space, space_2 )	
	print "\n\nPredicted neighbours : \n" , predicted_neighbours

	


if __name__ == "__main__": 

	
	parser = argparse.ArgumentParser()
	
	parser.add_argument("function", nargs = "*", help="Functions : 1) 'learn_ADJ' unigram_space bigram_space   \
							  	       2) 'learn_TENSOR' unigram_space bigram_space \
								       3) 'ADJ_space' unigram_space bigram_space ADJ_matrices \
								       4) 'TENSOR_space' unigram_space bigram_space TENSOR_matrix \
							               5) 'neighbours_ADJ' unigram_space compound space_2 ADJ_matrices \
							               6) 'neighbours_TENSOR' unigram_space compound space_2 TENSOR_matrix \
								       7) 'neighbours_bigrams'  compound space_2 bigram_space ")
	
	args = parser.parse_args()


	if args.function[0] == "learn_ADJ" :
		unigram_space = load_space(args.function[1])
		learn_ADJ_matrices( )
	
	if args.function[0] == "learn_TENSOR" :
		unigram_space = load_space(args.function[1])
		learn_TENSOR_matrix( )

	if args.function[0] == "ADJ_space" :
		unigram_space = load_space(args.function[1])
		compose_space_ADJ ( )

	if args.function[0] == "TENSOR_space" :
		unigram_space = load_space(args.function[1])
		compose_space_TENSOR ( )

	if args.function[0] == "neighbours_ADJ" :
		unigram_space = load_space(args.function[1])
		neighbours_ADJ( )

	if args.function[0] == "neighbours_TENSOR" : 
		unigram_space = load_space(args.function[1])
		neighbours_TENSOR(  )

	if args.function[0] == "neighbours_bigrams" : 
		neighbours_bigrams(  )

	



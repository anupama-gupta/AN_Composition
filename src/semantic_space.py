'''
Constructs unigram(main) and bigram(peripheral) semantic space from the coooccurence counts by applying the following operations :
PPMI -> Normalization -> SVD(300) {Dissect Toolkit is used}
'''


from composes.utils import io_utils
from composes.semantic_space.space import Space
from composes.transformation.scaling.ppmi_weighting import PpmiWeighting
from composes.transformation.scaling.row_normalization import RowNormalization
from composes.transformation.dim_reduction.svd import Svd
import argparse
from composes.semantic_space.peripheral_space import PeripheralSpace
import os

#Apply PPMI weighting to a given semantic space
def ppmi(space) :
	ppmi_space = space.apply(PpmiWeighting())
	#io_utils.save(my_space_ppmi, "")
	return ppmi_space

#Apply Normalization to a given semantic space
def norm(space) :
	norm_space = space.apply(RowNormalization())
	#io_utils.save(space_norm, "")
	return norm_space

#Apply SVD to a given semantic space
def svd(space, size=300) :
	svd_space = space.apply(Svd(300))
	#io_utils.save(svd_space, "")
	return svd_space

def save_space(space, space_type) :
	current_dir = os.getcwd()
	outfile_location = current_dir + '/space' 
	if not os.path.exists(outfile_location):
    		os.makedirs(outfile_location)
	
	outfilename = outfile_location + "/"+ instance_type + ".pkl" 
	io_utils.save(space, outfilename) 

#Create unigram space by applying PPMI->Norm->SVD
def build_unigram_space() :
	unigram_space = Space.build(data = args.function[3],
                       	       rows = args.function[2],
                       	       cols = args.function[1],
                       	       format = "sm")
	 
	ppmi_space = ppmi(unigram_space)
	ppmi_norm_space = norm(ppmi_space)
	ppmi_norm_svd_space = svd(ppmi_norm_space)
	
	save_space(ppmi_norm_svd_space, "unigrams_space") 
	return ppmi_norm_svd_space

#Create bigram space using the unigram space 
def build_bigram_space():
	bigrams_space = PeripheralSpace.build(unigrams_space,
                                     data=args.function[3],
                                     cols=args.function[1],
                                     format="sm")

	save_space(bigrams_space, "bigrams_space")

if __name__ == "__main__":
	
	parser = argparse.ArgumentParser()
	parser.add_argument("function", nargs=4, help="1) 'unigram_space' contexts_file unigram_rows_file unigrams_dense_matrix_file \
					               2) 'bigram_space' contexts_file unigram_space_file bigrams_dense_matrix_file" )
					               
	args = parser.parse_args()

	if args.function[0] == "unigram_space" :
		build_unigram_space( ) 
    		unigrams_space = build_unigram_space() 		
		
	if args.function[0] == "bigram_space" :
		unigrams_space = io_utils.load(args.function[2])    			
		build_bigram_space() 

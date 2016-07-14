#!/bin/bash

printf "\n\nPipeline Implementation\n\n"

corpus_path=$1

if [ ! -d "$corpus_path" ] 
then
	printf "Corpus location not found!"
	exit
fi


count_unigrams=10000
count_bigrams=10000
count_contexts=10000
context_window=5
processes=8

printf "Building vocab"
python vocab_count.py $corpus_path --unigrams $count_unigrams --bigrams $count_bigrams --contexts $count_contexts --nproc $processes

printf "Building cooccurence counts"
python cooccur.py $corpus_path ./dict/contexts_vocab.txt --unigrams ./dict/unigrams_vocab.txt --bigrams ./dict/bigrams_vocab.txt --nproc $processes

printf "Creating unigrams semantic space : Main space"
python semantic_space.py unigram_space ./dict/contexts_vocab.txt ./dict/unigrams_vocab.txt ./dict/unigrams_cooccur.txt

printf "Creating bigrams semantic space : Peripheral space" 
python semantic_space.py bigram_space ./dict/contexts_vocab.txt ./space/unigrams_space.pkl ./dict/bigrams_cooccur.txt

printf "Learn ADJ matrices" 
python lex_functions.py learn_ADJ ./space/unigrams_space.pkl ./space/bigrams_space.pkl

printf "Learn TENSOR matrix"
python lex_functions.py learn_TENSOR ./space/unigrams_space.pkl ./space/bigrams_space.pkl

printf "Compose new compound vectors space using ADJ matrices"
python lex_functions.py ADJ_space ./space/unigrams_space.pkl ./space/bigrams_space.pkl ./matrices/ADJ_matrices.pkl

printf "Compose new compound vectors space using TENSOR matrix"
python lex_functions.py TENSOR_space ./space/unigrams_space.pkl ./space/bigrams_space.pkl ./matrices/TENSOR_matrix.pkl 

printf "\nNearest neighbours of a compound (predicted using ADJ matrix )"
python lex_functions.py neighbours_ADJ ./space/unigrams_space.pkl old_town ./composed_space/composed_space_ADJ.pkl ./matrices/ADJ_matrices.pkl

printf "\nNearest neighbours of a compound (predicted using TENSOR matrix )"
python lex_functions.py neighbours_TENSOR ./space/unigrams_space.pkl old_town ./composed_space/composed_space_TENSOR.pkl ./matrices/TENSOR_matrix.pkl

printf "\nNearest neighbours of compound vectors (obtained from bigram_space)"
python lex_functions.py neighbours_bigrams old_town ./space/bigrams_space.pkl ./space/bigrams_space.pkl

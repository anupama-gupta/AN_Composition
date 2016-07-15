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

compound="small_town"

printf "\nBuilding vocab\n"
python ./src/vocab_count.py $corpus_path --unigrams $count_unigrams --bigrams $count_bigrams --contexts $count_contexts --nproc $processes

printf "\nBuilding cooccurence counts\n"
python ./src/cooccur.py $corpus_path ./dict/contexts_vocab.txt --unigrams ./dict/unigrams_vocab.txt --bigrams ./dict/bigrams_vocab.txt --nproc $processes

printf "\nCreating unigrams semantic space : Main space\n"
python ./src/semantic_space.py unigram_space ./dict/contexts_vocab.txt ./dict/unigrams_vocab.txt ./dict/unigrams_cooccur.txt

printf "\nCreating bigrams semantic space : Peripheral space\n" 
python ./src/semantic_space.py bigram_space ./dict/contexts_vocab.txt ./space/unigrams_space.pkl ./dict/bigrams_cooccur.txt

printf "\nLearn ADJ matrices\n" 
python ./src/lex_functions.py learn_ADJ ./space/unigrams_space.pkl ./space/bigrams_space.pkl

printf "\nLearn TENSOR matrix\n"
python ./src/lex_functions.py learn_TENSOR ./space/unigrams_space.pkl ./space/bigrams_space.pkl

printf "\nCompose new compound vectors space using ADJ matrices\n"
python ./src/lex_functions.py ADJ_space ./space/unigrams_space.pkl ./space/bigrams_space.pkl ./matrices/ADJ_matrices.pkl

printf "\nCompose new compound vectors space using TENSOR matrix\n"
python ./src/lex_functions.py TENSOR_space ./space/unigrams_space.pkl ./space/bigrams_space.pkl ./matrices/TENSOR_matrix.pkl 

printf "\nNearest neighbours of", $compound," (predicted using ADJ matrix )\n"
python ./src/lex_functions.py neighbours_ADJ ./space/unigrams_space.pkl $compound ./composed_space/composed_space_ADJ.pkl ./matrices/ADJ_matrices.pkl

printf "\nNearest neighbours of", $compound," (predicted using TENSOR matrix )\n"
python ./src/lex_functions.py neighbours_TENSOR ./space/unigrams_space.pkl $compound ./composed_space/composed_space_TENSOR.pkl ./matrices/TENSOR_matrix.pkl

printf "\nNearest neighbours of", $compound, " (obtained from bigram_space)\n"
python ./src/lex_functions.py neighbours_bigrams $compound ./space/bigrams_space.pkl ./space/bigrams_space.pkl

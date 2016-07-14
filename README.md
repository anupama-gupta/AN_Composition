# About
To train the lexical functions,the corpus can be prepared as a text file(s), with one sentence per line. The punctuations and numbers are removed and the words are preprocessed (lemmatized). The sentence tokens are pos-tagged (Stanford PosTagger(http://nlp.stanford.edu/software/tagger.shtml) can be used ) and separated by a single space. [Here] (https://github.com/anupama-gupta/AN_Composition/blob/master/sample_sentences.txt) are few sample sentences.

# Demo

The demo script implements the entire pipeline on a given [corpus] (https://github.com/anupama-gupta/AN_Composition/
corpus_links.txt)

Usage :
    
    $ git clone https://github.com/anupama-gupta/AN_Composition
    $ cd AN_Composition
    $ ./demo.sh /path/corpus



# Tools

After the corpus is created, the lexical functions can be learned by using the following 4 tools :

### 1) vocab_count
Constructs unigram(adjectives and nouns) or bigram(adjective noun compounds) or context(bag-of-words) counts from the corpus and optionally thresholds the resulting vocabulary based on the total vocabulary size. Vocabulary file(s) are generated as output.

#### Usage :

    $ python vocab_count.py /path/corpus --unigrams c1 --bigrams c2 --contexts c3

where :

c1 :  most frequent unigrams 

c2  : most frequent bigrams 

c3 : most frequent context words 

output files :

1. [/dict/unigrams_vocab.txt] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

2. [/dict/bigrams_vocab.txt] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

3. [/dict/contexts_vocab.txt] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)


### 2) cooccur
Constructs cooccurrence counts (unigram-context or bigram-context) from the corpus. The files containing the unigrams or bigrams are obtained by running 'vocab_count' in 1). The user may specify optional parameters such as, context window size, number of processes etc. This tool generates a sparse matrix file of cooccurence counts.

#### Usage :

    $ python cooccur.py /path/corpus file1 --unigrams file2 --bigrams file3 --workers 8

where :

file1 - [/dict/contexts_vocab.txt] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

file2 - [/dict/unigrams_vocab.txt] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

file3 - [/dict/bigrams_vocab.txt] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

output files :

1. [/dict/unigrams_cooccur.txt] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

2. [/dict/bigrams_cooccur.txt] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

### 3) semantic_space
Constructs a vector space from the cooccurence counts obtained from 'cooccur'. The vectors are weighted using positive point-wise mutual information (ppmi), normalized to unit length and then reduced to 300 dimensions using singular value decomposition(svd).

####a. To create unigrams semantic space: 

    $ python semantic_space.py unigram_space file1 file2 file3

where :

file1 - [/dict/contexts_vocab.txt] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

file2 - [/dict/unigrams_vocab.txt] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

file3 - [/dict/unigrams_cooccur.txt] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

output file :

[/space/unigrams_space.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

####b. To create bigrams semantic space:

    $ python semantic_space.py bigram_space file1 file2 file3

where :

file1 - [/dict/contexts_vocab.txt] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

file2 - [/space/unigrams_space.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

file3 - [/dict/bigrams_cooccur.txt] (https://github.com/anupama-gupta/AN_Composition/blob/Space/file_links.txt)

output file :

[/space/bigrams_space.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

### 4) lexical_functions

This tool performs the following 3 tasks :

#### 1. Learns lexical functions (adjective matrices or tensor Matrix)

##### a. To learn adjective matrices :

    $ python lex_functions.py learn_ADJ file1 file2
    
where :

file1 - [/space/unigrams_space.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

file2 - [/space/bigrams_space.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

output file :

[/matrices/ADJ_matrices.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

##### b. To learn tensor matrix :

    $ python lex_functions.py learn_TENSOR file1 file2
    
where :

file1 - [/space/unigrams_space.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

file2 - [/space/bigrams_space.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

output file :

[/matrices/TENSOR_matrix.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

#### 2. Creates a new semantic space (new composed vectors consructed using lexical functions)

##### a. To create new space using adjective matrices  :

    $ python lex_functions.py ADJ_space file1 file2 file3
    
where :

file1 - [/space/unigrams_space.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

file2 - [/space/bigrams_space.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

file3 - [/matrices/ADJ_matrices.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

output file :

[/composed_space/composed_space_ADJ.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

##### b. To create new space using tensor matrix  :

    $ python lex_functions.py TENSOR_space file1 file2 file3

where :

file1 - [/space/unigrams_space.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

file2 - [/space/bigrams_space.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

file3 - [/matrices/TENSOR_matrix.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

output file :

[/composed_space/composed_space_TENSOR.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

   
#### 3. Finds nearest neighbours (Lists n nearest neighbours of a compound in a given semantic space )

##### a. Find neighbours of a compound (predicted using adjective matrices) :

    $ python lex_functions.py neighbours_ADJ file1 compound file2 file3

where :

compound - eg : good_boy, old_tree, young_actor etc.

file1 - [/space/unigrams_space.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

file2 - a [semantic space file] (https://github.com/anupama-gupta/Composition/blob/Space/file_links.txt) ( in /space or in /composed_space ). This is the space where the neighbours will be searched for.

file3 - [/matrices/ADJ_matrices.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

output :

list of nearest neighbours and their cosine similarity 


##### b. Find neighbours of a compound (predicted using tensor matrix) :

    $ python lex_functions.py neighbours_TENSOR file1 compound file2 file3
    
where :

compound - eg : good_boy, old_tree, young_actor etc.

file1 - [/space/unigrams_space.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

file2 - a [semantic space file] (https://github.com/anupama-gupta/Composition/blob/Space/file_links.txt)( in /space or in /composed_space ). This is the space where the neighbours will be searched for.

file3 - [/matrices/TENSOR_matrix.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

output :

list of nearest neighbours and their cosine similarity

##### c. Find neighbours of a compound (present in the bigram space {/space/bigrams_space.pkl} )

    $ python lex_functions.py neighbours_bigrams compound file1 file2

where :
    
file1 - a [semantic space ] (https://github.com/anupama-gupta/Composition/file_links.txt) ( in /space or in /composed_space ). This is the space where the neighbours will be searched for.

file2 - [/space/bigrams_space.pkl] (https://github.com/anupama-gupta/AN_Composition/file_links.txt)

output :

list of nearest neighbours and their cosine similarity 







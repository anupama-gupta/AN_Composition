import sys
import random
from collections import defaultdict
import sklearn
import matplotlib.pyplot as plt
import numpy as np
from sklearn.manifold import TSNE
import rpy2.robjects as ro
import rpy2.robjects.packages as rp
rp.importr('pls')

def run_pls_R (x_vecs, y_vecs,ncomp=50):
	assert( len(x_vecs) == len(y_vecs))
	assert (len(x_vecs) > 0)
	d = len(x_vecs[0])
	xm = []
	ym = []
	for i, x in enumerate(x_vecs):
		xm += x
		ym += y_vecs[i]
	x = ro.r.t(ro.r.matrix(ro.FloatVector(xm), nrow = d))
	y = ro.r.t(ro.r.matrix(ro.FloatVector(ym), nrow = d))
	print "x,y created"
	l = ro.r(''' f <- function (x,y) {
	d <- data.frame( x1 = I(x), y1 = I(y))
	g1 <- plsr ( y ~ x, data = d, ncomp=''' + str(ncomp) + ''',validation = "LOO")
	t(g1['coefficients'][[1]][,,''' + str(ncomp) + '''])
	}''')
	r_f = ro.globalenv['f']
	print "running PLS"
	out = r_f(x,y)
	print "Done with PLS"
	#ans = dict(zip(out.names, list(out)))
	return out


def create_classification_database(rels, vecs,n):
	ans = {}
	for k in rels.keys():
		pos_dict = {}
		neg_dict = {}
		for i in range(0,n):
			pos_dict[random.choice(rels[k].keys())] = 1
		for i in range(0,n):
			k1 = random.choice(rels.keys())
			if k1 == k:
				continue
			neg_dict[random.choice(rels[k1].keys())] = 1
	
		out_data = []				
		for k2 in pos_dict.keys():
			if k2 in vecs:
				out_data.append((k2,vecs[k2],0))
	
		for k2 in neg_dict.keys():
			if k2 in vecs:
				out_data.append((k2,vecs[k2],1))

		random.shuffle(out_data)
		ans[k] = out_data
	return ans
	




def multX(m,x):
	d = len(x)
	xr = ro.r.matrix(ro.FloatVector(x), nrow = d)
	print ro.r.dim(m)
	print ro.r.dim(xr)
	return m.dot(xr)
	
	


def train_R(classification_data):
	writer = get_train_test(classification_data['writer'])
	actor = get_train_test(classification_data['actor'])
	clf_writer = get_SGD_fit(writer, "t1")
	clf_actor = get_SGD_fit(actor, "t1")
	writer_vecs = multiply_vectors(writer['X_train'], clf_writer.coef_[0]) 
        #return writer_vecs, actor['X_train']
	ml = min(len(writer_vecs), len(actor['X_train']) / 2)
	return run_pls_R(actor['X_train'][0:ml], writer_vecs[0:ml])	


def get_train_test(out_data,val=0.7):
	ind = int(val* len(out_data))
	ans = {}
	ans['labels_train'] = [x[0] for x in out_data[0:ind]]
	ans['labels_test'] = [x[0] for x in out_data[ind+1:]]
	ans['X_train'] = [x[1] for x in out_data[0:ind]]
	ans['Y_train'] = [x[2] for x in out_data[0:ind]]
 	ans['X_test'] = [x[1] for x in out_data[ind+1:]]
	ans['Y_test'] = [x[2] for x in out_data[ind+1:]]
	return ans

def print_vectors(labels, vecs, fn):
	with open(fn,"w") as fw:
	   for i, l in enumerate(labels):
	       fw.write(l + "\t" + "\t".join([str(x) for x in vecs[i]]) + "\n")
	

def multiply_vectors(vecs, coeffs):
	ans = []
	for v in vecs:
		new_v = [ x * coeffs[i] for i,x in enumerate(v)]
		ans.append(new_v)
	return ans	


def plot_vectors(vecs, original, predicted, fn):
	X = np.vstack(vecs)
	proj = TSNE(random_state = 20150101).fit_transform(X)
	f = plt.figure(figsize=(8, 8))
	ax = plt.subplot(aspect='equal')
	colors = []
	for i,o in enumerate(original):
		p = predicted[i]
		c = ""
		if o == 0 and p == 0:
			c = "darkred"
		elif o == 0 and p == 1:
		 	c = "red"
		elif o == 1 and p == 0:
			c = "green"
		elif o == 1 and p == 1:
			c = "darkgreen"

		colors.append(c)


	sc = ax.scatter(proj[:,0], proj[:,1], c = colors, s=40)
	plt.savefig(fn, dpi=120)


def get_SGD_fit(d,fn):
    #d = get_train_test(data)
    clf = sklearn.linear_model.SGDClassifier()
    clf.fit(d['X_train'], d['Y_train'])	
    trainacc = sklearn.metrics.accuracy_score(clf.predict(d['X_train']), d['Y_train'])
    testacc = sklearn.metrics.accuracy_score(clf.predict(d['X_test']), d['Y_test'])
    print "Training Accuracy:: " + str(trainacc) + "(" + str(len(d['Y_train'])) + ")  Test Accuracy:: " + str(testacc) + "(" + str(len(d['Y_test'])) + ")" 
    plot_vectors(multiply_vectors(d['X_train'], clf.coef_[0]), d['Y_train'],clf.predict(d['X_train']),fn)	
    plot_vectors(d['X_train'], d['Y_train'],clf.predict(d['X_train']),"before_" + fn) 
    return clf	


	


def try_SGD(classification_data):
    count = 0
    sumv = 0
    d = {}
    for k in classification_data.keys():
	dat = get_train_test(classification_data[k])
    	clf = sklearn.linear_model.SGDClassifier()
	print k 
	print dat['Y_train']
    	clf.fit(dat['X_train'], dat['Y_train'])
    	trainacc = sklearn.metrics.accuracy_score(clf.predict(dat['X_train']), dat['Y_train'])
    	acc = sklearn.metrics.accuracy_score(clf.predict(dat['X_test']), dat['Y_test'])
	#print k + " --> " + str(acc)  + " --> " + str(len(dat['Y_test']))
	d[k] = (acc, trainacc,len(dat['Y_test']))
	sumv += acc
	count += 1

    for k, v in sorted(d.items(), key = lambda x: -1 * x[1][0]):
    	print k + "-->" + str(v[0]) + " (" + str(v[2]) + ")   training accuracy->" + str(v[1])  
    print "Average Accuracy: " + str(sumv *1.0/ count) 



def load_relations(relations_file):
	ans = defaultdict(dict)
	with open(relations_file) as fp:
		for line in fp:
			tokens = line.strip().split("\t")
			ans[tokens[1]][tokens[0]] = 1
	return ans


def load_vectors(vectors_file):
	ans = defaultdict(list)
	with open(vectors_file) as fp:
		for line in fp:
			tokens = line.strip().split("\t")
			ans[tokens[0]] = [float(x) for x in tokens[1:]]
	return ans
	

if __name__ == "__main__":
	rels = load_relations(sys.argv[1])
	vecs = load_vectors(sys.argv[2])
        classification_data = create_classification_database(rels, vecs,100)			


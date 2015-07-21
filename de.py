from scipy.optimize import differential_evolution
import scipy
from Bulge import *
INDEX = 0
def objF(x):
	global INDEX
	modelname = 'Model-'+str(INDEX)
	INDEX += 1
	K,e0,n,rth,rz= x
	parts = [7.85e-9,210000.0,.3,K,e0,n,rth,rz]		
	paramFile = open('result.txt','a+')
	paramFile.write('%s %10.6E %10.6E %10.6E %10.6E %10.6E '%(str(INDEX),K,e0,n,rth,rz))
	paramFile.flush()
	material = {'part':parts}
	shapes = {'outDimater':72.5,'thick':3.65,'length':145}
	mesh={'tube':100}
	timelist = [.20,.21,.22,.24]
	amps = [.5547,.576,.5824,.5982]
	midpairs = [(.05,.0329),(.1,.2246),(.15,.4013),(.18,.4957)]
	args={'timelist':timelist,'amp':amps,'midpairs':midpairs}
	load=args
	inits={}
	BCs={}
	positions = {}
	material={'part':parts}
	meshSize = {'pressDie':shapes['thick']*3/0.6,'tube':shapes['thick']/0.6 * 2}
	t = TBFEA(modelname)
	t.setParameter(shapes,material,positions,inits,\
			len(timelist),BCs,load,meshSize,args)
	t.setModels()
	coords = t.getResults()
	npFEA = scipy.array(coords)
	npExp = scipy.array([37.00,37.55,38.53,40.58])
	npres = npFEA - npExp
	mse=scipy.sum(scipy.square(npres))
	paramFile.write('%10.6E\n'%(mse))
	paramFile.close()
	return mse
paramFile = open('result.txt','w')
paramFile.close()
#7.584489E+02 8.233530E-02 2.722855E-01 1.346841E+00 1.525195E+00 5.064105E+00
bs=scipy.array([[650,800],[0.01,0.1],[0.15,0.3],[0.5.,1.5],[0.5.,1.5]])
de = differential_evolution(func=objF, bounds=bs, args=(), \
	strategy='best1bin', maxiter=50, popsize=20,\
	tol=1, mutation=(0.5, 1), recombination=0.7,\
	seed=None, callback=None, disp=False, polish=True, init='latinhypercube')

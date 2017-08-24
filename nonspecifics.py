import numpy as np

'''
Functions whose functionality is not specific to working with demographic data
'''


# For dividing each row of a matrix by a corresponding number in a one-dimensional vector
def divideMatrixByVector(matrix,vector):
    assert matrix.shape[0] == vector.shape[0]
    return np.array([matrix[i,:]/vector[i] if vector[i]!=0 else -1*matrix[i,:] for i in range(matrix.shape[0])])

# Helper function to make NaN == NaN true
def compareAmongNANS(u,v):
    return np.logical_or(u==v,np.logical_and(np.isnan(u),np.isnan(v)))

# Given the name of a company, returns its index
def indexFromName(name):
    for cny in demoData:
        if cny['nomeDaEmpresa'][1] == name:
            return cny['nomeDaEmpresa'][0]

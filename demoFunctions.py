import numpy as np
import pandas as pd

def sumToTotal(matrix):
    index={}
    for gender in ['homens', 'mulheres']:
        totalGender = [gender in x.lower() and 'total' in x.lower() for x in list(matrix.columns)]
        index[gender] = np.nonzero(totalGender)[0][0]
    #index is the column with 'total GENDER' in it
    assert index['homens'] < index['mulheres']

    #eachGENDER holds the sum of discriminated columns of given gender
    #totalGENDER is the value of the 'total GENDER' column
    eachMales =  matrix.iloc[:,:index['homens']].values
    totalMales = matrix.iloc[:,index['homens']].values.reshape(-1)

    eachFemales =  matrix.iloc[:,index['homens']+1:index['mulheres']].values
    totalFemales =  matrix.iloc[:,index['mulheres']].values.reshape(-1)
    return (eachMales, totalMales), (eachFemales, totalFemales)


#Returns true if the sum of columns is equal to 'total' column
def compareGenderSum(matrix):
    (menEach,menTotal),(femaleEach,femaleTotal) = sumToTotal(matrix)
    return compareAmongNANS(menEach.sum(axis=1),menTotal), compareAmongNANS(femaleEach.sum(axis=1),femaleTotal)

# Helper function to make NaN == NaN true
def compareAmongNANS(u,v):
    return np.logical_or(u==v,np.logical_and(np.isnan(u),np.isnan(v)))

# Determine how many indexes have values diferent from NaN outside 'total' column
def isDiscriminated(matrix):
    (menEach,_),(femaleEach,_) = sumToTotal(matrix)
    return (menEach>=0).sum(), (femaleEach>=0).sum() #zeros as counted as discriminated values

# Merges all companies data from a given field
def getDemo(demoData, field, proportion = True):
    clusteredData = pd.DataFrame(columns=['specifics','company','variable','value'])
    for empresai in demoData:
        if proportion:
            aux = transformInProportion(empresai[field])
        else:
            aux = pd.DataFrame.copy(empresai[field])
        aux['specifics'] = aux.index
        aux['company'] = empresai['nomeDaEmpresa'][1]
        clusteredData= pd.concat((clusteredData,aux.melt(id_vars=['specifics','company'])),axis=0)

    return clusteredData[clusteredData['value'].isnull() == False]

def transformInProportion(matrix,dropTots = True):
    (eachMales, totalMales), (eachFemales, totalFemales) = sumToTotal(matrix)
    aux = pd.DataFrame.copy(matrix)
    # substitute discriminated values of dataframe to the proportions given by sumToTotal
    aux.iloc[:,:idxTotal(aux,'homens')] = divideMatrixByVector(eachMales,totalMales)
    aux.iloc[:,idxTotal(aux,'homens')+1: idxTotal(aux,'mulheres') ] = divideMatrixByVector(eachFemales,totalFemales)
    if dropTots:
        aux.drop(['Total de homens','Total de mulheres'], axis=1, inplace=True)
    return aux

def divideMatrixByVector(matrix,vector):
    assert matrix.shape[0] == vector.shape[0]
    return np.array([matrix[i,:]/vector[i] if vector[i]!=0 else 2*np.ones(matrix.shape[1]) for i in range(matrix.shape[0])])

def idxTotal(df, gender):
    return np.nonzero(df.columns=='Total de '+str(gender))[0][0]

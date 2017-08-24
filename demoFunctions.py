import numpy as np
import pandas as pd
from nonspecifics import compareAmongNANS, divideMatrixByVector
'''
Functions that are specific to dealing with demographic data from the questionnaire
'''

#calculate the sum of specifics for comparating with 'total' column
def sumToTotal(matrix):
    index = totalIndices(matrix)
    #eachGENDER holds the sum of discriminated columns of given gender
    #totalGENDER is the value of the 'total GENDER' column
    eachMales =  matrix.iloc[:,:index['homens']].values
    totalMales = matrix.iloc[:,index['homens']].values.reshape(-1)

    eachFemales =  matrix.iloc[:,index['homens']+1:index['mulheres']].values
    totalFemales =  matrix.iloc[:,index['mulheres']].values.reshape(-1)
    return (eachMales, totalMales), (eachFemales, totalFemales)

# When total is 0 but there are specifics > 0, sum specifics and put on total
def substituteMissingTotal(matrix):
    idx = totalIndices(matrix)
    (eachMales, totalMales), (eachFemales, totalFemales) = sumToTotal(matrix)
    totalMales[totalMales==0] = eachMales.sum(axis=1)[totalMales==0]
    matrix.iloc[:,idx['homens']] = totalMales

    totalFemales[totalFemales==0] = eachFemales.sum(axis=1)[totalFemales==0]
    matrix.iloc[:,idx['mulheres']] = totalFemales
    return matrix

#return a dict containing the index of the 'total' column for woman and men
def totalIndices(matrix):
    index={}
    for gender in ['homens', 'mulheres']:
        totalGender = [gender in x.lower() and 'total' in x.lower() for x in list(matrix.columns)]
        #index is the column with 'total GENDER' in it
        index[gender] = np.nonzero(totalGender)[0][0]
    assert index['homens'] < index['mulheres']
    return index

#Returns true if the sum of columns is equal to 'total' column
def compareGenderSum(matrix):
    (menEach,menTotal),(femaleEach,femaleTotal) = sumToTotal(matrix)
    return compareAmongNANS(menEach.sum(axis=1),menTotal), compareAmongNANS(femaleEach.sum(axis=1),femaleTotal)


# Determine how many indexes have values diferent from NaN outside 'total' column
def isDiscriminated(matrix):
    (menEach,_),(femaleEach,_) = sumToTotal(matrix)
    return (menEach>=0).sum(), (femaleEach>=0).sum() #zeros as counted as discriminated values

# Merges all companies data from a given field
def getDemo(demoData, field, proportion = True):
    clusteredData = pd.DataFrame(columns=['specifics','company','variable','value'])
    for empresai in demoData:
        if proportion and field not in ['salarioGeneroRaca']:
            aux = transformInProportion(empresai[field])
        else:
            aux = pd.DataFrame.copy(empresai[field])
        aux['specifics'] = aux.index
        aux['company'] = empresai['nomeDaEmpresa'][1]
        clusteredData= pd.concat((clusteredData,aux.melt(id_vars=['specifics','company'])),axis=0)

    return clusteredData[clusteredData['value'].isnull() == False]

# substitute discriminated values of dataframe to the proportions given by sumToTotal
def transformInProportion(matrix,dropTots = True):
    if len(matrix.columns) == 2:
        return matrix #for the cases in which there is no 'total' column

    aux = pd.DataFrame.copy(matrix)
    totalIdx = totalIndices(aux)
    (eachMales, totalMales), (eachFemales, totalFemales) = sumToTotal(matrix)

    aux.iloc[:,:totalIdx['homens']] = divideMatrixByVector(eachMales,totalMales)
    aux.iloc[:,totalIdx['homens']+1: totalIdx['mulheres'] ] = divideMatrixByVector(eachFemales,totalFemales)
    if dropTots:
        aux.drop(aux.columns[[totalIdx['homens'],totalIdx['mulheres']]], axis=1, inplace=True)
    return aux

# Flags as inconsistent any field that is filled with specifics that sum bigger than the total
def proportionConsistency(demoData,field):
    oneFieldAllCnys = getDemo(demoData,field)
    consistency = pd.DataFrame( index = oneFieldAllCnys['company'].unique(),
                               columns=['Proportions max','Consistent','Number of Categories','field'])


    for cnyi in oneFieldAllCnys['company'].unique():
        maxOfProportions = oneFieldAllCnys[ oneFieldAllCnys['company'] == cnyi ]['value'].max()
        consistency.loc[cnyi, 'Proportions max'] = maxOfProportions

        nCategories = oneFieldAllCnys[ oneFieldAllCnys['company'] == cnyi ]['specifics'].unique().shape[0]
        consistency.loc[cnyi, 'Number of Categories'] = nCategories
    consistency['Consistent'] = consistency['Proportions max'].apply(lambda x: x <= 1)
    consistency['field'] = field
    return consistency

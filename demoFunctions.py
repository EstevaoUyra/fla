import numpy as np
import pandas as pd
from nonspecifics import compareAmongNANS, divideMatrixByVector
'''
Functions that are specific to dealing with demographic data from the questionnaire
'''
 

def sumToTotal(matrix):
    '''Calculate the sum of specifics for comparating with 'total' column.
    (eachMales, totalMales), (eachFemales, totalFemales)
    eachGENDER holds the sum of discriminated columns of given gender
    totalGENDER is the value of the 'total GENDER' column
    '''
    index = totalIndices(matrix)
    #eachGENDER holds the sum of discriminated columns of given gender
    #totalGENDER is the value of the 'total GENDER' column
    eachMales =  matrix.iloc[:,:index['homens']].values
    totalMales = matrix.iloc[:,index['homens']].values.reshape(-1)

    eachFemales =  matrix.iloc[:,index['homens']+1:index['mulheres']].values
    totalFemales =  matrix.iloc[:,index['mulheres']].values.reshape(-1)
    return (eachMales, totalMales), (eachFemales, totalFemales)

def substituteMissingTotal(matrix):
    '''When total is 0 but there are specifics > 0, sum specifics and put on total '''
    idx = totalIndices(matrix)
    (eachMales, totalMales), (eachFemales, totalFemales) = sumToTotal(matrix)
    totalMales[totalMales==0] = eachMales.sum(axis=1)[totalMales==0]
    matrix.iloc[:,idx['homens']] = totalMales

    totalFemales[totalFemales==0] = eachFemales.sum(axis=1)[totalFemales==0]
    matrix.iloc[:,idx['mulheres']] = totalFemales
    return matrix

def totalIndices(matrix,axis=0):
    '''return a dict containing the index of the 'total' column for woman ['mulheres'] and men ['homens']'''

    index={}
    if axis==0:
        names = list(matrix.columns)
    elif axis==1:
        names = list(matrix.index)
    else:
        raise ValueError("No support for axis>1")

    for gender in ['homens', 'mulheres']:
        totalGender = [gender in x.lower() and 'total' in x.lower() for x in names]
        #index is the column with 'total GENDER' in it
        index[gender] = np.nonzero(totalGender)[0][0]
    assert index['homens'] < index['mulheres']
    return index


def compareGenderSum(matrix):
    '''Returns true if the sum of columns is equal to 'total' column'''

    (menEach,menTotal),(femaleEach,femaleTotal) = sumToTotal(matrix)
    return compareAmongNANS(menEach.sum(axis=1),menTotal), compareAmongNANS(femaleEach.sum(axis=1),femaleTotal)


def isDiscriminated(matrix):
    '''Determine how many indexes have values diferent from NaN outside 'total' column'''
    (menEach,_),(femaleEach,_) = sumToTotal(matrix)
    return (menEach>=0).sum(), (femaleEach>=0).sum() #zeros as counted as discriminated values

def getDemo(demoData, field, proportion = None):
    ''' Merges all companies data from a given field'''

    clusteredData = pd.DataFrame(columns=['specifics','company','variable','value'])
    for empresai in demoData:
        if proportion =='total' and field not in ['salarioGeneroRaca']:
            aux = propTotal(empresai[field])
        elif proportion == 'gender' and field not in ['salarioGeneroRaca']:
            aux = propGender(empresai[field])
        elif proportion == 'category':
            aux = propCategoryTotal(empresai[field])
        else:
            aux = pd.DataFrame.copy(empresai[field])
        aux['specifics'] = aux.index
        aux['company'] = empresai['nomeDaEmpresa'][1]
        aux = aux.melt(id_vars=['specifics','company'])
        aux['gender'] = aux.variable.apply(defineGender).values

        clusteredData= pd.concat((clusteredData, aux),axis=0)


    return clusteredData[clusteredData['value'].isnull() == False]

def propCategoryTotal(matrix,dropTots = True):
    '''substitute discriminated values of dataframe to the proportions given by sumToTotal'''

    if len(matrix.columns) == 2:
        return pd.DataFrame.copy(matrix) #for the cases in which there is no 'total' column

    aux = pd.DataFrame.copy(matrix)
    totalIdx = totalIndices(aux)
    (eachMales, totalMales), (eachFemales, totalFemales) = sumToTotal(matrix)

    aux.iloc[:,:totalIdx['homens']] = divideMatrixByVector(eachMales,totalMales)
    aux.iloc[:,totalIdx['homens']+1: totalIdx['mulheres'] ] = divideMatrixByVector(eachFemales,totalFemales)
    if dropTots:
        aux.drop(aux.columns[[totalIdx['homens'],totalIdx['mulheres']]], axis=1, inplace=True)
    return aux

def propTotal(matrix):
    '''substitute discriminated values of dataframe to proportions of the total of people in general
    with no distincion among categories'''

    aux = pd.DataFrame.copy(matrix)
    if len(matrix.columns) == 2: #for the cases in which there is no 'total' column
        totalIdx={'homens':0,'mulheres':1}
    else:
        totalIdx=totalIndices(aux)
    tot = matrix['Total de homens'].sum()+matrix['Total de mulheres'].sum()

    return matrix/tot

# For a given field of a given company
def propGender(matrix,returnBoth=False):
    '''For a given field of a given company, compare number of males and females in each
    category e.g. < 30yo, >50yo, black, white. if returnBoth == False (default), return only women data,
    otherwise returns the whole matrix in proportions
    '''

    aux = pd.DataFrame.copy(matrix)
    if len(matrix.columns) == 2: #for the cases in which there is no 'total' column
        totalIdx={'homens':0,'mulheres':1}
    else:
        totalIdx=totalIndices(aux)

    men = aux.iloc[:,:totalIdx['homens']+1]
    women = aux.iloc[:,totalIdx['homens']+1: totalIdx['mulheres']+1]
    tot = men.values+women.values
    men = np.divide(men,tot)
    women = np.divide(women,tot)
    if returnBoth:
        return pd.concat((men,women),axis=1)
    return women


def proportionConsistency(demoData,field):
    '''Flags as inconsistent any field that is filled with specifics that sum bigger than the total'''

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


def resumeSector(sectorDemo, field):
    sD = getDemo(sectorDemo,field)
    variables = sD['variable'].unique()
    specifics = sD['specifics'].unique()
    meanStdSector = pd.DataFrame(index=variables,columns=specifics)
    for vari in variables:
        for speci in specifics:
            specData = sD.iloc[np.logical_and(sD['variable']==vari,sD['specifics']==speci).values]
            meanStdSector[speci][vari] = specData['value'].values
            idx = totalIndices(meanStdSector,axis=1)
    return meanStdSector

def defineGender(x):
    if 'homens' in x.lower() or 'colaboradores' in x.lower():
        return 'men'
    elif 'mulheres' in x.lower() or 'colaboradoras' in x.lower():
        return 'women'
    else:
        print(x)
        raise ValueError('Cannot find gender')

def disgenderVar(x):
    x=x.lower()
    return x.replace('homens','').replace('mulheres','').replace('outras','outros').replace('colaboradoras','').replace('colaboradores','')

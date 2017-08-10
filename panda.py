#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import csv, json

# company = cny

def demog2array(rowList):
	# rowList: pd.Series obj
	# turns linearized array data back into an array
	# outputs a pandas dataFrame with tidy data
	labelList = rowList.index
	rows = [] # list of row names, or df indices
	cols = [] # list of col names, or df columns
	for label in labelList:
		cCol = label.split(' >> ')[1]
		cRow = label.split(' >> ')[2]
		#print rows
		if len(cols) == 0 or cCol not in cols:
			cols.append(cCol)
		if len(rows) == 0 or cRow not in rows:
			rows.append(cRow)
	outArray = pd.DataFrame(index=cols, columns=rows)
	n = 0

	empty = ["nt", "n", "tn", "-", "na", "--", "nd", "n/t", "tnt"] # empty field markers

	for item in rowList:
		cCol = labelList[n].split(' >> ')[1]
		cRow = labelList[n].split(' >> ')[2]
		n += 1
		try:
			if item.lower().strip() in empty:
				outArray.loc[cCol, cRow] = None
			else:
				outArray.loc[cCol, cRow] = int(item)
		except ValueError:
			print item
			outArray.loc[cCol, cRow] = None
	return outArray

def scoringQuestions(name, question, answer):
	# name = name of company, for debug
	# question = str containing question itself
	# answer = string containing set of answers given by company to above question
	outScore = 0 # full score for this question
	qDict = (q for q in questionList if q['question'].encode('utf-8') == question).next() # dict for specific 'question' at questionsList
	if isinstance(answer, basestring):
		cnyAnswers = answer.split(';') # answers provided by cny
		for cnyA in cnyAnswers:
			for ans, aScore in qDict['answers'].iteritems():
				if ans.encode('utf-8', 'ignore') == cnyA.strip():
					negativa = False # cny marcou respost 'negativa' ('n possui a politica X')?
					if aScore is False: # "negativa"
						negativa = True
					else:
						outScore += aScore
	return outScore

def idCny(cnyIP): # who's this company? fetch its metadata from ident.csv
	cnyID = ids[ids['IP'] == cnyIP]
	# returns a tuple "company name, respondent email"
	return str(cnyID['Nome da empresa/companhia respondente:']).split('\n')[0].split("  ")[-1].strip(), str(cnyID['Email de contato do/a respondente:']).split('\n')[0].split("  ")[-1].strip()

# setting up data frame
df = pd.read_csv('answers.csv', header=0) # raw data

# creating new columns
df["respEmail"] = ""
df["ciaNome"] = ""

labels = list(df.columns.values) # data labels

####### AUXILIARY FILES

questionList = json.loads(open('questions.json').read()) # list of multiple-choice questions; each question is a dict
qs = [q['question'].encode('utf-8') for q in questionList] # list of question names

ids = pd.read_csv('ident.csv') # list of form filling metadata, IPs, etc

parents = [row[3] for index, row in df.iterrows()] # list of companies, to use as row label on pandas dataframe

hiScore = ('',0) # which cny has the highest score?

# index is a company's index in the dataframe list of rows
# row is a list containing the answer for each column/question for a given company

####### COMPANY BY COMPANY ANALYSIS is where all the action unfolds

for index, row in df.iterrows():
	score = 0 # initial score for cny	
	
	cnyName = row[3] # mother company name

	# identifying company
	cnyID = idCny(row[0])
	df.loc[index, "respEmail"] = cnyID[1] # respondent email
	df.loc[index, "ciaNome"] = cnyID[0] # actual name, from ID form
	
	print "Processing company no. " + str(index) + ": " + cnyName

	# looping through multiple-choice questions
	indexCol = 0
	for col in row:
		if labels[indexCol] in qs: # this is a multiple-choice question
			points = scoringQuestions(row[3], labels[indexCol], col)
			score += points
			df.loc[index, labels[indexCol]] = points # add answer points as answer
		indexCol += 1

	####### DEMOGRAPHIC DATA is stored as dataframes - each dataframe is a specific column in the output DF
	# some tables required transposition so as to maintain a standard, roughly it goes like this:
	# GENDER+race/age/position/etc is always a column
	# specific categories are rows; e.g.:
	#    male/white | male/black | female/white | female/black
	# c1    2			2			5				2
	# c2    3			6			9				1
	# c3    3			5			9				9
	# c4    6			2			3				3

	# Preencher com a quantidade de colaboradores/as, de acordo com nível hierárquico, gênero, e etnia (Caso a empresa não tenha monitoramento pelo recorte de raça, indicar apenas o numero total de colaboradores)
	df.loc[index, "cargoGeneroRaca"] = demog2array(row[89:152])

	# Preencher com  a  quantidade  de  colaboradoras,  de  acordo  com nível  hierárquico,  gênero e faixa etária
	df.loc[index, "cargoGeneroIdade"] = demog2array(row[152:232])

	# Preencher com a quantidade de colaboradores/as, de acordo com o vínculo de colaboração, gênero e cor/etnia (caso a empresa não tenha monitoramento pelo recorte de raça, indicar apenas o numero total de colaboradores/as)
	df.loc[index, "vinculoGeneroRaca"] = demog2array(row[232:256]).transpose()

	# Preencher com a quantidade de colaboradores/as, de acordo com a jornada de trabalho (ou utilização de políticas de trabalho flexível), gênero e cor/etnia (caso a empresa não tenha monitoramento pelo recorte de raça, indicar apenas o numero total de colaboradores/as)
	df.loc[index, "jornadaGeneroRaca"] = demog2array(row[256:304])

	# Preencher com a quantidade de colaboradores, de acordo com a jornada de trabalho (ou utilização de políticas de trabalho flexível), gênero, e tipo de cargo
	df.loc[index, "jornadaGeneroCargo"] = demog2array(row[256:400])

	# Preencher  com os  valores  (em  R$) de salário  médio  na  empresa,  por nível  hierárquico, gênero,  e cor/etnia  (caso a empresa não tenha monitoramento pelo recorte de raça, indicar apenas o numero total de colaboradores/as). Não considerar remuneração variável
	df.loc[index, "salarioGeneroRaca"] = demog2array(row[400:448])

	# Preencher  com  a  quantidade  de  colaboradores/as  por nível  educacional  mais  avançado  que  já cursou, gênero e cor/etnia (caso a empresa não tenha monitoramento pelo recorte de raça, indicar apenas o numero total de colaboradores/as)
	df.loc[index, "educacaoGeneroRaca"] = demog2array(row[448:484])

	# Preencher  com  a  quantidade  de  colaboradores/as  por nível  educacional  mais  avançado  que  já cursou, gênero e faixa etária
	df.loc[index, "educacaoGeneroIdade"] = demog2array(row[484:532]).transpose()

	# Preencher com quantidade de contratações e desligamentos voluntários e involuntários, por gênero e faixa etária
	df.loc[index, "demissoesGeneroIdade"] = demog2array(row[532:556]).transpose()

	# Preencher  com  a  quantidade  de colaboradores  que  deixaram  a  empresa  voluntariamente  no  último exercício, de acordo com principais motivos para a saída, gênero e tipo de cargo
	df.loc[index, "motivosaidaGeneroCargo"] = demog2array(row[556:664])

	# Preencher com a quantidade de colaboradores/as, de acordo com tempo de permanência na empresa, gênero e raça/etnia (caso a empresa não tenha monitoramento pelo recorte de cor/raça, indicar apenas o numero total de colaboradores/as)
	df.loc[index, "permanenciaGeneroRaca"] = demog2array(row[664:700]).transpose()

	# Preencher  com  a  quantidade  de colaboradores/as  capacitados/as ou treinados/as,  de  acordo  com o  tipo de capacitação ou treinamento, gênero e cor/raça (caso a empresa não tenha monitoramento pelo recorte de cor/raça, indicar apenas o numero total de colaboradores/as)
	df.loc[index, "capacitacaoGeneroRaca"] = demog2array(row[700:754])

	# Preencher  com  a  quantidade  de colaboradores  capacitados ou treinados,  de  acordo  com o  tipo de capacitação ou treinamento, gênero e tipo de cargo
	df.loc[index, "capacitacaoGeneroCargo"] = demog2array(row[754:862])

	# Preencher  com  a  quantidade  de colaboradores/as,  de  acordo  com gênero e cor/raça,  com  dados relativos ao último exercício da empresa (caso a empresa não tenha monitoramento pelo recorte de cor/raça, indicar apenas o numero total de colaboradores/as)
	df.loc[index, "maternidadeGeneroRaca"] = demog2array(row[862:892])

	# Preencher  com  a  quantidade  de colaboradores,  de  acordo  com gênero e tipo de cargo,  com  dados relativos ao último exercício da empresa
	df.loc[index, "maternidadeGeneroCargo"] = demog2array(row[892:952])

	# Preencher  com  a  quantidade  de colaboradores/as em  relação  ao estado  civil,  por gênero e cor/raça (caso a empresa não tenha monitoramento pelo recorte de cor/raça, indicar apenas o numero total de colaboradores/as)
	df.loc[index, "estadocivilGeneroRaca"] = demog2array(row[952:988]).transpose()

	# Preencher  com  a  quantidade  de colaboradores/as em  relação  ao estado  civil,  por gênero e tipo de cargo
	df.loc[index, "estadocivilGeneroCargo"] = demog2array(row[988:1060]).transpose()

	# Preencher com a quantidade de colaboradores/as em relação ao número de filhos, por gênero e tipo de cargo
	df.loc[index, "filhosGeneroCargo"] = demog2array(row[1060:1120]).transpose()

	# Preencher com a quantidade de colaboradores/as relativa a cada cada categoria acerca da avaliação das oportunidades da empresa, em relação a gênero e cor/raça (caso a empresa não tenha monitoramento pelo recorte de cor/raça, indicar apenas o número total de colaboradores)
	df.loc[index, "avaliacaoGeneroRaca"] = demog2array(row[1120:1132]).transpose()

	# Preencher com a quantidade de colaboradores/as relativa a cada cada categoria acerca da avaliação das oportunidades da empresa, em relação a gênero e tipo de cargo
	df.loc[index, "avaliacaoGeneroCargo"] = demog2array(row[1132:1156]).transpose()

	# Preencher com a quantidade de integrantes do conselho de administração, por gênero, cor/raça e faixa etária (caso a empresa não tenha monitoramento pelo recorte de raça, indicar apenas o número total de colaboradores)
	df.loc[index, "conAdmIdadeGeneroRaca"] = demog2array(row[1156:1174]).transpose()

	# Preencher  com  a  quantidade  de integrantes do  conselho  de  administração,  por gênero e  tipo de formação (considerar graduação)
	df.loc[index, "conAdmFormacaoGenero"] = demog2array(row[1174:1184])

	# Preencher com a quantidade de colaboradores/as com deficiência, de acordo com nível hierárquico, gênero, e tipo de deficiência
	df.loc[index, "cargoGeneroDefic"] = demog2array(row[1184:1238]).transpose()

	# Preencher com a quantidade de colaboradores/as trans na empresa, de acordo com nível hierárquico e identidade de gênero
	df.loc[index, "cargoTrans"] = demog2array(row[1238:1256]).transpose()

	if score > hiScore[1]:
		hiScore = row[3], score

print hiScore
df.to_csv('output.csv', header=True, index=False, quoting=csv.QUOTE_ALL, escapechar= '\\')
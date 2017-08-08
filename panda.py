#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import csv, json

# company = cny

df = pd.read_csv('answers.csv', header=0) # raw data
labels = list(df.columns.values) # data labels

questionList = json.loads(open('questions.json').read()) # list of multiple-choice questions; each question is a dict
qs = [q['question'].encode('utf-8') for q in questionList] # list of question names

ids = pd.read_csv('ident.csv', header=0) # list of form filling metadata, IPs, etc

output = [] # list of dicts; each company will be output as a dict

def scoringQuestions(name, question, answer):
	outScore = 0 # full score for this question
	qDict = (q for q in questionList if q['question'].encode('utf-8') == question).next() # dict for specific 'question' at questionsList
	if isinstance(answer, basestring):
		cnyAnswers = answer.split(';') # answers provided by cny
		for cnyA in cnyAnswers:
			for ans, aScore in qDict['answers'].iteritems():
				if ans.encode('utf-8', 'ignore') == cnyA.strip():
					negativa = False # cny marcou respost 'negativa' ('n possui a politica X')?
					if aScore is False:
						negativa = True
					else:
						outScore += aScore
	""" this allows us to find out which companies checked scoring answers AND 'negativa'
	if negativa and outScore > 0:
		print outScore, name, question
	"""
	return outScore

def idCny(cnyIP): # who's this company? fetch its metadata from ident.csv
	cnyID = ids[ids['IP'] == cnyIP] 
	print cnyID

hiScore = ('',0) # which cny has the highest score?

# index is a company's index in the dataframe list of rows
# row is a list containing the answer for each column/question for a given company
for index, row in df.iterrows():
	score = 0 # initial score for cny	
	indexCol = 0
	
	# identifying company
	idCny(row[0])

	for col in row:
		if labels[indexCol] in qs: # this is a multiple-choice question
			score += scoringQuestions(row[3], labels[indexCol], col)
		indexCol += 1
	if score > hiScore[1]:
		hiScore = row[3], score

print hiScore
	#cia = {} # output dict for a given company
	#cia['ip'] = row[0]
	#scoringQuestions(label[])




	#print labels[1], labels[10]
	#print row[1], row[10]

"""
for ans in df.ix[:,46]: # testing
	ans = ans.split(";")
	for choice in ans:
		print choice
		total = 0
		neg = 0
		for cat in questionList:
			if cat["qs"]["question"] == u'A empresa possui quais das seguintes políticas ou ações relacionadas a programas de coaching?':
				for opt, point in cat["qs"]["answers"].iteritems():
					if point != False:
						if opt == choice:
							total =+ point
					else:
						neg =+ 1
		#if total > 0 and neg > 0:
			#print "total: " + str(total) + ", neg: " + str(neg)



def scoringQuestions(question):
	return question


#for cat in questionList:
#	print 

"""



"""
data = {
	"1. IP": df.loc[:, "IP"],
	"2. Controladora": df.loc[:,"Nome do grupo a que pertence a companhia (se houver):"],

	#trab flexivel
	"3. Medidas de conc. trab-familia-pessoal": df.loc[:, "A empresa adota quais das seguintes medidas de conciliação entre trabalho, família e vida pessoal quanto à jornada de trabalho de seus/as colaboradores/as?"],
	"4. Politicas de jornada flexivel": df.loc[:, "Quais das políticas ou práticas de jornada de trabalho flexível abaixo a empresa adota?"],
	"5. Outras politicas de jornada flexivel": df.loc[:, "Se a empresa possui outras políticas de jornada de trabalho flexível, listar quais:"],
	"6. Como e a quem praticas de jornada flexivel": df.loc[:, "Como e a quem a empresa destina práticas relativas às políticas de jornada de trabalho flexível?"],
	"7. Processo de concessao de pol. trab flexivel": df.loc[:, "Como se dá o processo de concessão de políticas de trabalho flexível (se houver) para os/as colaboradores/as? Há algum tipo de avaliação para esse tipo de concessão? Há algum outro tipo de requisito para a concessão além dos elencados na questão anterior?"],
	"8. Monitoramento de politicas de trab  flexivel": df.loc[:, "A empresa possui quais destas práticas relativas ao monitoramento de políticas de trabalho flexível?"],
	
	#discriminacao e assedio
	"9. Politicas contra disccriminacao de genero": df.loc[:, "Quais dessas políticas a empresa adota contra discriminação de gênero, assédio moral ou assédio sexual a colaboradoras?"],
	"10. Outras politicas contra discriminacao de genero": df.loc[:, "Se a empresa possui outras políticas contra a discriminação de gênero, assédio moral ou assédio sexual, listar:"],
	"11. Subestimacao e Preconceito": df.loc[:, "Quais destas práticas ou políticas a empresa possui para combater a cultura do preconceito contra a mulher e subestimação de sua capacidade?"],
	
	#lideranca
	"12. Politicas de lideranca": df.loc[:, "A empresa possui quais das seguintes ações relativas a programas de incentivo à liderança feminina?"],
	"13. Outras politicas de lideranca": df.loc[:, "Se a empresa possui outras políticas neste sentido, indicar quais:"]
}

"""
#output = pd.DataFrame(data, columns=data.keys())

#output.to_csv('heloisa.csv', quoting=1)
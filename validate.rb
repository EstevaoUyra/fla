require 'csv'
require 'rubygems' # gems relevantes
require 'date'

Encoding.default_internal, Encoding.default_external = ['utf-8'] * 2

# abre o CSV com respostas, printa o nome da controladora [campo [3]], e o numero total de itens naquela linha

CSV.foreach('answers.csv') do |row| # reads each row of data
	if row.length != 1257
		puts row[1]
		puts row.length
	end
end
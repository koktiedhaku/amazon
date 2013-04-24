
import nltk
import pprint
#import gensim
import re
import sys, getopt
import os
from nltk.tokenize import *
import codecs
import time
import pprint
from nltk.stem.snowball import SnowballStemmer
punct = [',','.','!', '?', ';', '+','-','*','|','(',')','\337','%', '=', '>','<','\u20ac','$','_','\u2013',':','&']	


def makeDir(path):
	global root
	global valmis
	print path
	if not os.path.exists(root+valmis+path):
		os.makedirs(root+valmis+path)

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

def lueRivit(tiedosto, output1, output2):
	for line in tiedosto:
		line = removeNonAscii(line)
		tokens = nltk.word_tokenize(line)		
		label =tokens.pop(0)
		label= label+' '+tokens.pop(0)
		clean_line = [w for w in tokens if not w in nltk.corpus.stopwords.words('english')]
		clean_line= [w.strip() for w in clean_line if w.strip() not in nltk.corpus.stopwords.words('english')]
		punctuation = re.compile(r'[-.?!,":;()|0-9]') 
		clean_line = [punctuation.sub("", word) for word in clean_line]
		clean_line = [w.lower() for w in clean_line]		
		stemmer = SnowballStemmer("english")
		unicode_line = nltk.Text([token.encode('utf-8') for token in clean_line])
		unicode_line =[stemmer.stem(word) for word in unicode_line]
		unicode_line.insert(0, label)
		clean_line.insert(0, label)
		comment= " ".join(unicode_line)
		comment2= " ".join(clean_line)
		tulos.write(comment + "\n")
		tulos_ws.write(comment2 + "\n")

def main(argv):
	global tulos
	global tulos_ws
	print len(argv)
	if len(argv)<3:
		print 'test.py -s <false/true> -i <inputfile> -o <outputfile> \n -s stem \n-i input text file\noutput textfile'
	else:
		inputfile = ''
		outputfile = ''
		outputfile2 = ''
		try:
			opts, args = getopt.getopt(argv,"hs:i:o:s:",["stem=","ifile=","ofile=", "ofile2="])
		except getopt.GetoptError:
			print 'test.py -i <inputfile> -o <outputfile>'
			sys.exit(2)
		for opt, arg in opts:
			if opt == '-h':
				print 'test.py -s <false/true> -i <inputfile> -o <outputfile> \n -s stem \n-i input text file\noutput textfile'
				sys.exit()
			elif opt in ("-i", "--ifile"):
				inputfile = arg
			elif opt in ("-o", "--ofile"):
				outputfile = arg
			elif opt in ("-s", "--ofile2"):
				outputfile2 = arg	
			else:
				print 'test.py -s <false/true> -i <inputfile> -o <outputfile> \n -s stem \n-i input text file\noutput textfile'
		print 'Input file is "', inputfile
		print 'Output file is "', outputfile
		file = open(inputfile, 'r' )
		tulos = open(outputfile2, 'w')
		tulos_ws = open(outputfile, 'w')
		lueRivit(file, tulos, tulos_ws)
		file.close()
		tulos.close()
		tulos_ws.close()
		
if __name__ == "__main__":
	main(sys.argv[1:])


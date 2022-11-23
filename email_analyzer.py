import math
import random

import time
import os
import shutil

import numpy as np
import re

import nltk
from transformers import pipeline

nltk.download('stopwords')
stop_words = set(nltk.corpus.stopwords.words('english'))

def time_diff(internal_time):
	t1 = time.gmtime(0)
	epoch = time.asctime(t1)
	current = round(time.time()*1000)
	y=int(internal_time)
	result=current-y;
	no_of_day = math.floor(result/86400000)
	return no_of_day

def write_dictionary_to_csv(filename, dict, header):
	file = open(filename, "w")
	file.write(header)
	for key in dict:
		file.write(str(key) + "," + str(dict[key]) + "\n")
	file.close()

def write_string_to_text(filename, string):
	file = open(filename,"w")
	file.write(str(string))
	file.close()

def write_word_tf_idf_to_csv(filename, word_list, tf_idf_dict):
	file = open(filename, "w")
	for word in word_list:
		file.write(str(word) + "," + str(tf_idf_dict[word]) + "\n")
	file.close()	

def write_metadata_to_csv(filename, list_of_meta_dictionary):
	file = open(filename, "w")
	file.write("email,day\n")
	for item in list_of_meta_dictionary:
		file.write(str(item["email"]) + "," + str(item["day"]) + "\n")
	file.close()		





def write_output(analyzer):
	if os.path.exists("output"):
		shutil.rmtree('output')
	os.makedirs("output")
	os.chdir("output")

	prediction_count = {}
	prediction_label = {}
	list_of_meta_dictionary = []


	for doc in analyzer.documents:
		meta_dictionary = {"email":doc.document, "header":doc.header, "sender":doc.sender, "day":doc.day}
		list_of_meta_dictionary.append(meta_dictionary)

		prefix = re.split("[.]", doc.document)[0]
		# prefix = re.split("[/]", prefix)[1]

		write_string_to_text(prefix+"_summary.txt", doc.summary)

		write_word_tf_idf_to_csv(prefix+"_keyword.csv", doc.top_nkey_words, doc.tf_idf_dict)

		if doc.prediction_label not in prediction_count:
			prediction_count[doc.prediction_label] = 1
		else:
			prediction_count[doc.prediction_label] += 1

		prediction_label[doc.document] = doc.prediction_label

	write_dictionary_to_csv("prediction_count.csv", prediction_count, "prediction_label,count\n")

	write_dictionary_to_csv("prediction_label.csv", prediction_label, "email,prediction_label\n")

	write_dictionary_to_csv("word_cloud.csv", analyzer.document_word_freq, "content,count\n")

	write_metadata_to_csv("duration.csv", list_of_meta_dictionary)


def filtered_words(word_list):
	filtered_words = [word for word in word_list if not word in stop_words]
	return filtered_words

def process_document(document):
	with open(document) as f:
		file_string = " ".join([l for l in f])
	return file_string	

def get_filtered_words(sentence):
	#split the words
	word_list = re.split(r"\s+", sentence)
	# convert everything to lower case
	word_list = list(map(lambda word: word.lower(), word_list))
	# remove words present in nltk stop words
	filtered_words = [word for word in word_list if not word in stop_words]
	# print("before punctuation \n", filtered_words, "\n")
	# remove punctuation from words
	filtered_words = list(filter(lambda word: not re.search(r"[^\w]", word), filtered_words))
	# print("after punctuation\n", filtered_words, "\n")
	return filtered_words



#stack overflow for sentence tokenization

def split_into_sentences(text):
	# Regex pattern
	alphabets= "([A-Za-z])"
	prefixes = "(Mr|St|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|Mt)[.]"
	suffixes = "(Inc|Ltd|Jr|Sr|Co)"
	starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
	acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
	websites = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
	digits = "([0-9])"
	section = "(Section \d+)([.])(?= \w)"
	item_number = "(^|\s\w{2})([.])(?=[-+ ]?\d+)"
	abbreviations = "(^|[\s\(\[]\w{1,2}s?)([.])(?=[\s\)\]]|$)"
	parenthesized = "\((.*?)\)"
	bracketed = "\[(.*?)\]"
	curly_bracketed = "\{(.*?)\}"
	enclosed = '|'.join([parenthesized, bracketed, curly_bracketed])

	text = " " + text + "  "
	text = text.replace("\n"," ")
	text = re.sub(prefixes,"\\1<prd>",text)
	text = re.sub(websites, lambda m: m.group().replace('.', '<prd>'), text)
	if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
	if "..." in text: text = text.replace("...","<prd><prd><prd>")
	text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
	text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
	text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
	text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
	text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
	text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
	text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
	text = re.sub(section,"\\1<prd>",text)
	text = re.sub(item_number,"\\1<prd>",text)
	text = re.sub(abbreviations, "\\1<prd>",text)
	text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
	text = re.sub(enclosed, lambda m: m.group().replace('.', '<prd>'), text)
	if "”" in text: text = text.replace(".”","”.")
	if "\"" in text: text = text.replace(".\"","\".")
	if "!" in text: text = text.replace("!\"","\"!")
	if "?" in text: text = text.replace("?\"","\"?")
	text = text.replace(".",".<stop>")
	text = text.replace("?","?<stop>")
	text = text.replace("!","!<stop>")
	text = text.replace("<prd>",".")
	# print(text)
	sentences = text.split("<stop>")
	if sentences[-1].isspace():
		# remove last since only whitespace
		sentences = sentences[:-1]
	sentences = [s.strip() for s in sentences]
	return sentences


# reference https://stackoverflow.com/questions/65262832/pre-trained-models-for-text-classification
class Classifier(object):

	def __init__(self, analyzer):
		self.classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')
		self.labels = ["academics", "career", "sports", "entertainment", "literary", "culture", "creativity"]
		self.hypothesis_template = 'These key words are about {}.'
		self.analyzer = analyzer
		self.classifcation_list = self.get_classification_list()
		return

	def find_prediction(self, sequence):
		prediction = self.classifier(sequence, self.labels, hypothesis_template=self.hypothesis_template, multi_label=True)
		return prediction["labels"][0]

	def get_classification_list(self):
		documents = self.analyzer.documents
		for document in documents:
			if document.summary != "" :
				document.prediction_label = self.find_prediction(document.summary)
			else:
				document.prediction_label = "random"


# https://towardsdatascience.com/tf-term-frequency-idf-inverse-document-frequency-from-scratch-in-python-6c2b61b78558
class Document(object):

	# takes document as argument
	def __init__(self, document):
		self.threshold = 0
		self.document = document


		self.header = ""
		self.sender = ""
		self.day = 0
		self.file_string = ""
		self.process_document(document)

		# creating sentence list
		self.sentence_list = split_into_sentences(self.file_string)

		# creating word list
		self.word_list = self.tokenize()

		# word frequncy and term frequency
		self.word_freq = self.compute_word_frequency()
		self.term_freq = self.compute_term_frequency()

		# list will be populated later from analyzer class
		self.tf_idf_dict = {}
		self.top_nkey_words = []
		self.summary= str()
		self.prediction_label = str()

	def process_document(self, document):
		with open("email/"+document) as f:
			for idx, line in enumerate(f):
				if idx == 0:
					self.header = line
				elif idx == 1:
					self.sender = line
				elif idx == 2:
					self.day = time_diff(line)
				else:
					self.file_string = self.file_string+line
		return

	def find_sentence_list(self, file_string):
		sentence_list = list(filter(lambda sentence:sentence!="", sentence_list))

	def tokenize(self):
		word_list = []
		for sentence in self.sentence_list:
			word_list = word_list + get_filtered_words(sentence)
		return word_list


	def compute_word_frequency(self):
		word_freq = {}
		for word in self.word_list:
			if word not in word_freq:
				word_freq[word] = 1
			else:
				word_freq[word] += 1
		return word_freq

	def compute_term_frequency(self):
		term_freq = {}
		corpus_length = len(self.word_list)
		for word in self.word_freq:
			term_freq[word] = self.word_freq[word]/float(corpus_length) 
		return term_freq

	def compute_tf_idf(self, inverse_document_frequency):
		for word in self.term_freq:
			self.tf_idf_dict[word] = self.term_freq[word] * inverse_document_frequency[word]
		return

	def compute_nsigma_threshold(self, n):
		# cal mean of weight of all the word in the doc
		effectiveFreqMean = np.mean( list(self.tf_idf_dict.values()) )	
		# cal std of weight of all the word in the doc
		effectiveFreqStd = np.std( list(self.tf_idf_dict.values()) )
		# cal weightThreshold of weight of all the word in the doc
		self.threshold = effectiveFreqMean + n * effectiveFreqStd
		return

	def find_top_nsigma_summary(self, n):
		self.compute_nsigma_threshold(n)
		for word in self.tf_idf_dict:
			if self.tf_idf_dict[word] >= self.threshold:
				self.top_nkey_words.append(word)

		for sentence in self.sentence_list:
			word_list = get_filtered_words(sentence)
			for word in word_list:
				if word in self.top_nkey_words:
					self.summary += sentence + ".\n"
					break
		return 


	
class Analyzer(object):
	def __init__(self, document_path, sigma):
		files = os.listdir(document_path)
		# print(files)
		files = list(filter(lambda doc: re.match(".*_mail.txt", doc), files))
		print(files)
		self.documents = list(map(lambda file: Document(file), files))
		# print(len(self.documents))
		# print(self.documents[0].word_freq)
		self.document_frequency = self.compute_document_frequency()
		self.inverse_document_frequency = self.compute_inverse_document_frequency()
		self.sigma = sigma
		self.document_word_freq = self.compute_word_frequency()

	def compute_word_frequency(self):
		document_word_freq  = {}
		for document in self.documents:
			for word in document.word_freq:
				if word not in document_word_freq:
					document_word_freq[word] = document.word_freq[word]
				else:
					document_word_freq[word] += document.word_freq[word]
		return document_word_freq

	def	compute_document_frequency(self):
		document_frequency = {}
		for document in self.documents:
			for word in document.word_freq:
				if word not in document_frequency:
					document_frequency[word] = 1
				else:
					document_frequency[word] += 1
		return document_frequency

	def compute_inverse_document_frequency(self):
		inverse_document_frequency = {}
		# total number of documents
		N = len(self.documents)
		for word in self.document_frequency:
			inverse_document_frequency[word] = math.log10((N+1)/float(self.document_frequency[word]+1)) 
		return inverse_document_frequency

	def compute_summary(self):
		for document in self.documents:
			document.compute_tf_idf(self.inverse_document_frequency)
			document.find_top_nsigma_summary(self.sigma)


def driver():
	analyzer = Analyzer("/home/spanda/Documents/software_lab/test/email", 2)
	analyzer.compute_summary()
	# classifier = Classifier(analyzer)
	# classifier.get_classification_list()
	prediction_label = ["academics", "career", "sports", "entertainment", "literary", "culture", "creativity"]
	for idx, doc in enumerate(analyzer.documents):
		doc.prediction_label = prediction_label[random.randint(0,6)]

	write_output(analyzer)
	print("summary finished")
	os.chdir("../")

# if __name__=="__main__":
# 	 main()

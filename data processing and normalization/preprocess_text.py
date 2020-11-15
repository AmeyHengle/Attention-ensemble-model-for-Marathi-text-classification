#!/usr/bin/env python
# coding: utf-8

# In[10]:


import re
import unicodedata
from queue import Queue
import pandas as pd
from indicnlp.tokenize.indic_tokenize import trivial_tokenize_indic


# In[109]:


class Preprocess:
        
        # --------------------------------------- Constructor --------------------------------------- 
   
        def __init__(self,stopword_list,minCount = 1000):
            self.data_path = ''
            self.stopword_list = stopword_list
            self.minCount = minCount
                

        # --------------------------------------- Preprocess --------------------------------------- 
        
        def expand_concatenations(self, word):
            
            
            if not re.match('[a-zA-Z]+', word) or re.match('/d+',word):
                for i in range(len(word)):
                    if not('DEVANAGARI ' in unicodedata.name(word[i])):
                        word = word[:i] if( len(word[i:]) < 2 and not word[i:].isnumeric()) else word[:i] + " " + word[i:]
                        break
            else:
                for i in range(len(word)):
                    if ('DEVANAGARI ' in unicodedata.name(word[i])):
                        word = word[i:] if( len(word[:i]) < 2 and not word[:i].isnumeric() ) else word[:i] + " " + word[i:]
                        break

            return(word)
    
        
        def clean_text(self,text: str) -> str:
            try:
                special_chars = r'''!()-[]{};:'"\,<>./?@#$%^&*_~'''
                stemmer = PorterStemmer()
                lemmatizer = WordNetLemmatizer()

                if not(isinstance(text, str)): text = str(text)

                #Removing unprintable characters
                text = ''.join(x for x in text if x.isprintable())

                # Cleaning the urls
                text = re.sub(r'https?://\S+|www\.\S+', '', text)

                # Cleaning the html elements
                text = re.sub(r'<.*?>', '', text)

                # Removing the punctuations
                text = re.sub('[!#?,.:";-@#$%^&*_~<>()/\-]', '', text)

                # Removing stopwords and words below minCount 
                if (self.minCount != 1000):
                    print('Enabled Mincount')
                    text = ' '.join([word for word in text.split() if word not in self.stopword_list and len(word) > self.minCount])
                else:
                    # Removing stop words
                    text = ' '.join([word for word in text.split() if word not in self.stopword_list])

                # Expanding noisy concatenations (Eg: algorithmआणि  -> algorithm आणि ) 
                text = ' '.join([self.expand_concatenations(word) for word in text.split()])


                return text
            
            except ValueError as ve:
                print('Error processing:\t',text)
                return ''
    
        def preprocess_text(self,text: str) -> str:

            try:
                if not(isinstance(text, str)): text = str(text)
                preprocessed_text = ""

                for word in text.split(): 
                    if (re.match('\d+', word)):
                        if(word.isnumeric()):
                            preprocessed_text = preprocessed_text + '#N' + " "
                        else:
                            preprocessed_text = preprocessed_text + word.lower() + " "

                    else:
                        if(re.match('[a-zA-Z]+', word)):
                            if not len(word) < 2:
                                word = word.lower()
    #                             word = lemmatizer.lemmatize(word, pos='v')
                                preprocessed_text = preprocessed_text + word + " "

                        else:
                            preprocessed_text = preprocessed_text + word + " "

                return preprocessed_text

            except ValueError as ve:
#                 print('Error processing:\t',text)
                return ''
            
        def split_devanagri_word(self,word: str, punctuations = True) -> str:
            try:
                q = Queue()
                l_index = 0
                if not(isinstance(word, str)): word = str(word)
                tokens = []
                
                for char in word:
                    
#                     print(char, '--->', unicodedata.name(char))
                    if not 'devanagari' in unicodedata.name(char).lower():
                        tokens.append(char)
                        continue
                        
                    if 'letter' in unicodedata.name(char).lower():
                        if q.empty():
                            tokens.append(char)
                        else:
                            while not q.empty():
                                tokens[len(tokens)-1] += q.get() 
                            tokens.append(char)   
                    else:
                        if punctuations == True:
                            q.put(char)
                    
                for i, char in reversed(list(enumerate(tokens.copy()))):
                    if('devanagari' in unicodedata.name(char).lower()):
                        l_index = i
#                         print(l_index)
                        break
                        
                while not q.empty():
                        tokens[l_index] += q.get() 
                
                return tokens
                
            except Exception as e:
#                 print('Error processing:\t',word)
                return ''
        
        def text2characters(self,text:str, punctuations = True)->str:
            try:
                if not(isinstance(text, str)): text = str(text)
                char_sequence = ""
                char_list = []
                
                for word in text.split():
                    seq = ' '.join([char for char in self.split_devanagri_word(word, punctuations)])                
                    char_sequence = char_sequence + seq + ' '
    
#                     print(word,'--->',seq)
                    
                return char_sequence
            
            except ValueError as ve:
                print('Error processing:\t',text)
                return ''
            
            
        def tokenize_characters(self, document):
            vocab = set()
            cnt = 0
            token_dict = {}
            
            if isinstance(document, list):
#                 print('Doc')
                for text in document:
                    char_sequence = self.text2characters(text)
                    tokens_indic = pd.Series(trivial_tokenize_indic(char_sequence))
                    word_counts = tokens_indic.value_counts()
                    
                    vocab = vocab.union(set(word_counts.keys()))

                print('Total Unique Tokens (Characters): {}'.format(len(vocab)))

                for char in vocab:
                    cnt += 1
                    token_dict[char] = cnt
            
            else:
#                 print('sent')
                char_sequence = self.text2characters(document)
                tokens_indic = pd.Series(trivial_tokenize_indic(char_sequence))
                word_counts = tokens_indic.value_counts()  
                vocab = vocab.union(set(word_counts.keys()))

                print('Total Unique Tokens (Characters): {}'.format(len(vocab)))

                for char in vocab:
                    cnt += 1
                    token_dict[char] = cnt
                
            return token_dict

        
        def text_to_sequence(self,document,token_dict):
            
            sequence_doc = []
            if isinstance(document, list):
                print('Total records: ',len(document))
                cnt = 0
                for text in document:
                    try:
                        char_array = self.text2characters(text).split()
                        text_sequence = [token_dict[x] for x in char_array]
                        sequence_doc.append(text_sequence)
                        cnt+=1
                    except:
                        print(text)
                        
                print('Records converted: ',cnt)
                
            else:
                char_array = self.text2characters(document).split()
                text_sequence = [token_dict[x] for x in char_array]
                sequence_doc.append(text_sequence)
                print('Records converted: 1')
                
            return sequence_doc
            


# In[ ]:





# In[80]:


if __name__ == '__main__':
    df = pd.read_csv('../Technodifacation/Data/training_data_marathi.csv')
    
    sampletext1 = df['text'].sample().values
    print(sampletext1)
    pp = Preprocess([])
    sampletext2 = 'त्यांना जनतेला पटवून द्यावे लागेल99'

    test_list1 = ['त्यांना','H20', '2H20','Animal2Animal' ,'सी२ओ२', 'लागेल99', 'Animalत्यांना',
                 'त्यांनाAnimal', 'Analogy_त्यांना', 'Science२१', '१२Number', '!@)$&%!#)&$!&$!$B Bo ', '११.२२','I', '१','1','11.22','a','B','सी']

    test_list2 = ['त्यांना CO2 2H20 सीओ२ लागेल99 , Animalत्यांना त्यांनाAnimal Analogy_त्यांना Science२१ १२Number',
                 '!@)$&%!#)&$!&$!$I am Atharva ११.२२ Kulkarni 11.22 a B 1 सी']

    for text in test_list2:
        print(text, '\t--->\t', pp.clean_text(text),'\n')   
#!/usr/bin/env python
# coding: utf-8

# In[4]:


from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM, SpatialDropout1D
from sklearn.model_selection import train_test_split
from keras.utils.np_utils import to_categorical
from keras.callbacks import EarlyStopping
from keras.layers import Dropout


# In[3]:


class Models:
    
    # --------------------------------------- Constructor --------------------------------------- 
    
#     def __init__(self, word_limit, embedding_dim, input_length):
        
#         self.word_limit = word_limit
#         self.embedding_dim = embedding_dim
#         self.input_length = input_length
        
        
    def model_A(self, x_train, y_train, num_labels ,epochs, batch_size):
        
        '''
        1. The first layer is the embedded layer that uses 100 length vectors to represent each word.
        2. SpatialDropout1D performs variational dropout in NLP models.
        3. The next layer is the LSTM layer with 100 memory units.
        4. The output layer must create 13 output values, one for each class.
        5. Activation function is softmax for multi-class classification.
        6. Because it is a multi-class classification problem, categorical_crossentropy is used as the loss function.
        
        '''
        
        model = Sequential()
        model.add(Embedding( self.word_limit, self.embedding_dim, input_length = self.input_length ))
        model.add(SpatialDropout1D(0.2))
        model.add(LSTM(100, dropout=0.2, recurrent_dropout=0.2))
        model.add(Dense(num_labels, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

        
        history = model.fit(x_train, y_train, epochs=epochs,
                            batch_size=batch_size,validation_split=0.1,
                            callbacks=[EarlyStopping(monitor='val_loss', patience=3, min_delta=0.0001)])
        
        return model


    def myLSTM_1(self, embedding_matrix, num_records ,pad_len, embedding_dim, num_labels):

            model = Sequential()
            model.add(Embedding (input_dim = num_records, output_dim = embedding_dim,
                                 input_length = pad_len, weights = [embedding_matrix]))
            
            model.add(SpatialDropout1D(0.2))
            model.add(LSTM(100, dropout=0.2, recurrent_dropout=0.2))
            model.add(Dense(num_labels, activation='softmax'))
            model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
            
            return model
# In[ ]:


# class Callback(tf.keras.callbacks.Callback):
    
#     def on_epoch_end(self,epochs,logs={}):
#         if(logs.get('accuracy') > 0.99):
#             print('Accuracy reached 99%, initiating callback')
#             self.model.stop_training = True


# In[ ]:





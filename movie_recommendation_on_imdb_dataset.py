# -*- coding: utf-8 -*-
"""Movie Recommendation on IMDB dataset

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jdq_kVYsdfQOITJQ-YoOkaq0f6lAVL97
"""

# @title Imports (run this cell)
from __future__ import print_function

#importing the Libraries
import io
import numpy as np
import pandas as pd
import collections
from mpl_toolkits.mplot3d import Axes3D
from IPython import display
from matplotlib import pyplot as plt
import sklearn
import sklearn.manifold
import tensorflow as tf
tf.logging.set_verbosity(tf.logging.ERROR)
from scipy import sparse
from scipy.stats import uniform

#load the dataset
from google.colab import files
uploaded = files.upload()

#Reading and Displaying the Movie Dataset
movie_dataset=pd.read_csv(io.StringIO(uploaded['movies.csv'].decode('utf-8')))
movie_dataset.head()

#Reading and Displaying the Ratings Dataset
rate_dataset=pd.read_csv(io.StringIO(uploaded['ratings.csv'].decode('utf-8')))
rate_dataset.head()

n_users = len(rate_dataset['userId'].unique())
n_items = len(rate_dataset['movieId'].unique())
R_shape = (n_users, n_items)
print (str(n_users) + ' users')
print (str(n_items) + ' items')

#668 Users Rated 10325 Movies

#Genre List
genre_list = ["Action", "Adventure", "Animation", "Children", 
                "Comedy", "Crime","Documentary", "Drama", "Fantasy",
                "Film-Noir", "Horror", "Musical", "Mystery","Romance",
                "Sci-Fi", "Thriller", "War", "Western"]

#Creating the Search Matrix

movie_dataset['Action']=0
movie_dataset['Adventure']=0
movie_dataset['Animation']=0
movie_dataset['Children']=0
movie_dataset['Comedy']=0
movie_dataset['Crime']=0
movie_dataset['Documentary']=0
movie_dataset['Drama']=0
movie_dataset['Fantasy']=0
movie_dataset['Film-Noir']=0
movie_dataset['Horror']=0
movie_dataset['Musical']=0
movie_dataset['Mystery']=0
movie_dataset['Romance']=0
movie_dataset['Sci-Fi']=0
movie_dataset['Thriller']=0
movie_dataset['War']=0
movie_dataset['Western']=0

for i in movie_dataset.index:
  g_list=movie_dataset['genres'][i].split("|")
  for a in g_list:
    if a in genre_list:
      movie_dataset[a][i]=1

movie_dataset.head()

rate_dataset=rate_dataset.drop('timestamp',1)
rate_dataset.head()

#Sparse Matrix for the Ratings
col = ["userId","movieId"]
rating_one_hot = pd.get_dummies(rate_dataset,columns = col)
rating_one_hot.head()

#Sparse_Matrix Alternative
row_ind = []
col_ind = []
data=[]
for ind in rate_dataset.index:
  x= rate_dataset['userId'][ind]
  y= rate_dataset['movieId'][ind]
  val=rate_dataset['rating'][ind]
  row_ind.append(x)
  col_ind.append(y)
  data.append(val)
  
rating_sparse = sparse.coo_matrix((data, (row_ind, col_ind)))

rating_matrix = pd.DataFrame.sparse.from_spmatrix(rating_sparse)
rating_matrix.head(40)
print(rating_matrix)

"""# Model-based Collaborative Filtering (Matrix Factorization approach)

### Non-Negative Matrix Factorisation Model
"""

parametersNMF_opt = {
                    'n_components' : 20,     # number of latent factors
                    'init' : 'random', 
                    'random_state' : 0,
                     'alpha' : 0.01, 
                    'max_iter' : 25
                }

#Fitting the Model (Non-Negative Matrix Factorization)
from sklearn.decomposition import NMF
model = NMF(**parametersNMF_opt)
transform_matrix = model.fit_transform(rating_matrix)
M = model.components_.T

# Making the predictions
rating_pred = M.dot(transform_matrix.T).T
                    
# Clipping values                                                    
rating_pred[rating_pred > 5] = 5.           # clips ratings above 5             
rating_pred[rating_pred < 1] = 1.           # clips ratings below 1

merge=pd.merge(movie_dataset,rate_dataset)
merge.head()

"""# Making Movie Recommendations for an Active User"""

def make_recommendation_activeuser(df,rating_matrix, prediction, user_idx, k=5):

    rated_items_df_user = pd.DataFrame(rating_matrix).iloc[user_idx, :]               # get the list of actual ratings of user_idx (seen movies)
    user_prediction_df_user = pd.DataFrame(prediction).iloc[user_idx,:]               # get the list of predicted ratings of user_idx (unseen movies)
    reco_df = pd.concat([rated_items_df_user, user_prediction_df_user], axis=1)       # merge both lists with the movie's title
    
   
    reco_df.columns = ['rating','prediction']

    
    # Return the 5 seen movies with the best actual Ratings
    print ('Preferred movies for user #', user_idx)                                   
    l=[]
    l= reco_df.sort_values(by='rating', ascending=False)[:k].index
    
    m=[]
    for a in l:
      m.append(df.loc[df['movieId'] == a, 'title'].iloc[0])
    concat1=reco_df.sort_values(by='rating', ascending=False)[:k]
    concat1['TITLE']=m
    print (concat1)
    
    #Return the 5 unseen movie with the best predicted Ratings
    print ('Recommended movies for user #', user_idx)   # returns the 5 unseen movies with the best predicted ratings
    reco_df = reco_df[ reco_df['rating'] == 0 ]
    x=[]
    x=reco_df.sort_values(by='prediction', ascending=False)[:k].index     
    
    y=[]
    for b in x:
      y.append(df.loc[df['movieId'] == b, 'title'].iloc[0])
    concat2=reco_df.sort_values(by='prediction', ascending=False)[:k]
    concat2['TITLE']=y
    print(concat2)
    print

make_recommendation_activeuser(movie_dataset,rating_matrix, rating_pred, user_idx=50, k=5)
make_recommendation_activeuser(movie_dataset,rating_matrix, rating_pred, user_idx=2, k=5)
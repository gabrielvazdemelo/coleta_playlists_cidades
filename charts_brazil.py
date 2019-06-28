# -*- coding: utf-8 -*-

import pandas as pd
import csv
import spotipy
import spotipy.util as util

#colunas da base de dados completa (Top 200 Brasil)
columns=['nome_faixa','artista','artista_uri','faixa','faixa_uri','preview_url','pop_faixa','mercados','album','album_uri']

#criando a base de dados
df = pd.DataFrame(columns=columns)

#dados para a autenticacao
username='XXXXXXX'
scope=None
client_id = 'XXXXXXXXXXXXXXXXXXXXX'
client_secret='XXXXXXXXXXXXXXXXXXXXX'
redirect_uri='http://localhost/callback'

#autenticando no spotify
token = util.prompt_for_user_token(username,scope,client_id,client_secret,redirect_uri)

#abrindo a conexao
sp = spotipy.Spotify(auth=token)

#pegando URLs das faixas no arquivo csv
with open('regional-br-weekly-2017-05-05--2017-05-12.csv', 'r') as arquivo:
    reader = csv.reader(arquivo, delimiter=',')
    for row in reader:
        faixa_url = row[4]
        response = sp.track(track_id=faixa_url)
        nome = response['name']
        print(nome)
        #encontrar a popularidade do artista
        df.loc[df.shape[0]]=[nome,response['artists'][0]['name'],response['artists'][0]['uri'],response['name'],response['uri'],response['preview_url'],response['popularity'],response['available_markets'],response['album']['name'],response['album']['uri']]

########### ARTISTAS ##################

artistas = df.drop_duplicates('artista_uri')

columns = ['artista_uri','pop_artista','seguidores','genero']

df2 = pd.DataFrame(columns=columns)

for index, row in artistas.iterrows():
    author = sp.artist(row['artista_uri'])
    print(row['artista'])
    df2.loc[df2.shape[0]]=[row['artista_uri'],author['popularity'],author['followers']['total'],author['genres']]

############ TRACKS ######################

faixas = df.drop_duplicates('faixa_uri')

columns = ['faixa_uri','acousticness','danceability','energy','instrumentalness','loudness','liveness','speechiness','valence']

df4 = pd.DataFrame(columns=columns)

for index, row in faixas.iterrows():
    faixa = sp.audio_features(tracks=[row['faixa_uri']])[0]
    print(row['faixa'])
    df4.loc[df4.shape[0]]=[row['faixa_uri'],faixa['acousticness'],faixa['danceability'],faixa['energy'],faixa['instrumentalness'],faixa['loudness'],faixa['liveness'],faixa['speechiness'],faixa['valence']]

############ ALBUMS ######################

albums = df.drop_duplicates('album_uri')

columns = ['album_uri','release_date']

df3 = pd.DataFrame(columns=columns)

for index, row in albums.iterrows():
    album = sp.album(row['album_uri'])
    print(row['album'])
    df3.loc[df3.shape[0]]=[row['album_uri'],album['release_date']]

#fazendo o merge entre as bases
resultado = pd.merge(df,df2, on='artista_uri', how='left')
resultado.drop('artista_uri', axis=1, inplace=True)

resultado2 = pd.merge(resultado,df3, on='album_uri', how='left')
resultado2.drop('album_uri',axis=1, inplace=True)

resultado3 = pd.merge(resultado2,df4, on='faixa_uri', how='left')
resultado3.drop('faixa_uri',axis=1, inplace=True)

#exportando
resultado3.to_excel('base_br_AAMMDD_a_AAMMDD.xlsx')

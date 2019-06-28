#!/usr/bin/env python3

#PLAYLISTS DAS CIDADES BRASILEIRAS

import urllib.request
from bs4 import BeautifulSoup
import spotipy
import spotipy.util as util
import pandas as pd
import os
from json.decoder import JSONDecodeError

#colunas da base de dados completa
columns=['playlist','numero','artista','artista_uri','artista_id','faixa','faixa_uri','preview_url','pop_faixa','mercados','album','album_uri']

#criando a base de dados
df = pd.DataFrame(columns=columns)

#dados para a autenticacao
username='12150841917'
scope=None
client_id = '943e460183f346b8b999aade242ba010'
client_secret='6cb83eb3383d4d9ca88793b1c1cdfa60'
redirect_uri='http://localhost/callback'

#autenticando no spotify
scope = 'streaming'
try:
    token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)
except (AttributeError, JSONDecodeError):
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)
    
    #abrindo a conexao
sp = spotipy.Spotify(auth=token)

#consultando no everynoise quais sao as playlists 'the sound of ...'
url = 'http://everynoise.com/everyplace.cgi?vector=activity&scope=BR'
request = urllib.request.Request(url)
opener = urllib.request.build_opener()
response = opener.open(request)

#response = urllib.request(url)
data = response.read()
soup = BeautifulSoup(data,'html.parser')

#colocando a mao na massa
for link in soup.find_all('a', 'note'):
    num_playlist = link.get('href').split(':')[2]
    #consultando no spotify os dados de cada playlist
    response = sp.user_playlist(user='thesoundsofspotify',playlist_id=num_playlist)
    nome = response['name']
    tracks = response['tracks']
    print(nome)
    #consultado cada faixa de uma playlist
    for i, item in enumerate(tracks['items']):
        track = item['track']
        #encontrar a popularidade do artista
        df.loc[df.shape[0]]=[nome,i+1,track['artists'][0]['name'],track['artists'][0]['uri'],track['artists'][0]['id'],track['name'],track['uri'],track['preview_url'],track['popularity'],track['available_markets'],track['album']['name'],track['album']['uri']]

########### ARTISTAS E ARTISTAS RELACIONADOS ##################

artistas = df.drop_duplicates('artista_uri')

columns = ['artista_uri','pop_artista','seguidores','genero']

df2 = pd.DataFrame(columns=columns)

for index, row in artistas.iterrows():
    author = sp.artist(row['artista_uri'])
    print(row['artista'])
    df2.loc[df2.shape[0]]=[row['artista_uri'],author['popularity'],author['followers']['total'],author['genres']]
    
#fazendo o merge entre as bases
resultado = pd.merge(df,df2, on='artista_uri', how='left')
resultado.drop('artista_uri', axis=1, inplace=True)

#exportando
resultado.to_excel('base_cid_br_AAMMDD.xlsx')

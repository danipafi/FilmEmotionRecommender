#!/usr/bin/env python
# coding: utf-8

# In[1]:


# In[2]:

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Título da aplicação
st.title("Minha Aplicação Streamlit")

# Upload de arquivo CSV
arquivo = st.file_uploader("Envie um arquivo CSV", type="csv")

if arquivo is not None:
    # Carregar dados
    df = pd.read_csv(arquivo)
    
    # Exibir DataFrame
    st.write("Dados carregados:")
    st.write(df.head())
    
    # Criar gráfico
    st.write("Gráfico de linhas:")
    fig, ax = plt.subplots()
    ax.plot(df["coluna_x"], df["coluna_y"])
    ax.set_title("Gráfico de Linhas")
    st.pyplot(fig)

# In[ ]:





#!/usr/bin/env python
# coding: utf-8

# In[1]:


# In[2]:

import streamlit as st
import pandas as pd


# Título da aplicação
st.title("Minha Primeira Aplicação com Streamlit")

# Texto simples
st.write("Olá, mundo! Esta é minha primeira aplicação Streamlit.")

# Slider para entrada de dados
numero = st.slider("Escolha um número", 0, 100)

# Exibir o número escolhido
st.write(f"Você escolheu o número: {numero}")


# In[ ]:





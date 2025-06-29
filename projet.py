import streamlit as st
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup as bs


def Scrapping(Categorie, Nombre_de_pages,type_catg):
    df = pd.DataFrame()
    data = []
    for p in range(Nombre_de_pages):
        url = f"https://sn.coinafrique.com/categorie/{Categorie}?page={p}"
        res = requests.get(url)

        if res.status_code != 200:
            print(f"Erreur sur la page {p}")
            continue

        soup = bs(res.text, "html.parser")
        containers = soup.find_all("div", class_="card")

        
        for container in containers:
            try:
                image_tag = container.find("img", class_="ad__card-img")
                image_lien = image_tag['src'] if image_tag is not None and image_tag.has_attr('src') else None
                prix_tag = container.find("p", class_="ad__card-price")
                prix = prix_tag.text.strip().replace('\u202f', ' ') if prix_tag else None
                type_tag = container.find("p", class_="ad__card-description")
                type = type_tag.text.strip().replace('\u202f', ' ') if type_tag else None
                adresse_tag = container.find("p", class_="ad__card-location")
                adresse = adresse_tag.text.strip().replace('location_on', '') if adresse_tag else None

                dic = {
                    "image_lien": image_lien,
                    "prix": prix,
                    type_catg: type,
                    "adresse": adresse,
                }
                data.append(dic)

            except Exception as e:
                print(f"Erreur sur une annoce : {e}")
                continue
        df = pd.DataFrame(data).dropna()
        print(df)

    return df

st.set_page_config(page_title="MINI projet DC", page_icon="🕸️", layout="wide")


st.sidebar.title("Navigation")
option = st.sidebar.selectbox(
    "Choisissez une option :",
    [
        "Scraper des données",
        "Visualiser les données scrapées",
        "Remplir le formulaire d'évaluation"
    ]
)

st.title("MINI projet DC - Mouhamed Diouf")
# Scraper des données
if option == "Scraper des données":
    st.subheader("Scraping des données")
    
    nombre_pages = st.sidebar.slider("Nombre de pages à scraper :", 1, 20, 1)

    if st.button("Scraper les vetements pour homme"):
        st.info(f"Lancement du scraping pour {nombre_pages} page(s)...")
        data = Scrapping(Categorie="vetements-homme", Nombre_de_pages=nombre_pages, type_catg="type_habits")
        data.to_csv("data_scrapees.csv", index=False)
        df = pd.read_csv("data_scrapees.csv")
        st.dataframe(df)
        st.success("Scraping terminé. Les données ont été enregistrées avec succès.")
        
    if st.button("Scraper les chaussures pour homme"):
        st.info(f"Lancement du scraping pour {nombre_pages} page(s)...")
        data = Scrapping(Categorie="chaussures-homme", Nombre_de_pages=nombre_pages, type_catg="type_chaussures")
        data.to_csv("data_scrapees.csv", index=False)
        df = pd.read_csv("data_scrapees.csv")
        st.dataframe(df)
        st.success("Scraping terminé. Les données ont été enregistrées avec succès.")
        
    if st.button("Scraper les vetements pour enfants"):
        st.info(f"Lancement du scraping pour {nombre_pages} page(s)...")
        data = Scrapping(Categorie="vetements-enfants", Nombre_de_pages=nombre_pages, type_catg="type_habits")
        data.to_csv("data_scrapees.csv", index=False)
        df = pd.read_csv("data_scrapees.csv")
        st.dataframe(df)
        st.success("Scraping terminé. Les données ont été enregistrées avec succès.")
        
    if st.button("Scraper les chaussures pour enfants"):
        st.info(f"Lancement du scraping pour {nombre_pages} page(s)...")
        data = Scrapping(Categorie="chaussures-enfants", Nombre_de_pages=nombre_pages, type_catg="type_chaussures")
        data.to_csv("data_scrapees.csv", index=False)
        df = pd.read_csv("data_scrapees.csv")
        st.dataframe(df)
        st.success("Scraping terminé. Les données ont été enregistrées avec succès.")
# Visualiser les données scrapées       
elif option == "Visualiser les données scrapées":
    st.subheader("Visualiser les données scrapées")

    if st.button("Visualiser les vetements pour homme"):
        df = pd.read_csv('data/coinafrique-vetements-homme.csv')
        st.dataframe(df)
    if st.button("Visualiser les chaussures pour homme"):
        df = pd.read_csv('data/coinafrique-chaussures-homme.csv')
        st.dataframe(df)
    if st.button("Visualiser les vetements pour enfants"):
        df = pd.read_csv('data/coinafrique-vetements-enfants.csv')
        st.dataframe(df)
    if st.button("Visualiser les chaussures pour enfants"):
        df = pd.read_csv('data/coinafrique-chaussures-enfants.csv')
        st.dataframe(df)
# Remplir le formulaire d'évaluation
elif option == "Remplir le formulaire d'évaluation":
    st.subheader("Formulaire d'évaluation")

    st.write("Merci de prendre un moment pour évaluer cette application.")
    st.components.v1.iframe(src="https://ee.kobotoolbox.org/68SAXgxx", height=1000, width=700)


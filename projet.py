import streamlit as st
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup as bs
import plotly.express as px

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
        "Dashboard",
        "Scraper des données",
        "Visualiser les données scrapées",
        "Remplir le formulaire d'évaluation"
    ]
)


st.title("MINI projet DC - Mouhamed Diouf")
# Dashboard (graphiques)
# Dashboard (graphiques)
if option == "Dashboard":
    st.subheader("Dashboard des données scrapées")
    fichiers = [
        'data/coinafrique-vetements-homme.csv',
        'data/coinafrique-chaussures-homme.csv',
        'data/coinafrique-vetements-enfants.csv',
        'data/coinafrique-chaussures-enfants.csv',
    ]
    dataframes = []
    for fichier in fichiers:
        if os.path.exists(fichier):
            df_temp = pd.read_csv(fichier)
            df_temp["source"] = os.path.basename(fichier).replace("coinafrique-", "").replace(".csv", "")
            dataframes.append(df_temp)
    
    if dataframes:
        df = pd.concat(dataframes, ignore_index=True)
        
        # Nettoyage des prix amélioré
        def nettoyer_prix(val):
            if pd.isna(val) or val == "sur demande" or val == "":
                return None
            if isinstance(val, str):
                # Nettoyer les prix en supprimant CFA, espaces, points et virgules
                val = val.replace("CFA", "").replace(" ", "").replace(".", "").replace(",", "")
                try:
                    return float(val)
                except:
                    return None
            elif isinstance(val, (int, float)):
                return float(val)
            return None
        
        df["prix_clean"] = df["prix"].apply(nettoyer_prix)
        
        # Affichage des statistiques générales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total articles", len(df))
        with col2:
            st.metric("Articles avec prix", len(df[df["prix_clean"].notna()]))
        with col3:
            prix_valides = df["prix_clean"].dropna()
            if not prix_valides.empty:
                st.metric("Prix moyen", f"{prix_valides.mean():,.0f} CFA")
            else:
                st.metric("Prix moyen", "N/A")
        with col4:
            st.metric("Sources", df["source"].nunique())
        
        #  Répartition des types d'articles (plus lisible)
        st.write("### Répartition des types d'articles")
        type_counts = df["type"].value_counts()
        if len(type_counts) > 15:
            type_counts = type_counts.head(15)
            st.info(f"Affichage des 15 types les plus fréquents sur {df['type'].nunique()} types total")
        
        fig1 = px.bar(
            x=type_counts.index,
            y=type_counts.values,
            title="Répartition des types d'articles",
            labels={'x': 'Type d\'article', 'y': 'Nombre d\'annonces'}
        )
        fig1.update_layout(xaxis_tickangle=-45, height=500)
        st.plotly_chart(fig1, use_container_width=True)
        
        #  Répartition géographique 
        st.write("### Top 10 des zones avec le plus d'annonces")
        adresse_counts = df["adresse"].value_counts().head(10)
        
        fig2 = px.bar(
            x=adresse_counts.values,
            y=adresse_counts.index,
            orientation='h',
            title="Top 10 des zones géographiques",
            labels={'x': 'Nombre d\'annonces', 'y': 'Zone'}
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
        
        #  Distribution des prix (améliorée)
        st.write("### Analyse des prix")
        prix_valides = df["prix_clean"].dropna()
        
        if not prix_valides.empty:
            # Statistiques des prix
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Statistiques des prix:**")
                st.write(f"- Prix minimum: {prix_valides.min():,.0f} CFA")
                st.write(f"- Prix maximum: {prix_valides.max():,.0f} CFA")
                st.write(f"- Prix médian: {prix_valides.median():,.0f} CFA")
                st.write(f"- Écart-type: {prix_valides.std():,.0f} CFA")
            
            with col2:
                # Filtrer les prix aberrants pour une meilleure visualisation
                q1 = prix_valides.quantile(0.25)
                q3 = prix_valides.quantile(0.75)
                iqr = q3 - q1
                prix_filtered = prix_valides[
                    (prix_valides >= q1 - 1.5 * iqr) & 
                    (prix_valides <= q3 + 1.5 * iqr)
                ]
                
                if len(prix_filtered) > 0:
                    st.write("**Distribution (sans valeurs aberrantes):**")
                    fig3 = px.histogram(
                        x=prix_filtered,
                        nbins=30,
                        title="Distribution des prix",
                        labels={'x': 'Prix (CFA)', 'y': 'Nombre d\'articles'}
                    )
                    st.plotly_chart(fig3, use_container_width=True)
            
        
        # Articles par source
        st.write("### Répartition des articles par source")
        source_counts = df["source"].value_counts()
        
        fig5 = px.pie(
            values=source_counts.values,
            names=source_counts.index,
            title="Répartition des articles par source"
        )
        st.plotly_chart(fig5, use_container_width=True)
        
      
        
    else:
        st.error("Aucune donnée trouvée. Merci de scraper ou visualiser des données d'abord.")
# Scraper des données
elif option == "Scraper des données":
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


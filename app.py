import streamlit as st
from reddit_utils import get_reddit_comments
from sentiment_utils import analyze_sentiments
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Setup
st.set_page_config(page_title="Tennis Sentiment Analysis", layout="wide")
st.title("🎾 Analyse des sentiments des fans de tennis (Reddit)")

# ----- SESSION STATE INIT -----
if "joueur" not in st.session_state:
    st.session_state.joueur = ""
if "joueur1" not in st.session_state:
    st.session_state.joueur1 = ""
if "joueur2" not in st.session_state:
    st.session_state.joueur2 = ""

# -------- SETTINGS --------
annee = st.selectbox("Filtrer par année 📅", options=[2025, 2024, 2023, 2022, 2021])
nb_comments = st.slider("Nombre de commentaires à analyser", 10, 200, 50)


# ANALYSE INDIVIDUELLE
st.header("🔍 Analyse individuelle")
with st.form("individuel_form"):
    st.session_state.joueur = st.text_input(
        "Nom du joueur 🎾",
        value=st.session_state.joueur,
        placeholder="Ex: Djokovic, Nadal, Alcaraz",
        key="joueur_input"
    )
    submit_indiv = st.form_submit_button("Analyser")


# COMPARAISON DE DEUX JOUEURS
st.header("⚔️ Comparaison de deux joueurs")
with st.form("comparaison_form"):
    col1, col2 = st.columns([4, 4])
    with col1:
        st.session_state.joueur1 = st.text_input("Joueur 1", value=st.session_state.joueur1, key="joueur1_input")
    with col2:
        st.session_state.joueur2 = st.text_input("Joueur 2", value=st.session_state.joueur2, key="joueur2_input")

    submit_compare = st.form_submit_button("Analyser")


# -------- ANALYSE COMPARAISON --------
if submit_compare and st.session_state.joueur1 and st.session_state.joueur2:
    with st.spinner("🔍 Récupération des données pour les deux joueurs..."):
        com1 = get_reddit_comments(st.session_state.joueur1, nb_comments, annee)
        com2 = get_reddit_comments(st.session_state.joueur2, nb_comments, annee)

    df1 = analyze_sentiments(com1)
    df1["joueur"] = st.session_state.joueur1
    df2 = analyze_sentiments(com2)
    df2["joueur"] = st.session_state.joueur2

    st.subheader("📋 Données analysées pour chaque joueur")
    col_tab1, col_tab2 = st.columns(2)
    with col_tab1:
        st.markdown(f"**Commentaires pour {st.session_state.joueur1}**")
        st.dataframe(df1)
    with col_tab2:
        st.markdown(f"**Commentaires pour {st.session_state.joueur2}**")
        st.dataframe(df2)

    st.subheader("📊 Répartition des sentiments pour chaque joueur")
    col_graph1, col_graph2 = st.columns(2)
    with col_graph1:
        fig1, ax1 = plt.subplots(figsize=(5, 3))
        sns.countplot(data=df1, x="sentiment", palette="Set2", ax=ax1)
        ax1.set_title(f"Répartition sentiments {st.session_state.joueur1}")
        st.pyplot(fig1)
    with col_graph2:
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        sns.countplot(data=df2, x="sentiment", palette="Set2", ax=ax2)
        ax2.set_title(f"Répartition sentiments {st.session_state.joueur2}")
        st.pyplot(fig2)

elif submit_compare and (not st.session_state.joueur1 or not st.session_state.joueur2):
    st.warning("⚠️ Pour la comparaison, veuillez remplir **les deux** champs Joueur 1 et Joueur 2.")


# -------- ANALYSE INDIVIDUELLE --------
if submit_indiv and st.session_state.joueur:
    with st.spinner("🔍 Récupération des commentaires Reddit..."):
        commentaires = get_reddit_comments(st.session_state.joueur, nb_comments, annee)

    if not commentaires:
        st.warning("Aucun commentaire trouvé pour ce joueur.")
    else:
        df = analyze_sentiments(commentaires)

        st.download_button(
            label="📥 Télécharger les résultats en CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name=f'{st.session_state.joueur}_sentiments_{annee}.csv',
            mime='text/csv'
        )

        score_global = df["score"].mean()
        st.metric("Indice global de sentiment", round(score_global, 2))
        if score_global > 0.2:
            st.success("👍 Bonne perception générale des fans")
        elif score_global < -0.2:
            st.error("👎 Mauvaise perception générale des fans")
        else:
            st.warning("😐 Perception générale neutre")

        st.subheader(f"🧠 Analyse de sentiments pour {st.session_state.joueur} en {annee}")
        st.dataframe(df)

        col_graph3, col_graph4 = st.columns(2)

        with col_graph3:
            st.subheader("📈 Répartition des sentiments")
            fig, ax = plt.subplots(figsize=(5, 3))
            sns.countplot(data=df, x="sentiment", palette="Set2", ax=ax)
            st.pyplot(fig)

        with col_graph4:
            st.subheader("📈 Évolution des sentiments dans le temps")
            evol_df = df.groupby(["date", "sentiment"]).size().reset_index(name='count')
            fig2, ax2 = plt.subplots(figsize=(5, 3))
            sns.lineplot(data=evol_df, x="date", y="count", hue="sentiment", ax=ax2)
            st.pyplot(fig2)

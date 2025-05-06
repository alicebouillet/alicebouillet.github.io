import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
import plotly.express as px
import matplotlib as plt
# --- Chargement ou initialisation des données ---
lien_excel = "Gestion de projet - Manifestations.xlsx"
lien_sauvegarde = "Gestion de projet - Manifestations.xlsx"

if "df" not in st.session_state:
    try:
        st.session_state.df = pd.read_excel(lien_excel)
    except FileNotFoundError:
        st.session_state.df = pd.DataFrame(columns=[
            "ID de tâche", "Nom de tâche", "Progression", "Pourcentage", "Priorité", "Attribué à",
            "Date de début", "Date de fin", "Etiquettes", "Description", "Budget prévu", "Budget utilisé"
        ])

df = st.session_state.df
df["Description"] = df["Description"].astype(str)
df["Date de début"] = pd.to_datetime(df["Date de début"], errors='coerce')

# --- Sidebar navigation ---
st.sidebar.title("Navigation")
onglet = st.sidebar.radio("Aller à :", [
    "📊 Tableau de bord", "📝 Tâches restantes", "📋 Liste complète",
    "➕ Ajouter une tâche", "✏️ Modifier une tâche","🗑️ Supprimer une tâche", "💰 Budget"
])

# --- Onglet 1 : Tableau de bord principal ---
if onglet == "📊 Tableau de bord":
    st.title("📊 Tableau de bord")
        # Histogramme du nombre de tâches par compartiment
    fig1 = px.histogram(df, x="Nom du compartiment", color="Progression", barmode="group",
                        title="Répartition des tâches par compartiment et progression",
                        labels={"Nom du compartiment": "Compartiment", "Progression": "Statut des tâches"})
    st.plotly_chart(fig1, use_container_width=True)

    # Diagramme en barres empilées : Nombre de tâches par compartiment et statut de progression
    progression_compartiment = df.groupby(["Nom du compartiment", "Progression"]).size().reset_index(name="Nombre de tâches")
    fig2 = px.bar(progression_compartiment, x="Nom du compartiment", y="Nombre de tâches",
                  color="Progression", title="Nombre de tâches par compartiment et progression",
                  labels={"Nom du compartiment": "Compartiment", "Nombre de tâches": "Nombre de tâches"})
    st.plotly_chart(fig2, use_container_width=True)

    # Camembert : Répartition globale des tâches par statut de progression
    statut_counts = df["Progression"].value_counts().reset_index()
    statut_counts.columns = ["Statut", "Nombre de tâches"]
    fig3 = px.pie(statut_counts, values="Nombre de tâches", names="Statut",
                  title="Répartition des tâches selon le statut",
                  color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig3, use_container_width=True)
    for index, row in df.iterrows():
        # Afficher le nom de la tâche
        st.markdown(f"**{row['Nom de tâche']}**")

        # Convertir le pourcentage en entier
        progress_percent = int(row["Pourcentage"])

        # Afficher la barre de progression
        st.progress(progress_percent)
        #Affichage descriptions
        st.markdown(f"{row['Description']}")

# --- Onglet 2 : Tâches restantes ---
elif onglet == "📝 Tâches restantes":
    st.title("📝 Tâches à faire")
    restantes = df[df["Progression"] != "Terminé"]
    st.dataframe(restantes)

# --- Onglet 3 : Liste complète ---
elif onglet == "📋 Liste complète":
    st.title("📋 Toutes les tâches")
    st.dataframe(df)

# --- Onglet 4 : Ajouter une tâche ---
elif onglet == "➕ Ajouter une tâche":
    st.title("➕ Ajouter une nouvelle tâche")

    with st.form("form_ajout"):
        nom = st.text_input("Nom de la tâche")
        description = st.text_area("Description")
        progression = st.selectbox("Progression", ["Non démarrées", "En cours", "Terminées"])
        pourcentage = st.slider("Pourcentage", 0, 100, 0)
        priorite = st.selectbox("Priorité", ["Faible", "Moyen", "Élevée"])
        assignee = st.text_input("Attribué à", "Alice Boullet")
        date_debut = st.date_input("Date de début", datetime.today())
        date_fin = st.date_input("Date de fin", datetime.today())
        etiquettes = st.text_input("Étiquettes (séparées par des virgules)")
        budget_prevu = st.number_input("Budget prévu (€)", min_value=0.0, value=0.0)
        budget_utilise = st.number_input("Budget utilisé (€)", min_value=0.0, value=0.0)
        inclus = st.text_input("Inclus dans budget (ex : repas, transport...)")
        prise_en_charge = st.text_input("Pris en charge par (ex : BDE, partenaires...)")

        submitted = st.form_submit_button("Ajouter")
        if submitted:
            nouvelle_tache = {
                "ID de tâche": str(uuid.uuid4()),
                "Nom de tâche": nom,
                "Description": str(description),
                "Progression": progression,
                "Pourcentage": pourcentage,
                "Priorité": priorite,
                "Attribué à": assignee,
                "Date de début": date_debut,
                "Date de fin": date_fin,
                "Etiquettes": etiquettes,
                "Budget prévu": budget_prevu,
                "Budget utilisé": budget_utilise,
                "Inclus dans budget": inclus,
                "Pris en charge par": prise_en_charge
            }
            st.session_state.df = st.session_state.df.append(nouvelle_tache, ignore_index=True)
            st.success("✅ Tâche ajoutée avec succès.")

# --- Onglet 5 : Modifier une tâche ---
elif onglet == "✏️ Modifier une tâche":
    st.title("✏️ Modifier une tâche existante")

    if df.empty:
        st.info("Aucune tâche à modifier.")
    else:
        noms_taches = df["Nom de tâche"].tolist()
        selection = st.selectbox("Sélectionnez une tâche :", noms_taches)
        tache_index = df[df["Nom de tâche"] == selection].index[0]
        tache = df.loc[tache_index]

        # Fonction pour sécuriser les dates
        def convertir_date(val):
            if pd.isnull(val):
                return datetime.today().date()
            return pd.to_datetime(val).date()

        with st.form("form_modif"):
            nom = st.text_input("Nom de la tâche", tache["Nom de tâche"])
            description = st.text_input("Description", tache["Description"])
            progression = st.selectbox("Progression", ["Non démarrées", "En cours", "Terminées"],
                                       index=["Non démarrées", "En cours", "Terminées"].index(str(tache["Progression"])))
            pourcentage = st.slider("Pourcentage", 0, 100, int(tache["Pourcentage"]))
            priorite = st.selectbox("Priorité", ["Faible", "Moyen", "Élevée"],
                                    index=["Faible", "Moyen", "Élevée"].index(str(tache["Priorité"])))
            assignee = st.text_input("Attribué à", tache["Attribué à"])
            date_debut = st.date_input("Date de début", convertir_date(tache["Date de début"]))
            date_fin = st.date_input("Date de fin", convertir_date(tache["Date de fin"]))
            etiquettes = st.text_input("Étiquettes", tache["Étiquettes"])
            budget_prevu = st.number_input("Budget prévu (€)", min_value=0.0, value=float(tache["Budget prévu"]))
            budget_utilise = st.number_input("Budget utilisé (€)", min_value=0.0, value=float(tache["Budget utilisé"]))
            inclus = st.text_input("Inclus dans budget", tache.get("Inclus dans budget", ""))
            prise_en_charge = st.text_input("Pris en charge par", tache.get("Pris en charge par", ""))
            modif = st.form_submit_button("💾 Enregistrer les modifications")
            if modif:
                df.at[tache_index, "Nom de tâche"] = nom
                df.at[tache_index, "Description"] = str(description)
                df.at[tache_index, "Progression"] = progression
                df.at[tache_index, "Pourcentage"] = pourcentage
                df.at[tache_index, "Priorité"] = priorite
                df.at[tache_index, "Attribué à"] = assignee
                df.at[tache_index, "Date de début"] = date_debut
                df.at[tache_index, "Date de fin"] = date_fin
                df.at[tache_index, "Etiquettes"] = etiquettes
                df.at[tache_index, "Budget prévu"] = budget_prevu
                df.at[tache_index, "Budget utilisé"] = budget_utilise
                df.at[tache_index, "Inclus dans budget"] = inclus
                df.at[tache_index, "Pris en charge par"] = prise_en_charge
                st.success("✅ Tâche modifiée avec succès.")

# --- Onglet 7 : Suppression d'une tâche ---

elif onglet == "🗑️ Supprimer une tâche":
    st.title("🗑️ Supprimer une tâche")

    # Vérifier si des tâches sont présentes
    if df.empty:
        st.info("Aucune tâche à supprimer.")
    else:
        # Sélectionner une tâche à supprimer
        tache_a_supprimer = st.selectbox("Sélectionne la tâche à supprimer :", df["Nom de tâche"])

        # Ajouter un bouton de suppression
        if st.button(f"Supprimer la tâche : {tache_a_supprimer}"):
            # Supprimer la tâche de la DataFrame
            df = df[df["Nom de tâche"] != tache_a_supprimer]
            st.session_state.df = df  # Mettre à jour la session avec les nouvelles données
            # Sauvegarder la DataFrame mise à jour dans le fichier
            df.to_csv(lien_sauvegarde, index=False)  # Sauvegarde des modifications
            st.success(f"Tâche '{tache_a_supprimer}' supprimée avec succès!")

        # Afficher la liste mise à jour après suppression
        st.write("Tâches restantes après suppression :")
        st.dataframe(df)
# --- Onglet 6 : Suivi du budget ---
elif onglet == "💰 Budget":
    st.title("💰 Suivi du budget")
    if "Budget prévu" in df.columns and "Budget utilisé" in df.columns:
        st.dataframe(df[["Nom de tâche", "Budget prévu", "Budget utilisé", "Inclus dans budget", "Pris en charge par"]])
    else:
        st.warning("Colonnes de budget manquantes.")

st.sidebar.markdown("---")
if st.sidebar.button("💾 Sauvegarder les modifications"):
    try:
        # Sauvegarde dans le fichier Excel
        df.to_excel(lien_sauvegarde, index=False, engine='openpyxl')

        st.sidebar.success(f"Fichier enregistré dans : `{lien_sauvegarde}`")
    except Exception as e:
        st.sidebar.error(f"Erreur lors de l'enregistrement : {e}")

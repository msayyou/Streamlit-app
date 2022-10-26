import joblib
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
import pandas as pd
import shap
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
import streamlit as st

st.title('Implémentez un modèle de scoring')

st.sidebar.header("Les paramètres des clinets")


def client_parameters_enter():
    CODE_GENDER = st.sidebar.selectbox('CODE_GENDER', ('M', 'F'))
    EMERGENCYSTATE_MODE = st.sidebar.selectbox('EMERGENCYSTATE_MODE', ('No', 'Yes'))
    OCCUPATION_TYPE = st.sidebar.selectbox('OCCUPATION_TYPE',
                                           ('Cleaning staff', 'Cooking staff', 'Core staff', 'Drivers',
                                            'HR staff', 'High skill tech staff', 'IT staff',
                                            'Laborers', 'Low-skill Laborers', 'Managers',
                                            'Medicine staff ', 'Private service staff',
                                            'Realty agents', 'Sales staff',
                                            'Secretaries', 'Security staff', 'Waiters/barmen staff'))
    WALLSMATERIAL_MODE = st.sidebar.selectbox('WALLSMATERIAL_MODE', ('Mixed', 'Monolithic', 'Others',
                                                                     'Panel ', 'Stone, brick', 'Wooden'))
    EXT_SOURCE_3 = st.sidebar.slider('EXT_SOURCE_3', 0.00, 1.00, 0.01)
    REGION_RATING_CLIENT = st.sidebar.slider('REGION_RATING_CLIENT', 1, 3, 1)
    AMT_GOODS_PRICE = st.sidebar.slider('AMT_GOODS_PRICE', 4500, 35000, 10000)
    GOODS_PRICE_CREDIT_PER = st.sidebar.slider('GOODS_PRICE_CREDIT_PER', 0.384615, 4.666667, 0.124305)
    DAYS_WORKING_PER = st.sidebar.slider('DAYS_WORKING_PER', -37.743412, 0.717426, 0.022656)
    ANNUITY_DAYS_BIRTH_PERC = st.sidebar.slider('ANNUITY_DAYS_BIRTH_PERC', -8.088154, -0.054627, 0.5)

    data = {'CODE_GENDER': CODE_GENDER, 'EXT_SOURCE_3': EXT_SOURCE_3, 'EMERGENCYSTATE_MODE': EMERGENCYSTATE_MODE,
            'OCCUPATION_TYPE': OCCUPATION_TYPE, 'WALLSMATERIAL_MODE': WALLSMATERIAL_MODE,
            'REGION_RATING_CLIENT': REGION_RATING_CLIENT, 'AMT_GOODS_PRICE': AMT_GOODS_PRICE,
            'GOODS_PRICE_CREDIT_PER': GOODS_PRICE_CREDIT_PER, 'DAYS_WORKING_PER': DAYS_WORKING_PER,
            'ANNUITY_DAYS_BIRTH_PERC': ANNUITY_DAYS_BIRTH_PERC}

    client_parameters = pd.DataFrame(data, index=[0])
    return client_parameters


input_df = client_parameters_enter()

st.header('Le déploiement')

df = pd.read_csv('data_model.csv')
df.drop('Unnamed: 0', axis=1, inplace=True)

donnee_entree = pd.concat([input_df, df], axis=0)


var_cat = ['CODE_GENDER', 'EMERGENCYSTATE_MODE', 'OCCUPATION_TYPE', 'WALLSMATERIAL_MODE']

for col in var_cat:
    dummy = pd.get_dummies(donnee_entree[col], drop_first=True)
    donnee_entree = pd.concat([dummy, donnee_entree], axis=1)
    del donnee_entree[col]

# prendre uniquement la premiere ligne
donnee_entree = donnee_entree.fillna(donnee_entree.mode())
donnee_entree = donnee_entree[:1]

tableau_prevision = donnee_entree.drop(['TARGET'], axis=1)
X = donnee_entree.drop(['TARGET'], axis=1)
y = donnee_entree['TARGET']

st.subheader('Les nouveaux parametres')
st.write(tableau_prevision)

# importer le modèle
model = joblib.load('predict_loan_GBC.pkl')

# appliquer le modèle sur le profil d'entrée
prevision = model.predict(tableau_prevision)
prevision_proba = model.predict_proba(tableau_prevision)

st.subheader('Résultat de la prévision')
st.write(y[prevision])

st.subheader('prediction probability')
st.write(prevision_proba)

prediction = model.predict(tableau_prevision)

if st.button("Predict"):
    prediction = model.predict(tableau_prevision)
    if prediction[0] < 0.5:
        st.success('Le demandeur a une forte probabilité de rembourser le prêt !')
    else:
        st.error('Le demandeur a un risque élevé de ne pas rembourser le prêt')

st.title("SHAP in Streamlit")

st.set_option('deprecation.showPyplotGlobalUse', False)
st.subheader('Interprétabilité des résultats - Niveau candidat')
shap.initjs()
explainer = shap.Explainer(model)
shap_values = explainer(X)
fig = shap.plots.bar(shap_values[0])
st.pyplot(fig)

import streamlit.components.v1 as components
st.components.v1.iframe("https://explanair-dashboard.herokuapp.com/dashboard", width=None, height=1500, scrolling=True)

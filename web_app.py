# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 14:30:44 2025

@author: jmich
"""

import ast
import os
import streamlit as st
import pandas as pd
#import plotly.express as px
#from registr_scraping import vytvor_adresar


def multiply_czk_amount(amount_text, multiplier):
    """
    Vyčte z textu částku a pronásobenou multiplier ji vrátí.
    """
    amount_numeric = float(amount_text.replace(" ", "").replace("CZK", "").replace(",", "."))

    result = amount_numeric * multiplier
    return result

def change_currency_format(amount_text):
    """
    Vyčte z textu částku a tu vrátí.
    """
    amount_numeric = float(amount_text.replace(" ", "").replace("CZK", "").replace(",", "."))
    return amount_numeric

def format_float_to_czk(text):
    """
    Převede částku na text a výsledek vrátí.
    """
    return f"{text:,.2f}".replace(",", " ").replace(".", ",") + " CZK"

if __name__ == "__main__":
    # Titulek aplikace
    st.title("Pomocník pro obchodní zástupce")

    st.write("Toto je nástroj, který čerpá data z registru smluv a usnadňuje tvou práci.")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    st.subheader("Koukněte se na zakázky, který odběratel uskutečnil.")
    st.write("Zobrazená data se mohou mírně lišit od smluv - to je způsobeno \
             kvalitou zpracovávaných dokumentů a halucinací jazykových modelů. \
             Proto berte data jako informační a pro přesné informace klikněte\
            na odkaz dané smlouvy.")
    current_directory = os.getcwd()
    tabulky_path = os.path.join(current_directory,"stažené_tabulky")
    #vytvor_adresar(tabulky_path)

    tabulky_path = os.path.join(tabulky_path,"Data_vsechny.csv")

    if tabulky_path:
        data = pd.read_csv(tabulky_path)
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]

        # Výběr odběratele
        customers = data['Odběratel'].unique()
        selected_customer = st.selectbox("Vyberte odběratele:", customers)

        # Filtrace dat pro vybraného odběratele
        customer_data = data[data['Odběratel'] == selected_customer]

        # Seřazení podle data uzavření smlouvy od nejnovějšího po nejstarší
        customer_data['Datum uzavření smlouvy'] = pd.to_datetime(customer_data\
                            ['Datum uzavření smlouvy'], format="%d.%m.%Y")
        customer_data = customer_data.sort_values(by='Datum uzavření smlouvy', ascending=False)

        # Skupina podle zakázky (contract_id)
        contracts = customer_data['ID'].unique()

        st.write(f"Seznam zakázek pro odběratele: {selected_customer}")
        # Iterace přes jednotlivé zakázky
        for contract_id in contracts:
            st.write(" ")
            st.write(" ")
            contract_data = customer_data[customer_data['ID'] == contract_id]
            supplier = contract_data['Dodavatel'].iloc[0]
            contract_date = contract_data['Datum uzavření smlouvy'].iloc[0]
            contract_value_with_DPH = contract_data['Cena_s_dph'].iloc[0]
            contract_value_without_DPH = contract_data['Cena_bez_dph'].iloc[0]
            predmet_smlouvy = contract_data['Předmět smlouvy'].iloc[0]
            id_verze = contract_data['ID verze'].iloc[0]

            st.subheader(f"Zakázka ID: {contract_id}")
            URL = "https://smlouvy.gov.cz/smlouva/" + str(id_verze)
            st.write(f"Klikněte na odkaz smlouvy: {URL}")
            st.write(f"**Dodavatel:** {supplier}")
            st.write(f"**Datum uzavření smlouvy:** {contract_date.date()}")
            st.write(f"**Hodnota smlouvy bez DPH:** {contract_value_without_DPH} Kč")
            st.write(f"**Hodnota smlouvy vč. DPH:** {contract_value_with_DPH} Kč")
            st.write(f"**Předmět smlouvy:** {predmet_smlouvy} Kč")

            # Tabulka zboží pro danou zakázku
            products_table_data_list = contract_data['zboží'].copy().to_list()
            nazev_list = []
            mnozstvi_list = []
            cena_bez_DPH_list = []
            cena_s_DPH_list = []
            for slovnik in ast.literal_eval(products_table_data_list[0]):
                #print(slovnik)
                nazev_list.append(slovnik['název'])
                if 'množství' in slovnik:
                    mnozstvi_list.append(slovnik['množství'])
                elif 'množstí' in slovnik:
                    mnozstvi_list.append(slovnik['množstí'])
                cena_bez_DPH_list.append(slovnik['cena bez DPH'])
                if 'cena s dph' in slovnik:
                    cena_s_DPH_list.append(slovnik['cena s dph'])
                elif 'cena s DPH' in slovnik:
                    cena_s_DPH_list.append(slovnik['cena s DPH'])
                else:
                    print("Problém se slovníkem")
            tabulka_data = {
                "Název": nazev_list,
                "Množství": mnozstvi_list,
                "Cena bez DPH": cena_bez_DPH_list,
                "Cena s DPH": cena_s_DPH_list
                }
            tabulka_df = pd.DataFrame(tabulka_data)

            st.write("*Tabulka zboží:*")
            st.table(tabulka_df)

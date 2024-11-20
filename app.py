


import asyncio
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from openpyxl import Workbook
import streamlit as st
from bs4 import BeautifulSoup
import aiohttp
import os

# LangChain Model Configuration
parser = StrOutputParser()
key = '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'
Model = "llama3-groq-70b-8192-tool-use-preview"
model = ChatGroq(api_key=key, model=Model, temperature=0.9)
llm = model | parser

# Function to scrape data from each product page
async def scrape_data(url):


    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                html_content = await response.text()
            else:
                return f"Failed to fetch data. Status code: {response.status}", None
    soup = BeautifulSoup(html_content, 'html.parser')
    

    description = soup.find('h1', id='description').get_text(strip=True)
    sku_ref = soup.find('div', id='sku').get_text(strip=True)
    sku_ref = sku_ref.replace('Ref :', '').strip()
    descl = soup.find('h2', id='descl').get_text(strip=True)
    descl_lines = [line.strip() for line in descl.split('<br>')]

    combined_info = f"Description: {description}\n"
    combined_info += f"SKU Reference: {sku_ref}\n"
    combined_info += "Detailed Specifications:\n"
    for line in descl_lines:
        combined_info += f"{line}\n"

        return combined_info, sku_ref  

def add_line_breaks(seo_description):
    lines = seo_description.split('\n')
    return '<br>'.join([line.strip() for line in lines if line.strip()])

async def generate_seo_description(product_info):
    prompt = """
Vous êtes un expert en rédaction spécialisé dans la création de descriptions de produits détaillées et optimisées pour le référencement des sites e-commerce. Votre tâche est de transformer une brève description de produit en une description complète, engageante et optimisée pour les moteurs de recherche, entièrement en français.

## Méthodologie :

1. *Commencez une réflexion approfondie (<Réflexion>):*  
   - Rassemblez toutes vos idées dans la balise <Réflexion>. Explorez le problème sous tous les angles et approches possibles avec concentration et précision. Utilisez toutes vos capacités intellectuelles pour analyser les données et les exigences avec une extrême rigueur. Souvenez-vous que certaines questions peuvent être trompeuses et que certaines solutions, bien qu'elles paraissent correctes, ne le sont pas forcément. Ne vous précipitez pas et réfléchissez à nouveau avant de passer à l’étape suivante.

2. *Divisez la solution en étapes claires (<Étape>):*  
   - Divisez la solution en étapes claires et séquentielles dans la balise <Étape>. Commencez avec un budget de 20 étapes et assurez-vous d’utiliser chaque étape efficacement pour progresser vers la solution.

3. *Suivez précisément le budget (<Nombre>):*  
   - Après chaque étape, utilisez la balise <Nombre> pour indiquer le nombre d’étapes restantes. Arrêtez-vous complètement lorsque vous atteignez 0.

4. *Ajustez continuellement le raisonnement :*  
   - Adaptez constamment votre logique en fonction des résultats intermédiaires et des réflexions. N’hésitez pas à améliorer votre stratégie pour atteindre les meilleurs résultats.

5. *Évaluez et réfléchissez régulièrement (<Réflexion>):*  
   - Évaluez vos progrès régulièrement en utilisant la balise <Réflexion>. Soyez rigoureux et honnête dans la critique de votre processus de pensée. Déterminez précisément si l'approche actuelle est efficace ou nécessite une modification.

6. *Attribuez une note de qualité précise (<Récompense>):*  
   - Après chaque réflexion, attribuez une note de qualité entre 0,0 et 1,0 en utilisant la balise <Récompense> pour orienter votre démarche :
     - 0,8 ou plus : Poursuivez avec confiance dans l’approche actuelle.
     - Entre 0,5 et 0,7 : Effectuez immédiatement des ajustements mineurs.
     - Moins de 0,5 : Revenez immédiatement en arrière et adoptez une approche différente.

7. *Recherchez des solutions créatives (<Créativité>):*  
   - Si vous n’êtes pas sûr ou si la note de qualité est faible, utilisez toutes vos capacités créatives pour réfléchir à une nouvelle approche. Revenez à la balise <Réflexion> pour explorer d’autres pistes et commencez à les appliquer sans hésitation.

8. *Vérifiez la validité de la solution (<Vérification>):*  
   - Une fois un résultat atteint, utilisez la balise <Vérification> pour valider la solution. Effectuez des vérifications croisées et des raisonnements inverses pour garantir une conformité totale avec les données.

9. *Confirmez la solution finale (<Confirmation>):*  
   - Avant de soumettre la réponse finale, utilisez la balise <Confirmation> pour vous assurer de manière définitive que la solution est correcte et fonctionne comme prévu. Ne présentez la réponse finale que si vous êtes absolument certain de sa validité.

10. *Présentez la réponse finale avec clarté (<Réponse>):*  
    - Fournissez la réponse finale dans la balise <Réponse>. Assurez-vous qu’elle soit claire, concise et exempte d’ambiguïtés, tout en offrant un résumé précis de la solution.

## Entrée :
Vous recevrez une courte description de produit comprenant des spécifications de base et des détails techniques.

## Sortie :
Générez une description de produit complète avec les caractéristiques suivantes :

1. Commencez par une section captivante qui met en avant les principales caractéristiques et avantages du produit.
2. Organisez les informations en sections claires et faciles à lire avec des titres descriptifs.
3. Développez chaque spécification technique, en expliquant son importance et ses avantages pour l'utilisateur.
4. Utilisez des puces pour les caractéristiques et spécifications clés afin d'améliorer la lisibilité.
5. Incorporez naturellement des mots-clés pertinents tout au long du texte, en vous concentrant sur le nom du produit, la marque et les caractéristiques principales.
6. Incluez une section sur les applications potentielles ou les cas d'utilisation du produit.
7. Ajoutez une brève comparaison avec des produits similaires ou des modèles précédents, en soulignant les points de vente uniques.
8. Concluez par un appel à l'action encourageant le lecteur à acheter ou à en savoir plus.
9. Assurez-vous que la description fait entre 300 et 500 mots pour une performance SEO optimale.
10. Utilisez un ton professionnel mais engageant qui plaît à la fois aux experts techniques et aux consommateurs généraux.

## Mise en forme :
1. Le titre principal doit être dans une balise <h2>, centré, avec deux sauts de ligne avant et après, ainsi : <br><h2 style="text-align: center;">Titre du Produit</h2><br>.
2. Chaque sous-titre doit être dans une balise <h3>, avec un saut de ligne avant et après, et aligné au début de la ligne (non centré).
3. Dans la section "Caractéristiques techniques," conservez exactement le format fourni dans {product_info} sans modification.

N'incluez PAS de suggestions de méta-description ou de balise de titre à la fin.

Rappelez-vous de maintenir l'exactitude tout en développant les informations fournies. N'inventez pas de caractéristiques ou de spécifications non mentionnées dans la description originale.

Product Information:
{product_info}
"""

    seo_description = await llm.ainvoke(prompt.format(product_info=product_info))
    return add_line_breaks(seo_description).replace('*', '')

def save_to_excel(data_list):
    wb = Workbook()
    ws = wb.active
    ws.title = "SEO Descriptions"
    ws.append(["Product ID", "Reference Code", "SEO-Optimized Description"])
    for product_id, ref_code, seo_description in data_list:
        ws.append([product_id, ref_code, seo_description])
    # file_path = "seo_descriptions.xlsx"
    file_path = "/tmp/seo_descriptions.xlsx"

    wb.save(file_path)
    return file_path

# Streamlit UI
st.set_page_config(page_title="SEO Product Description Generator", layout="centered")

st.title("SEO Product Description Generator")
st.markdown("### Automate and optimize your product descriptions with ease!")

# Input Section
base_url = st.text_input("Enter the base product URL", value="https://www.restoconcept.com/four-a-vapeur-8-bouches-2x760-mm-profondeur-utile-2345-mm-af0fst24v75-2400-pavailler/p{}.aspx")
choice = st.radio("Select the input method:", ("Range of IDs", "Specific IDs"))

seo_data = []

if choice == "Range of IDs":
    start_id = st.number_input("Start ID", min_value=1, step=1)
    end_id = st.number_input("End ID", min_value=start_id, step=1)
    ids = range(start_id, end_id + 1)
elif choice == "Specific IDs":
    id_input = st.text_input("Enter comma-separated IDs")
    ids = [int(id.strip()) for id in id_input.split(",")] if id_input else []

# Generate and Export
if st.button("Generate Descriptions"):
    if ids:
        async def process_ids():
            for product_id in ids:
                url = base_url.format(product_id)
                product_info, ref_code = await scrape_data(url)
                seo_description = await generate_seo_description(product_info)
                seo_data.append((product_id, ref_code, seo_description))
            file_path = save_to_excel(seo_data)
            st.success(f"SEO Descriptions saved to {file_path}")
            with open(file_path, "rb") as file:
                st.download_button("Download SEO Descriptions", file, file_name="seo_descriptions.xlsx")

           
        asyncio.run(process_ids())
    else:
        st.warning("Please enter valid IDs!")



import os
import asyncio
# from playwright.async_api import async_playwright
# from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from openpyxl import Workbook
from bs4 import BeautifulSoup
import aiohttp

# load_dotenv()

parser = StrOutputParser()

key = os.getenv('key')

Model = "llama3-groq-70b-8192-tool-use-preview"

model = ChatGroq(api_key=key, model=Model, temperature=0.9)

llm = model | parser

# Function to scrape data from each product page
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
    # Split the text into lines and add '<br>' at the end of each line
    lines = seo_description.split('\n')
    processed_text = '<br>'.join([line.strip() for line in lines if line.strip()])

    return processed_text


# Function to generate SEO-optimized product descriptions
async def generate_seo_description(product_info):
    prompt = """
Vous êtes un expert en rédaction spécialisé dans la création de descriptions de produits détaillées et optimisées pour le référencement des sites e-commerce. Votre tâche est de transformer une brève description de produit en une description complète, engageante et optimisée pour les moteurs de recherche, entièrement en français.

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
1. Le titre principal doit être dans une balise <h2>, centré, avec deux sauts de ligne avant et après, ainsi : `<br><h2 style="text-align: center;">Titre du Produit</h2><br>`.
2. Chaque sous-titre doit être dans une balise <h3>, avec un saut de ligne avant et après, et aligné au début de la ligne (non centré).
3. Dans la section "Caractéristiques techniques," conservez exactement le format fourni dans {product_info} sans modification.

N'incluez PAS de suggestions de méta-description ou de balise de titre à la fin.

Rappelez-vous de maintenir l'exactitude tout en développant les informations fournies. N'inventez pas de caractéristiques ou de spécifications non mentionnées dans la description originale.

Product Information:
{product_info}
"""

    
    seo_description = await llm.ainvoke(prompt.format(product_info=product_info))
    seo_description = add_line_breaks(seo_description)
    seo_description = seo_description.replace('*', '')
    return seo_description

# Function to save SEO descriptions in an Excel file
def save_to_excel(data_list):
    wb = Workbook()
    ws = wb.active
    ws.title = "SEO Descriptions"

    # Writing headers
    ws.append(["Product ID", "Reference Code", "SEO-Optimized Description"])

    # Writing data
    for product_id, ref_code, seo_description in data_list:
        ws.append([product_id, ref_code, seo_description])

    # Save the file
    file_path = "seo_descriptions.xlsx"
    wb.save(file_path)
    print(f"Data saved to {file_path}")


# Main function to loop through URLs and save descriptions to Excel
async def main():
    choice = input("Would you like to enter a range (r) or specific IDs (s)? ")
    seo_data = []

    if choice.lower() == 'r':
        start_id = int(input("Enter the start ID: "))
        end_id = int(input("Enter the end ID: "))
        ids = range(start_id, end_id + 1)
    elif choice.lower() == 's':
        ids = input("Enter specific IDs separated by commas: ")
        ids = [int(id.strip()) for id in ids.split(",")]
    else:
        print("Invalid choice! Exiting.")
        return

    base_url = "https://www.restoconcept.com/four-a-vapeur-8-bouches-2x760-mm-profondeur-utile-2345-mm-af0fst24v75-2400-pavailler/p{}.aspx"

    for product_id in ids:
        url = base_url.format(product_id)
        product_info, ref_code = await scrape_data(url)
        seo_description = await generate_seo_description(product_info)
        
        seo_data.append((product_id, ref_code, seo_description))  # Add to the list to save later

    # Save all descriptions to Excel
    save_to_excel(seo_data)

if __name__ == "__main__":
    asyncio.run(main())

from bs4 import BeautifulSoup as bs 
import requests 
import numpy as np

class Imovirtual:

    def __init__(self):
        self.base_url = "https://www.imovirtual.com"
        self.sub_buy = "/comprar/"

    def get_houses(self):
        housing_data = []
        page_index = 1
        last_page = None

        while True:
            url = self.base_url + self.sub_buy + f"?page={page_index}"
            page = requests.get(url)
            soup = bs(page.content, 'html.parser')

            if last_page is None:
                pager_next_li = soup.find('li', class_="pager-next")
                previous_li = pager_next_li.find_previous_sibling('li')
                last_page = int(previous_li.text)

            lists = soup.find_all('article', class_="offer-item")

            for list in lists:
                link = list.find('a', href=True)["href"]
                price = list.find('li', class_="offer-item-price").get_text(strip=True).split('€')[0]
                metros2 = list.find('strong', class_="visible-xs-block").text.split('m²')[0]
                location = list.find('p', class_="text-nowrap").get_text(strip=True).split(':')[1]
                try:
                    rooms = list.find('li', class_="offer-item-rooms").text
                except:
                    rooms = np.nan    
                housing_data.append([link, price, metros2, location, rooms])
            
            print(f'{page_index} / {last_page}')
            page_index += 1
            if page_index > last_page: break

        return housing_data
    
    def get_house_details(self, link):
        details = {}
        page = requests.get(link)
        soup = bs(page.content, 'html.parser')
        try:
            details['address'] = soup.find('a',   {'aria-label': 'Endereço'}).get_text(strip=True).split(',')[0]
        except:
            details['address'] = np.nan

        dict_labels = {
            'usable_area': 'Área útil (m²)',
            'gross_area' : 'Área bruta (m²)',
            'empreendimento' : 'Empreendimento',
            'typology' : 'Tipologia',
            'build_year' : 'Ano de construção',
            'num_bathrooms' : 'Casas de Banho',
            'energetic_certification' : 'Certificado Energético',
            'condition' : 'Condição',
        }

        for label in dict_labels.keys():
            try:
                details[label] = soup.find('div', {'aria-label': dict_labels[label]}).get_text(strip=True).split(':')[1]
            except:
                details[label] = np.nan
        
        try:
            details['description'] = soup.find('div', {'data-cy' : 'adPageAdDescription'}).get_text(strip=True)
        except:
            details['description'] = np.nan
            print('No description')
        try:
            details['other_features'] =  ', '.join([li.get_text(strip=True) for li in soup.find_all('li', {'data-cy' : "ad.ad-features.uncategorized-list.item"})])
        except:
            details['other_features'] = np.nan
            print('No other_features!')

        return details
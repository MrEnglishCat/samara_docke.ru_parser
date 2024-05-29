import pprint
from wsgiref import headers

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class SamaraDockeParser:
    RESULT = {}
    BASE_URL = 'https://samara.docke.ru'
    URL_LIST = ['https://samara.docke.ru/siding/lux/korabelny-brus-d5d/orekh/']
    CLASTER_LINKS = []
    HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'User-Agent': UserAgent().random
    }
    TASKS = []

    def request(self, url, headers, ):
        return requests.get(url, headers=headers).content

    def get_soup(self, response, parser='html.parser'):
        return BeautifulSoup(response, features=parser)

    def get_clasters(self):
        soup = BeautifulSoup(requests.get(self.BASE_URL, headers=self.HEADERS).content, 'html.parser')
        # for item in soup.find('nav', class_='popup-menu popup-menu--products').find_all('a'):
        for item in soup.find('nav', class_='popup-menu popup-menu--products').find_all('a', class_='is-bold'):
            print(self.BASE_URL + item['href'])
            self.CLASTER_LINKS.append(self.BASE_URL + item['href'])

    def get_groups(self):


    def get_all_urls(self):
        pass

    def get_data_from_page(self, soup):
        pass

    def get_tasks(self):
        pass

    def run(self):
        asyncio.run(
            self.get_tasks()
        )

        response = requests.get(url, headers=headers).content
        soup = BeautifulSoup(response, 'html.parser')
        categpry_name_1_5 = soup.find('nav', class_='breadcrumbs container')
        link_names = categpry_name_1_5.find_all('a')
        last_category_name = categpry_name_1_5.find_all('span')[-1]
        article = soup.find('div', class_='product-detail__articul').text.split(':')[-1].strip()
        item_name = soup.find('h1', class_='product-heading').text
        price_value = soup.find('span', class_='product-price__value').text
        price_data = soup.find('span', class_='product-price__text').text
        image_url = soup.find('div', class_='product-img__items').find('a')['href']

        all_characteristics = soup.find('div', class_='product-blocks__item').find('div',
                                                                                   class_='characteristics').find_all(
            class_='characteristics__item')
        # all_characteristics = soup.find('div', class_='product-blocks__item')
        all_characteristics_data = {}
        for item in all_characteristics:
            if item is not None:
                i_name = item.find('div', class_='characteristics__name')
                i_value = item.find('div', class_='characteristics__value')
                if i_name is not None and i_value is not None:
                    i_name = i_name.text
                    i_value = i_value.text
                    all_characteristics_data.update(
                        {
                            i_name: i_value
                        }
                    )

        result.update(
            {
                'url': url,
                'категория 1': link_names[0].text,
                'категория 2': link_names[1].text,
                'категория 3': link_names[2].text,
                'категория 4': link_names[3].text,
                'категория 5': last_category_name.text,
                'артикул': article,
                'Наименование товара': item_name,
                'цена': price_value,
                'Ед изм': price_data,
                'image_url': BASE_URL + image_url,
                'характеристики': all_characteristics_data
            }
        )

        pprint.pprint(result)

        #
        # with open('result.pdf', 'wb') as f:
        #     f.write(requests.get('https://www.docke.ru/upload/iblock/3e2/vd72hvtmv90rg8bs5thx49ne3lomr2zn/IM-LCH_GCH-2024-WEB-_ot-17.05_.pdf', headers=headers).content)


samara_parser = SamaraDockeParser()
samara_parser.get_clasters()
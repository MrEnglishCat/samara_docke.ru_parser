import asyncio

import aiohttp
import requests
from pprint import pprint
from wsgiref import headers
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class SamaraDockeParser:
    RESULT = {}
    BASE_URL = 'https://samara.docke.ru'
    URL_LIST = ['https://samara.docke.ru/siding/lux/korabelny-brus-d5d/orekh/']
    LINKS = {}
    HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'User-Agent': UserAgent().random
    }
    TASKS = []

    async def get_soup(self, session, url, headers):
        async with session.get(url, headers=headers) as response:
            return BeautifulSoup(await response.content, 'html.parser')

    def get_clasters(self):
        soup = BeautifulSoup(requests.get(self.BASE_URL, headers=self.HEADERS).content, 'html.parser')
        # for item in soup.find('nav', class_='popup-menu popup-menu--products').find_all('a'):
        for item in soup.find('nav', class_='popup-menu popup-menu--products').find_all('a', class_='is-bold'):
            self.LINKS.setdefault(self.BASE_URL + item['href'], [])

    async def get_series(self, session, claster_url):
        result_urls = []
        # soup = await self.get_soup(session, claster_url, self.HEADERS)
        async with session.get(claster_url, headers=self.HEADERS) as response:
            soup =  BeautifulSoup(await response.read(), 'html.parser')
            for url in soup.find('div', class_='cards-slider').find_all('a', class_='series-card'):
                result_urls.append(
                    self.BASE_URL + url.get('href')
                )
            # print(len(result_urls), result_urls)
            return result_urls

    async def get_collections(self, session, series_url):
        result_urls = []

        # soup = await self.get_soup(session, series_url, self.HEADERS)
        async with session.get(series_url, headers=self.HEADERS) as response:
            soup = BeautifulSoup(await response.read(), 'html.parser')
        for url in soup.find('div', class_='cards-slider').find_all('a', class_='series-card'):
            result_urls.append(
                self.BASE_URL + url.get('href')
            )
        # print(len(result_urls), result_urls)
        return result_urls

    async def get_goods_urls(self, session, goods_url):
        goods_urls = []
        # soup = await self.get_soup(session, goods_url, self.HEADERS)
        async with session.get(goods_url, headers=self.HEADERS) as response:
            soup = BeautifulSoup(await response.read(), 'html.parser')
        for url in soup.find('div', class_='products-tile').find_all('a', class_='product-card__name'):
            goods_urls.append(
                goods_url[:-1] + url.get('href')
            )
        return goods_urls

    async def get_all_urls(self, session, url):
        series_url = await self.get_series(session, url)
        for s_url in series_url:
            try:
                collection_urls = await self.get_collections(session, s_url)
                for c_url in collection_urls:
                    goods_urls = await self.get_goods_urls(session, c_url)
                    self.LINKS[url].extend(goods_urls)
            except Exception as e:
                goods_urls = await self.get_goods_urls(session, s_url)
                self.LINKS[url].extend(goods_urls)

        pprint(self.LINKS)

    def get_data_from_page_facades(self, soup):
        pass

    def get_data_from_page_roofs(self, soup):
        pass

    def get_data_from_page_vodostoki(self, soup):
        pass

    async def get_tasks(self):
        samara_parser.get_clasters()
        print(self.LINKS)
        async with aiohttp.ClientSession(trust_env=True) as session:
            for url in self.LINKS.keys():
                self.TASKS.append(asyncio.create_task(self.get_all_urls(session, url)))

            await asyncio.gather(*self.TASKS)

    def run(self):
        asyncio.run(
            self.get_tasks()
        )

    def a(self):
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
samara_parser.run()

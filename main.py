import asyncio
import json
import os.path

import aiohttp
import requests
from pprint import pprint
from wsgiref import headers
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class SamaraDockeParser:
    RESULT = []
    ERRORS = {}
    BASE_URL = 'https://samara.docke.ru'
    # URL_LIST = ['https://samara.docke.ru/siding/lux/korabelny-brus-d5d/orekh/']
    LINKS = {}
    HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'User-Agent': UserAgent().random
    }
    TASKS = []

    @staticmethod
    def check_dir_files(path, filename=None, isfile=False):
        if not os.path.exists(path):
            os.makedirs(path)
        if isfile:
            return os.path.isfile(f"{path}/{filename}")

    @staticmethod
    def write_file(path, filename, data, isjson=False):
        full_path = f"{path}/{filename}"
        __class__.check_dir_files(path, filename)

        with open(full_path, 'w', encoding='utf-8') as f:
            if isjson:
                json.dump(data, f, ensure_ascii=False, indent=3)
            else:
                pass

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
            soup = BeautifulSoup(await response.read(), 'html.parser')
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
                url.get('href')
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
                # goods_url[:-1] + url.get('href')
                self.BASE_URL + url.get('href')
            )
        return goods_urls

    async def get_all_urls(self, session, url):
        series_url = await self.get_series(session, url)

        for s_url in series_url:
            print(f"[WARNING] Обработка серии {s_url}")
            try:
                collection_urls = await self.get_collections(session, s_url)
                for c_url in collection_urls:
                    goods_urls = await self.get_goods_urls(session, c_url)
                    self.LINKS[url].extend(goods_urls)
            except Exception as e:
                goods_urls = await self.get_goods_urls(session, s_url)
                self.LINKS[url].extend(goods_urls)
            for g_url in goods_urls:
                if 'facades' in url:
                    await self.get_data_from_page_facades(session, g_url)
                elif 'roofs' in url:
                    await self.get_data_from_page_roofs(session, g_url)
                else:
                    await self.get_data_from_page_vodostoki(session, g_url)
                print(f"[INFO] URLs: {g_url} обработана.")
                # break
            # break


    async def parsing_data_from_page(self,session, url):
        async with session.get(url, headers=self.HEADERS) as response:
            soup = BeautifulSoup(await response.read(), 'html.parser')
            self.parsing_data_from_page(soup, url)

            if (a := soup.find('div', class_='page-404 container')):
                self.RESULT.append(
                    {
                        url: a.text
                    }
                )
                print(f"[ERROR] {url}, page not found!")
                self.ERRORS.setdefault(url, '[ERROR] {url}, page not found!')
                return
            elif (a:= soup.find('pre')):
                error_description = a.text
                print(f"[ERROR] {url}, Goods data not found! ([TypeError] - CODE ERROR on web-page)")
                self.ERRORS.setdefault(url, "[ERROR] {url}, Goods data not found! ([TypeError] - CODE ERROR on web-page)")
            try:
                categpry_name_1_5 = soup.find('nav', class_='breadcrumbs container')
                link_names = categpry_name_1_5.find_all('a')
                print('===', len(link_names))
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
                            i_name = i_name.text.strip()
                            i_value = i_value.text.strip()
                            if i_name in all_characteristics_data:
                                all_characteristics_data[i_name].append(i_value)
                            else:
                                all_characteristics_data.update(
                                    {
                                        i_name: [i_value]
                                    }
                                )

                documents_links = [item.get('href') for item in soup.find('div', class_='documents').find_all('a')]

                self.RESULT.append(
                    {
                        'url': url,
                        'категория 1': link_names[0].text,
                        'категория 2': link_names[1].text,
                        'категория 3': link_names[2].text,
                        'категория 4': link_names[3].text if len(link_names) == 4 else None,
                        'категория 5': last_category_name.text,
                        'артикул': article,
                        'Наименование товара': item_name,
                        'цена': price_value,
                        'Ед изм': price_data,
                        'image_url': self.BASE_URL + image_url,
                        'характеристики': all_characteristics_data,
                        'ссылки на документы': documents_links,
                    }
                )


            #
            # with open('result.pdf', 'wb') as f:
            #     f.write(requests.get('https://www.docke.ru/upload/iblock/3e2/vd72hvtmv90rg8bs5thx49ne3lomr2zn/IM-LCH_GCH-2024-WEB-_ot-17.05_.pdf', headers=headers).content)
            except Exception as e:
                print(f"[ERROR] Ошибка поиска данных со страницы {url}")
                self.ERRORS.setdefault(url, '[ERROR] Ошибка поиска данных со страницы')

    async def get_data_from_page_facades(self, session, url):
        await self.parsing_data_from_page(session, url)

    async def get_data_from_page_roofs(self, session, url):
        await self.parsing_data_from_page(session, url)

    async def get_data_from_page_vodostoki(self, session, url):
        await self.parsing_data_from_page(session, url)

    async def get_tasks(self):
        samara_parser.get_clasters()
        print(f'[INFO] Собрано ссылок кластеров: {len(samara_parser.LINKS)}')
        async with aiohttp.ClientSession(trust_env=True) as session:
            for url in self.LINKS.keys():
                self.TASKS.append(asyncio.create_task(self.get_all_urls(session, url)))

            await asyncio.gather(*self.TASKS)
        self.write_file('data', 'errors_json.json', self.ERRORS, isjson=True)
        self.write_file('data', 'result_json.json', self.RESULT, isjson=True)

    def run(self):
        asyncio.run(
            self.get_tasks()
        )


samara_parser = SamaraDockeParser()
samara_parser.run()

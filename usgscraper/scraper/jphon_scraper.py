import asyncio
import aiohttp
import pydantic
from functools import reduce
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional, Union, Callable, Awaitable, Any
from usgscraper.json_downloader import JPhonJSONDownloader


class JPhonInfo(pydantic.BaseModel):
    """
    The JPhonInfo object keeps track of an item in inventory, including title, published date, authors, doi and href.
    """

    title: str
    published_date: str
    authors: list
    doi: str
    href: str
    keywords: Any
    abstract: Any

    @pydantic.validator("authors")
    @classmethod
    def is_author(cls, author) -> str:
        """The is_author method makes sure there is author value definied."""

        def extract_author(value):
            auth_id = value["id"]
            full_name = f'{value["givenName"]} {value["surname"]}'
            return {auth_id: full_name}

        return list(map(extract_author, author))
    
    @pydantic.validator("keywords", 'abstract')
    @classmethod
    def check_content(cls, value):
        """The check_content method makes sure there is keyword or abstract value definied"""
        output = asyncio.run(value)
        if output == None:
            return None
        return output
    

@dataclass
class JPhon:
    """
    The JPhon object extracts and cleans the JSON data from Jouranl of Phonetics.
    """

    volume: int
    headers: dict
    issue: Optional[int] = None

    async def download_multiple(self) -> Callable[[], Awaitable[list]]:
        """The download_multiple method downloads multiple JSON data.

        Returns:
            an awaitable list
        """
        return await asyncio.gather(
            *[
                JPhonJSONDownloader(
                    self.volume, issue=issue, headers=self.headers
                ).download()
                for issue in range(1, 7)
            ]
        )

    @property
    def json_data(self) -> list[dict[str, Union[str, list]]]:
        """The json_data property set the JSON data based on the volume and issue number.

        Returns:
            a list
        """
        if self.volume < 42 and self.issue is None:
            data_collection = asyncio.run(self.download_multiple())
            return reduce(lambda x, y: x + y, data_collection)
        return asyncio.run(
            JPhonJSONDownloader(
                self.volume, issue=self.issue, headers=self.headers
            ).download()
        )

    async def get_keywords(self, soup: BeautifulSoup) -> list[str]:
        """The get_keywords method gets the keywords as a list from a soup object

        Args:
            soup (BeautifulSoup): the soup object

        Returns:
            a list
        """
        keyword_html = soup.find(class_="keywords-section") 
        if keyword_html:
            return [keyword.text for keyword in keyword_html][1:] 
 
    async def get_abstract(self, soup: BeautifulSoup) -> str:
        """The get_abstract method gets the abstract as a str from a soup object

        Args:
            soup (BeautifulSoup): the soup object

        Returns:
            a str
        """
        abstract_html = soup.find(id='abstracts') 
        if abstract_html:
            abstract = re.search('(?<=Abstract).*', abstract_html.text).group()
            return abstract 

    async def get_soup(self, href: str) -> BeautifulSoup:
        """THe get_soup method gets the soup object from href

        Args:
            href (str): the link to a paper

        Returns:
            a BeautifulSoup object
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(href) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "lxml")
                return soup
            
    async def clean_data(self, json_data: dict) -> dict[str, Union[str, list]]:
        """The clean_data method cleans the JSON data from the class property `self.json_data`.

        Args:
            json_data (dict): paper info

        Returns:
            a dict: {
                'title': 'Spectral differences in /ai/ offsets conditioned by voicing of the following consonant',
                'published_date': 'January 2000',
                'authors': [{'auth-0': 'Erik R. Thomas'}],
                'doi': '10.1006/jpho.2000.0103',
                'href': 'https://www.sciencedirect.com/science/article/pii/S0095447000901037'},
            }
        """
        title = json_data["title"]
        doi = json_data["doi"]
        href = f'https://www.sciencedirect.com{json_data["href"]}'
        published_date = json_data["coverDateText"]
        authors = json_data["authors"]
        article_info = JPhonInfo(
            title=title,
            published_date=published_date,
            authors=authors,
            doi=doi,
            href=href,
            keywords=asyncio.run(self.get_keywords(href)),
        )
        return article_info.dict()

    def extract_data(self) -> map:
        """The extract_data method extracts the JSON data from the class property `self.json_data`.

        Returns:
            a map object
        """
        tasks = map(self.clean_data, self.json_data)
        return asyncio.run(asyncio.gather(*tasks)) 

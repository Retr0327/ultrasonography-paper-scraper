import asyncio
import pydantic
from functools import reduce
from dataclasses import dataclass
from typing import Optional, Union, Callable, Awaitable
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

    @pydantic.validator("href")
    @classmethod
    def is_href(cls, link) -> str:
        """The is_href method makes sure there is href value definied."""
        if not link:
            return "no link"
        return f"https://www.sciencedirect.com{link}"

    @pydantic.validator("authors")
    @classmethod
    def is_author(cls, author) -> str:
        """The is_author method makes sure there is authors value definied."""

        def extract_author(value):
            auth_id = value["id"]
            full_name = f'{value["givenName"]} {value["surname"]}'
            return {auth_id: full_name}

        return list(map(extract_author, author))


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

    def clean_data(self, json_data: dict) -> dict[str, Union[str, list]]:
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
        href = json_data["href"]
        published_date = json_data["coverDateText"]
        authors = json_data["authors"]
        article_info = JPhonInfo(
            title=title,
            published_date=published_date,
            authors=authors,
            doi=doi,
            href=href,
        )
        return article_info.dict()

    def extract_data(self) -> map[dict[str, Union[str, list]]]:
        """The extract_data method extracts the JSON data from the class property `self.json_data`.

        Returns:
            a map object
        """
        data = map(self.clean_data, self.json_data)
        return data

import re
import asyncio
import aiohttp
import pydantic
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Literal, Optional, Union, Any
from usgscraper.downloader import JASADownloader


class JASAInfo(pydantic.BaseModel):
    """
    The JASAInfo object keeps track of an item in inventory, including title, published date, and authors.
    """

    title: str
    published_date: Any
    authors: Any
    # href: Any
    # abstract: Any

    @pydantic.validator("authors")
    @classmethod
    def is_author(cls, value) -> Union[dict[str, str], str]:
        """The is_author method makes sure there is author value definied."""
        authors = asyncio.run(value)

        def create_author_info(authors):
            key = [f"auth-{author+1}" for author in range(len(authors))]
            return dict(zip(key, authors))

        if isinstance(authors, str):
            return authors
        return create_author_info(authors)

    @pydantic.validator("published_date")
    @classmethod
    def check_content(cls, value) -> Union[str, Literal['None']]:
        """The check_content method makes sure there is published_date value definied"""
        output = asyncio.run(value)
        if output == None:
            return "None"
        return output

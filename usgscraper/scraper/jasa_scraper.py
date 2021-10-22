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
    published_date: str  
    authors: Union[list, str]  
    href: str  

    @pydantic.validator("authors")
    @classmethod
    def is_author(cls, value) -> Union[str, dict[str, str]]: 
        """The is_author method makes sure there is author value definied."""
        def create_author_info(authors):
            key = [f'auth-{author + 1}' for author in range(len(authors))] 
            return dict(zip(key, authors))

        if isinstance(value, str):
            return value
        return create_author_info(value)

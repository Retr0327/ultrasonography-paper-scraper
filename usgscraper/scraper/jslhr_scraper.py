import re
import asyncio
import pydantic
from bs4 import BeautifulSoup
from dataclasses import dataclass
from usgscraper.util import convert
from typing import Optional, Any, Union
from usgscraper.downloader import (
    DownloadingJSLHRSoupStrategy,
    SingleJSLHRSoupStrategy,
    AllJSLHRSoupStrategy,
)


class JSLHRInfo(pydantic.BaseModel):
    """
    The JSLHRInfo object keeps track of an item in inventory, including title, published date, authors, and abstract.
    """

    title: Any
    published_date: Any
    authors: Union[list, str]
    abstract: Any

    @pydantic.validator("authors")
    @classmethod
    def has_author(cls, authors: Union[list, str]) -> Union[str, dict[str, str]]:
        """The has_author method makes sure there is author value definied."""

        def create_author_info(author_list: list) -> dict[str, str]:
            key = [f"auth-{author+1}" for author in range(len(author_list))]
            return dict(zip(key, author_list))

        author_list = [value["title"].strip() for value in authors]
        if isinstance(authors, str):
            return authors
        return create_author_info(author_list)

    @pydantic.validator("published_date")
    @classmethod
    def has_date(cls, date: Any) -> str:
        """The has_date method makes sure there is published_date value definied."""

        def create_date(soup_date: BeautifulSoup) -> str:
            is_date = re.compile("\w*.\d{4}$")
            return re.search(is_date, soup_date).group()

        if not date:
            return "no date"
        return create_date(date)

    @pydantic.validator("title", "abstract")
    @classmethod
    def has_content(cls, value: Any) -> str:
        """The has_content method makes sure there is title or abstract value definied"""
        if not value:
            return "no info"
        return " ".join(value.text.strip().split())


@dataclass
class JSLHR:
    """
    The JSLHR object extracts and cleans the JSON data from the Journal of Speech Language and Hearing Research.
    """

    volume: int
    issue: Optional[int] = None

    def merge_soup(self, soup_list: list) -> BeautifulSoup:
        """The merge_soup method converts a list of soup objects to a single soup object.

        Args:
            soup_list (list): the list of soup objects

        Returns:
            a list
        """
        filterd_list = list(filter(lambda value: "no such issue" != value, soup_list))
        pseudo_soup = BeautifulSoup("<body></body>", "lxml")
        for soup in filterd_list:
            pseudo_soup.append(soup)
        return pseudo_soup

    def extract_soup(self) -> DownloadingJSLHRSoupStrategy:
        """The extract_soup method extracts the soup object based on `self.volume` and `self.issue`."""
        if self.issue:
            return SingleJSLHRSoupStrategy(
                volume=self.volume, issue=self.issue
            ).create_soup()
        soup_list = asyncio.run(
            AllJSLHRSoupStrategy(volume=self.volume, issue=None).create_soup()
        )
        return self.merge_soup(soup_list)

    def clean_data(self, article_html: BeautifulSoup) -> dict[str, Union[str, list]]:
        title = article_html.find("div", class_="issue-item__title")
        date = article_html.find("div", class_="issue-item__header").text
        abstract = article_html.find("div", class_="accordion__content card--shadow")
        authors = article_html.find("div", class_="issue-item__authors").ul.find_all(
            "a"
        )

        jslhr_info = JSLHRInfo(
            title=title, published_date=date, abstract=abstract, authors=authors
        )
        return jslhr_info.dict()

    def extract_data(self) -> map:
        """The extract_data method extracts the BeautifulSoup object from `self.extract_soup()`.

        Returns:
            a map object
        """
        articles_soup = self.extract_soup().findAll("div", class_="issue-item")
        return map(self.clean_data, articles_soup)

    @convert("json")
    def to_json(self):
        return

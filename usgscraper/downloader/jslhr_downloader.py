import asyncio
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from aiohttp import ClientSession
from abc import ABC, abstractmethod
from fake_useragent import UserAgent
from typing import Union, Callable, Awaitable, Optional


class DownloadingSoupStrategy(ABC):
    def __init__(self, volume: int, issue: Optional[int] = None) -> None:
        self.volume = volume
        self.issue = issue

    @abstractmethod
    def create_soup(self) -> BeautifulSoup:
        """Returns a soup object"""
        pass


class SingleSoupStrategy(DownloadingSoupStrategy):
    def create_soup(self) -> Union[BeautifulSoup, str]:
        req = requests.get(
            f"https://pubs.asha.org/toc/jslhr/{self.volume}/{self.issue}",
            headers={"user-agent": UserAgent().google},
        )
        soup = BeautifulSoup(req.text, "lxml")
        article_html = soup.find(class_="titled_issues")
        if article_html is None:
            return "no such issue"
        return article_html


class AllSoupStrategy(DownloadingSoupStrategy):
    def create_url_list(self, issue: int) -> str:
        """The create_url_list method create a url based on the base url

        Args:
            issue (str): the issue of a volume
        Returns:
            a str
        """
        base_url = f"https://pubs.asha.org/toc/jslhr/{self.volume}/"
        return urljoin(base_url, str(issue))

    async def fetch(self, url: str, session) -> Union[BeautifulSoup, str]:
        """The fetch method fetch the url and session to get the soup object

        Args:
            url (str)
            session
        Returns:
            a BeautifulSoup object if a issue exists, a str otherwise.
        """
        async with session.get(url) as response:
            html_body = await response.text()
            soup = BeautifulSoup(html_body, "lxml")
            article_html = soup.find(class_="titled_issues")
            if article_html is None:
                return "no such issue"
            return article_html

    async def create_soup(self) -> Callable[[], Awaitable[list]]:
        url_list = list(map(self.create_url_list, range(1, 13)))
        async with ClientSession(headers={"user-agent": UserAgent().google}) as session:
            tasks = [asyncio.create_task(self.fetch(url, session)) for url in url_list]
            return await asyncio.gather(*tasks)

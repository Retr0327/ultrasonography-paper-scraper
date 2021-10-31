import json
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from fake_useragent import UserAgent
from typing import Callable, Awaitable, Optional


HEADERS = {"user-agent": UserAgent().google}


class DownloadingJSONStrategy(ABC):
    """
    The DownloadingJSONStrategy object is the abstract class for downlading classes.
    """

    def __init__(self, volume: int, issue: Optional[int] = None):
        self.volume = volume
        self.issue = issue

    def create_url(self, issue: str) -> str:
        """The create_url method creates a url based on the arugment `issue`.

        Args:
            issue (str): the issue of a volume

        Returns:
            a str
        """
        if self.volume >= 42:
            return f"https://www.sciencedirect.com/journal/journal-of-phonetics/vol/{self.volume}/suppl/C"
        return f"https://www.sciencedirect.com/journal/journal-of-phonetics/vol/{self.volume}/issue/{issue}"

    def find_articles(self, json_data: json) -> json:
        """The find_articles method is a strategy that finds the artice JSON data from `json_data`.
        Args:
            json_data (json): the original JSON data
        Returns:
            a json
        """

        try:
            return json.loads(json_data)["articles"]["ihp"]["data"]["issueBody"][
                "issueSec"
            ][1]["includeItem"]
        except KeyError:
            return json.loads(json_data)["articles"]["ihp"]["data"]["issueBody"][
                "includeItem"
            ]

    @abstractmethod
    def download_json(self):
        """Returns a json object"""
        pass


class SingleJSONStrategy(DownloadingJSONStrategy):
    """
    The SingleJSONStrategy object downloads one json at a time.
    """

    def download_json(self) -> list[dict[str, str]]:
        url = self.create_url(self.issue)
        req = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(req.text, "lxml")
        json_data = json.loads(soup.find("script", {"type": "application/json"}).text)
        return self.find_articles(json_data)


class AllJSONStrategy(DownloadingJSONStrategy):
    """
    The AllJSONStrategy object downloads all the json at a time.
    """

    async def fetch(self, url: str, session) -> Callable[[], Awaitable[list]]:
        async with session.get(url) as response:
            html_body = await response.text()
            soup = BeautifulSoup(html_body, "lxml")
            json_info = soup.find("script", {"type": "application/json"})
            if not json_info:
                return "no json data"
            return self.find_articles(json.loads(json_info.text))

    async def download_json(self) -> Callable[[], Awaitable[list]]:
        url_list = list(map(self.create_url, range(1, 7)))
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            tasks = [asyncio.create_task(self.fetch(url, session)) for url in url_list]
            return await asyncio.gather(*tasks)

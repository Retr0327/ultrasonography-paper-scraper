import json
import aiohttp
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional


@dataclass
class JPhonJSONDownloader:
    """
    The JPhonJSONDownloader object downloads the JSON from Journal of Phonetics
    """

    volume: int
    headers: dict
    issue: Optional[int] = None

    @property
    def url(self) -> str:
        """The url property set the url based on the volume number.

        Returns:
            a str
        """
        if self.volume >= 42:
            return f"https://www.sciencedirect.com/journal/journal-of-phonetics/vol/{self.volume}/suppl/C"
        return f"https://www.sciencedirect.com/journal/journal-of-phonetics/vol/{self.volume}/issue/{self.issue}"

    def find_articles_strategy_1(self, json_info: json) -> json:
        """The find_articles_strategy_1 method is a strategy that finds the artice JSON data from `json_info`.

        Args:
            json_info (json): the original JSON data

        Returns:
            a json
        """
        return json.loads(json_info)["articles"]["ihp"]["data"]["issueBody"][
            "issueSec"
        ][1]["includeItem"]

    def find_articles_strategy_2(self, json_info) -> json:
        """The find_articles_strategy_2 method is another strategy that finds the artice JSON data from `json_info`.

        Args:
            json_info (json): the original JSON data

        Returns:
            a json
        """
        return json.loads(json_info)["articles"]["ihp"]["data"]["issueBody"][
            "includeItem"
        ]

    async def download(self) -> json:
        """The get_json method gets the JSON data.

        Returns:
            a json
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(self.url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "lxml")
                json_info = json.loads(
                    soup.find("script", {"type": "application/json"}).text
                )
                try:
                    return self.find_articles_strategy_1(json_info)
                except KeyError:
                    return self.find_articles_strategy_2(json_info)

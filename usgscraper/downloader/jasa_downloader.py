import aiohttp
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class JASADownloader:
    """
    The JASADownloader object downloads the JSON from the Journal of the Acoustical Society of America.
    """

    volume: int
    issue: int
    headers: dict

    @property
    def url(self) -> str:
        """The url property set the url based on the volume and issue number."""
        return f"https://asa.scitation.org/toc/jas/{self.volume}/{self.issue}?size=all"

    async def download(self) -> BeautifulSoup:
        """The download method gets the target BeautifulSoup object.

        Returns:
            a BeautifulSoup object
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(self.url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "lxml")
                article_html = soup.find("div", class_="sub-section")
                if article_html == None:
                    return "no such issue"
                return article_html

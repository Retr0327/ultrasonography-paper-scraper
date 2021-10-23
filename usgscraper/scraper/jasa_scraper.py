import re
import json
import pydantic
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Union, Optional
from usgscraper.downloader import JASADownloader
from concurrent.futures import ThreadPoolExecutor


class JASAInfo(pydantic.BaseModel):
    title: str
    published_date: str
    authors: Union[list, str]
    href: str

    @pydantic.validator("authors")
    @classmethod
    def has_author(cls, value) -> Union[str, dict[str, str]]:
        def create_author_info(authors):
            key = [f"auth-{author+1}" for author in range(len(authors))]
            return dict(zip(key, authors))

        if isinstance(value, str):
            return value
        return create_author_info(value)


@dataclass
class JASA:
    """
    The JASA object extracts and cleans the data from the Journal of the Acoustical Society of America.
    """

    volume: int
    issue: Optional[int] = None

    def download_multiple(self, issue):
        return JASA(volume=self.volume, issue=issue).soup

    @property
    def soup(self) -> BeautifulSoup:
        """The soup property set the soup object based on the volume and issue number.

        Returns:
            a BeautifulSoup object
        """
        if self.issue:
            return JASADownloader(volume=self.volume, issue=self.issue).download()

        with ThreadPoolExecutor() as executor:
            sudo_soup = BeautifulSoup("<html><body></body></html>", "lxml")
            sudo_body = sudo_soup.find("body")
            result = executor.map(self.download_multiple, [*range(1, 7)])
            for soup in result:
                sudo_body.append(soup)
            return sudo_body

    def create_href(self, doi) -> str:
        """The create_href method creates a href based on the doi.

        Returns:
            a str
        """
        href = re.search("(?<=\/)\d.*", doi).group()
        return f"https://asa.scitation.org/doi/full/{href}"

    def create_author_list(self, author_html) -> Union[list, str]:
        """The create_author_list method creates a list of authors

        Returns:
            a list
        """
        try:
            authors = author_html.find_all(class_="hlFld-ContribAuthor")
            return [author.text.strip() for author in authors]
        except AttributeError:
            return "no author"

    def clean_data(self, article_html) -> dict[str, Union[str, list]]:
        """The clean_data method cleans the BeautifulSoup object from the argument `article_html`.

        Args:
            article_html (BeautifulSoup): the BeautifulSoup object with paper info.

        Returns:
            a dict: {
                'title': 'Estimating target strength of estuarine pelagic fish assemblages using fisheries survey data',
                'published_date': 'October 2021',
                'authors': [
                    {
                        'auth-1': 'Justin R. Stevens',
                        'auth-2': 'J. Michael Jech',
                        'auth-3': 'Gayle B. Zydlewski',
                        'auth-4': 'Damian C. Brady',
                    }
                ],
                'href': 'https://asa.scitation.org/doi/full/10.1121/10.0006449',
                }
        """

        title = article_html.find(class_="hlFld-Title").text.strip()
        date = article_html.find(class_="open-access item-access").text.strip()
        article_date = re.search("(?<=(Full|Open)).*", date).group()
        doi = article_html.find(class_="meta-article").a.text.strip()
        href = self.create_href(doi)
        author_html = article_html.find(class_="entryAuthor")
        authors = self.create_author_list(author_html)

        jasa_info = JASAInfo(
            title=title, 
            published_date=article_date, 
            authors=authors, 
            href=href
        )
        return jasa_info.dict()

    def extract_data(self) -> map:
        """The extract_data method extracts the BeautifulSoup object from `article_html_list`.

        Returns:
            a map object
        """
        article_html_list = self.soup.findAll("section", class_="card")
        return map(self.clean_data, article_html_list)

    def to_json(self) -> None:
        """The to_json method converts the data to json file"""
        data = list(self.extract_data())
        with open(f"JASA - {self.volume}.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False)

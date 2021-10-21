import requests
from typing import Union
from bs4 import BeautifulSoup
from dataclasses import dataclass
from fake_useragent import UserAgent


@dataclass
class JASADownloader:
    """
    The JASADownloader object downloads the JSON from the Journal of the Acoustical Society of America.
    """

    volume: int
    issue: int

    @property
    def headers(self) -> dict[str, str]:
        """The headers property set the headers based on the volume and issue number."""
        return {
            "authority": "asa.scitation.org",
            "method": "GET",
            "path": f"/toc/jas/{self.volume}/{self.issue}",
            "scheme": "https",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "cookie": "timezone=480; MAID=MDE5TEKRZxJiaXXY5v1L3g==; I2KBRCK=1; _gid=GA1.2.471755225.1634812858; osano_consentmanager_uuid=9eabedcd-2da3-40e7-9ec5-9b5edd29baf0; osano_consentmanager=akAGMIPDgIwWUw4aqdavDCevUn7m3HDTcH-sKLzYymvIQD2DodgMkJz18ntRUID18z8bWno-j2AsmVK3N2kul_YsS2RC9fIrqBIo0SN9rXulaREeLi4duxEQR_B5ILW6p8Gwpgif2uAQdcsOraZgVAYqxpvQe60R3ZcMMwjocPn8QXY0BRFwPJVsPfRQPWqsde9QPkhwmKI7HU7GNL8kRsw9vqamqYAzvkIVxDKkuFYtbX9iKWprYdeMd8Bsdh_bhpL0BeRSmHgbAxbdV0lhjXtL2tSM-i8aaen6WvqeFqLTV6k4-yRNDoJzVfho6JTNWtPUm7M-Cc9z0uUKfPekvUxmIkD5Wnsyy3K6WSPBG2vW09NDhWnU_Uwj7RA=; osano_consentmanager_expdate=1667990458456; timezone=480; _ga=GA1.3.686566128.1634812858; _gid=GA1.3.471755225.1634812858; JSESSIONID=0543a24e-6237-4d75-8f72-da541783d72a; SERVER=WZ6myaEXBLFUgBZIdXnDcg==; MACHINE_LAST_SEEN=2021-10-21T06%3A22%3A02.925-07%3A00; _ga_W1NY9Q2R0V=GS1.1.1634822523.3.1.1634822611.0; _ga=GA1.1.686566128.1634812858",
            "sec-ch-ua": """Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99""",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "Windows",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": UserAgent().google, 
        }

    @property
    def url(self) -> str:
        """The url property set the url based on the volume and issue number."""
        return f"https://asa.scitation.org/toc/jas/{self.volume}/{self.issue}?size=all"

    def download(self) -> Union[str, BeautifulSoup]:
        """The download method gets the target BeautifulSoup object.

        Returns:
            a BeautifulSoup object if a issue exists, a str otherwise.
        """
        req = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(req.text, 'lxml')
        article_html = soup.find("div", class_="sub-section") 
        if article_html == None:
            return "no such issue"
        return article_html

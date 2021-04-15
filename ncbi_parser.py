import re
import webbrowser
from typing import Dict, Iterable, Iterator, List, Tuple
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from bs4.element import Tag
from openpyxl import Workbook

row_type = Tuple[str, str, str]


class NCBIParser:
    excel_fields = (
        "Name",
        "Link",
        "Keywords",
    )
    file_name = "ncbi.xlsx"
    host = "https://pubmed.ncbi.nlm.nih.gov/"
    pagination = 200

    def __call__(self) -> None:
        content = self.get_content()
        rows = self.get_rows(content)
        self.save_to_excel(rows)

    def get_content(self) -> bytes:
        response = httpx.get(
            self.host,
            params={
                "term": self.term_param,
                "filter": "datesearch.y_10",
                "format": "abstract",
                "size": self.pagination,
            },
            timeout=None,
        )
        webbrowser.open(str(response.url))
        return response.content

    @classmethod
    def get_rows(cls, response_content: bytes) -> Iterator[row_type]:
        soup = BeautifulSoup(response_content, features="html.parser")
        articles = soup.select('.results-article')

        for article in articles:
            yield (
                article.select_one('h1.heading-title').text.replace('\n', '').strip(),
                urljoin(cls.host, article.h1.a['href']),
                cls._get_article_keywords(article)
            )

    @staticmethod
    def _get_article_keywords(article: Tag) -> str:
        if not (keywords := article.select_one('.abstract > p')):
            return

        cleaned_keywoards = re.sub(r'[ ]{2,}|\n|\.|Keywords:', '', keywords.text)
        return cleaned_keywoards.replace(";", ",")

    @classmethod
    def save_to_excel(cls, rows: Iterable[row_type]) -> None:
        wb = Workbook()
        ws = wb.active

        ws.append(cls.excel_fields)
        for row in rows:
            ws.append(row)

        wb.save(cls.file_name)

    @property
    def term_param(self) -> str:
        term_1 = "osteoarthritis"
        #term_2 = "joints"
        term_3 = "hyaline cartilage"
        term_4 = "gene"
        term_5 = "oa"
        term_6 = "signaling pathway"
        term_7 = "chondrocyte"
        #term_8 = "BMP-7"
        return "(" + term_1 + " OR " + term_5 + ") AND (" + term_3 + ") AND (" + term_4 + ") AND (" + term_6 + ") AND (" + term_7 + ")"

if __name__ == "__main__":
    NCBIParser()()


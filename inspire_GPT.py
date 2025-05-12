import os
import requests
from pathlib import Path
from typing import List, Dict, Any

# Assuming FASTMCP provides a base class ModelContextProtocol
try:
    from fastmcp import ModelContextProtocol
except ImportError:
    class ModelContextProtocol:
        """Placeholder base class if fastmcp is not installed."""
        pass


class InspireHEPContext(ModelContextProtocol):
    """
    A ModelContextProtocol implementation for InspireHEP.

    Functionalities:
    - search_inspirehep(query: str) -> List[Dict[str, Any]]
    - download_pdfs(records: List[Dict[str, Any]], out_dir: str = 'papers') -> None
    - list_downloaded(out_dir: str = 'papers') -> List[Path]
    - get_paper_info(record: Dict[str, Any]) -> Dict[str, Any]
    """

    BASE_URL = "https://inspirehep.net/api/literature"

    def __init__(self, out_dir: str = 'papers'):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(exist_ok=True)

    def search_inspirehep(self, query: str, size: int = 10) -> List[Dict[str, Any]]:
        """
        Search InspireHEP for literature matching the query.

        :param query: The search string.
        :param size: Number of records to return.
        :return: List of record dicts.
        """
        params = {
            'q': query,
            'size': size,
        }
        resp = requests.get(self.BASE_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get('hits', {}).get('hits', [])

    def download_pdfs(self, records: List[Dict[str, Any]], out_dir: str = None) -> None:
        """
        Download PDFs for the given InspireHEP records.

        :param records: List of record dicts from search_inspirehep.
        :param out_dir: Directory to save PDFs.
        """
        target_dir = Path(out_dir or self.out_dir)
        target_dir.mkdir(exist_ok=True)

        for rec in records:
            # Get PDF link
            links = rec.get('metadata', {}).get('links', [])
            pdf_link = None
            for link in links:
                if link.get('title', '').lower() == 'pdf':
                    pdf_link = link.get('url')
                    break
            if not pdf_link:
                continue

            # Prepare filename
            rec_id = rec.get('id').split('/')[-1]
            filename = target_dir / f"{rec_id}.pdf"
            if filename.exists():
                print(f"Already downloaded: {filename}")
                continue

            # Download
            print(f"Downloading {rec_id} from {pdf_link}...")
            r = requests.get(pdf_link)
            r.raise_for_status()
            with open(filename, 'wb') as f:
                f.write(r.content)
            print(f"Saved to {filename}")

    def list_downloaded(self, out_dir: str = None) -> List[Path]:
        """
        List all downloaded PDF files in the out_dir.

        :param out_dir: Directory where PDFs are stored.
        :return: List of Paths.
        """
        target_dir = Path(out_dir or self.out_dir)
        return list(target_dir.glob('*.pdf'))

    def get_paper_info(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata: title, abstract, authors.

        :param record: A single record dict.
        :return: Dict with title, abstract, authors list.
        """
        meta = record.get('metadata', {})
        title = meta.get('titles', [{}])[0].get('title', '')
        abstract = ''
        if 'abstracts' in meta and meta['abstracts']:
            abstract = meta['abstracts'][0].get('value', '')

        authors = []
        for a in meta.get('authors', []):
            name = a.get('full_name') or ' '.join(a.get('names', []))
            authors.append(name)

        return {
            'title': title,
            'abstract': abstract,
            'authors': authors
        }


# Example usage:
if __name__ == '__main__':
    hep = InspireHEPContext('downloaded_papers')
    # Search for recent Higgs papers
    records = hep.search_inspirehep('Higgs boson', size=5)
    hep.download_pdfs(records)
    print("Downloaded files:", hep.list_downloaded())
    info = hep.get_paper_info(records[0])
    print("Sample paper info:", info)

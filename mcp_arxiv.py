import argparse
from pathlib import Path
from typing import List, Dict
import arxiv
import os
import requests

from mcp.server.fastmcp import FastMCP
# import PyPDF2

# Initialize the MCP server
mcp = FastMCP("ArxivServer")

parser = argparse.ArgumentParser(description="arXiv MCP Server")
parser.add_argument("--storage-path", required=True, help="Path to store downloaded papers")
args, unknown = parser.parse_known_args()

STORAGE_PATH = Path(args.storage_path).resolve()
STORAGE_PATH.mkdir(parents=True, exist_ok=True)

@mcp.tool()
def search_arxiv(query: str, max_results: int = 2) -> List[str]:
    """Search arXiv and return IDs of recent papers."""
    results = arxiv.Search(query=query, max_results=max_results)
    return [result.entry_id.split('/')[-1] for result in results.results()]

@mcp.tool()
def search_top_cited_arxiv(query: str, max_results: int = 4) -> List[Dict[str, any]]:
    BASE_URL = "https://inspirehep.net/api/literature"
    """Search InspireHEP for literature matching the query."""
    params = {
        'q': query,
        'size': max_results,
    }
    resp = requests.get(BASE_URL, params=params)
    resp.raise_for_status()
    data = resp.json()
    records = data.get('hits', {}).get('hits', [])
    ids = [ records[i].get('id') for i in range(len(records))]
    return ids

@mcp.tool()
def download_paper(arxiv_id: str) -> str:
    """Download paper from arXiv and store it."""
    # Check if already downloaded
    file_path = STORAGE_PATH / f"{arxiv_id}.pdf"
    if file_path.exists():
        return f"Paper {arxiv_id} already downloaded to {file_path.name}"

    search = arxiv.Search(id_list=[arxiv_id])
    paper = next(search.results(), None)
    if paper:
        # file_path = STORAGE_PATH / f"{arxiv_id}.pdf"
        paper.download_pdf(dirpath=STORAGE_PATH, filename=file_path.name)
        # print(f"Downloaded {arxiv_id} to {file_path.name}")
        return f"Downloaded {arxiv_id} to {file_path.name}"
    else:
        return f"Paper {arxiv_id} not found"

@mcp.tool()
def list_papers() -> List[str]:
    """List downloaded papers."""
    return [f.name for f in STORAGE_PATH.glob("*.pdf")]

@mcp.tool()
def read_paper(filename : str) -> str:
    """Read and return the content of a downloaded paper."""
    file_path = STORAGE_PATH / filename
    if not file_path.exists() or not file_path.is_file():
        return f"File '{filename}' not found or is not a valid file."
    try:
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        return f"Error reading PDF: {e}"
    return f"Content of '{filename}'"
    


@mcp.tool()
def get_paper_info(arxiv_id: str) -> Dict[str, str]:
    """Extract and return title and abstract of a paper from arXiv."""
    arxiv_id = str(arxiv_id)
    search = arxiv.Search(id_list=[arxiv_id])
    paper = next(search.results(), None)
    if paper:
        return {"arxivid" : arxiv_id, "url": paper.pdf_url, "date": paper.updated, "title": paper.title, "abstract": paper.summary, "authors":paper.authors}
    else:
        return {"error": f"Paper {arxiv_id} not found"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="arXiv MCP Server")
    parser.add_argument("transport", choices=["stdio", "sse"], help="Transport mode")
    parser.add_argument("--storage-path", required=True, help="Path to store papers")
    args = parser.parse_args()

    mcp.run(transport=args.transport)

import requests
import csv
import argparse
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Function to fetch papers from PubMed API
def fetch_papers(query: str) -> List[Dict]:
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    details_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    
    # Search PubMed for the query
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": 10,
        "retmode": "json"
    }
    response = requests.get(base_url, params=search_params)
    response.raise_for_status()
    search_data = response.json()
    
    ids = search_data.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []
    
    # Fetch details for the papers
    details_params = {
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "json"
    }
    details_response = requests.get(details_url, params=details_params)
    details_response.raise_for_status()
    details_data = details_response.json()
    
    papers = []
    for id in ids:
        summary = details_data.get("result", {}).get(id, {})
        papers.append({
            "PubmedID": id,
            "Title": summary.get("title", ""),
            "Publication Date": summary.get("pubdate", ""),
            "Non-academic Author(s)": "Heuristic not implemented",  # Placeholder
            "Company Affiliation(s)": "Heuristic not implemented",  # Placeholder
            "Corresponding Author Email": "Not available"           # Placeholder
        })
    return papers

# Function to save results to a CSV file
def save_to_csv(papers: List[Dict], filename: str):
    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
            "PubmedID", "Title", "Publication Date", 
            "Non-academic Author(s)", "Company Affiliation(s)", 
            "Corresponding Author Email"
        ])
        writer.writeheader()
        writer.writerows(papers)

# Main function
def main():
    parser = argparse.ArgumentParser(description="Fetch research papers from PubMed.")
    parser.add_argument("query", help="Search query for PubMed.")
    parser.add_argument("-f", "--file", help="Output file to save results as CSV.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode.")
    
    args = parser.parse_args()
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    try:
        logger.info("Fetching papers for query: %s", args.query)
        papers = fetch_papers(args.query)
        
        if not papers:
            logger.info("No papers found for the given query.")
            return
        
        if args.file:
            save_to_csv(papers, args.file)
            logger.info("Results saved to %s", args.file)
        else:
            for paper in papers:
                print(paper)
    except Exception as e:
        logger.error("An error occurred: %s", e)

if True:
    main()
"""poetry install
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"""
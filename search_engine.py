import requests
from bs4 import BeautifulSoup
import openreview
import time
import urllib3
import os
from datetime import datetime
import json
from openai import OpenAI

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_system_proxy():
    # ... (existing code) ...
    pass

class SearchEngine:
    def __init__(self, api_key=None):
        self.proxy = get_system_proxy()
        if self.proxy:
            print(f"Using system proxy: {self.proxy}")
            self.proxies = {'http': self.proxy, 'https': self.proxy}
        else:
            self.proxies = None
            
        # Initialize DeepSeek Client
        # API Key is now passed dynamically from the frontend/user settings
        if not api_key:
             # Fallback to env or empty (which will fail gracefully later if needed)
             api_key = os.getenv("DEEPSEEK_API_KEY", "")
             
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    def extract_keywords_with_deepseek(self, user_prompt):
        """
        Use DeepSeek to extract 3-5 academic keywords from natural language prompt.
        Returns a list of keywords.
        """
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": '你是一个学术搜索专家。请将用户的自然语言意图转化为 3-5 个具体的、组合式的学术英文关键词（避免过于宽泛的单词如 "Image"）。返回格式必须是 JSON: {"keywords": ["keyword1", "keyword2"]}'},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={ "type": "json_object" },
                stream=False
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            return data.get("keywords", [])
            
        except Exception as e:
            print(f"Error extracting keywords with DeepSeek: {e}")
            # Fallback: just return the user prompt as a single keyword
            return [user_prompt]

    def deepseek_rerank_papers(self, user_prompt, papers_list, top_n=25):
        """
        Rerank and select top_n papers based on user prompt using DeepSeek.
        Returns a list of selected paper IDs/indices or re-ordered list.
        """
        if not papers_list:
            return []
            
        # Limit to 100 papers to avoid context window limits
        candidates = papers_list[:100]
        
        # Format candidates for prompt
        candidates_text = ""
        for i, paper in enumerate(candidates):
            candidates_text += f"[{i}] Title: {paper.get('title', '')}\nAbstract: {paper.get('abstract', '')[:300]}...\n\n"
            
        prompt = f"""
        用户查询: "{user_prompt}"
        
        请从以下候选论文中，挑选出最符合用户意图的 Top {top_n} 篇论文。
        
        候选论文列表:
        {candidates_text}
        
        请返回一个 JSON 对象，格式如下:
        {{
            "recommendations": [
                {{ "id": 0, "reason": "简短推荐理由" }},
                ...
            ]
        }}
        注意: "id" 必须对应候选列表中的编号。
        """
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个学术助手，负责根据用户意图筛选和推荐论文。请严格按照 JSON 格式返回结果。"},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" },
                stream=False
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            recommendations = data.get("recommendations", [])
            
            # Reconstruct the result list
            reranked_results = []
            for rec in recommendations:
                idx = rec.get("id")
                if isinstance(idx, int) and 0 <= idx < len(candidates):
                    paper = candidates[idx].copy()
                    paper["recommendation_reason"] = rec.get("reason", "")
                    reranked_results.append(paper)
            
            return reranked_results
            
        except Exception as e:
            print(f"Error reranking papers with DeepSeek: {e}")
            # Fallback: return original list
            return papers_list[:top_n]

    def search(self, source, year, keyword, status="Accepted"):
        if source in ["ICLR", "NeurIPS", "ICML"]:
            return self.search_openreview(source, year, keyword, status)
        elif source in ["CVPR", "ECCV", "ICCV"]:
            return self.search_cvf(source, year, keyword)
        elif source == "AAAI":
            return self.search_aaai(year, keyword)
        else:
            return []

    def search_openreview(self, conference, year, keyword, status):
        results = []
        try:
            # Map conference name to OpenReview ID
            venue_prefix = f"{conference}.cc"
            
            print(f"Searching {conference} {year} ({status}) on OpenReview...")
            
            # Use V2 API for recent years (safe bet for 2023+)
            if int(year) >= 2023:
                client = openreview.api.OpenReviewClient(baseurl='https://api2.openreview.net')
                
                notes_to_process = []
                
                if status == "Accepted":
                    # 1. Search Accepted Papers
                    venue_id = f'{venue_prefix}/{year}/Conference'
                    print(f"Fetching accepted from {venue_id}")
                    try:
                        notes_to_process = client.get_all_notes(content={'venueid': venue_id})
                    except Exception as e:
                        print(f"Could not fetch accepted papers: {e}")
                
                elif status == "Under Review":
                    # 2. Search Under Review / Submissions
                    # Usually under 'Blind_Submission' or 'Submission'
                    invitation_id = f'{venue_prefix}/{year}/Conference/-/Blind_Submission'
                    print(f"Fetching under review from {invitation_id}")
                    try:
                        notes_to_process = client.get_all_notes(invitation=invitation_id)
                        if not notes_to_process:
                            # Fallback to just 'Submission'
                            invitation_id = f'{venue_prefix}/{year}/Conference/-/Submission'
                            notes_to_process = client.get_all_notes(invitation=invitation_id)
                    except Exception as e:
                        print(f"Could not fetch under review papers: {e}")
                
                # Process Results
                for note in notes_to_process:
                    content = note.content
                    title = content.get('title', {}).get('value', '')
                    abstract = content.get('abstract', {}).get('value', '')
                    authors = content.get('authors', {}).get('value', [])
                    keywords = content.get('keywords', {}).get('value', [])
                    pdf = content.get('pdf', {}).get('value', '')
                    
                    if self._match(keyword, title, abstract, keywords):
                        results.append({
                            "title": title,
                            "authors": authors,
                            "abstract": abstract,
                            "keywords": keywords,
                            "link": f"https://openreview.net/forum?id={note.id}",
                            "pdf": f"https://openreview.net{pdf}" if pdf else None,
                            "status": f"{conference} {year} ({status})"
                        })

            else:
                # V1 API for older years (Legacy, mostly just accepted/all)
                # V1 logic is complex for separating status, assume Accepted for simplicity or fallback
                client = openreview.Client(baseurl='https://api.openreview.net')
                venue_id = f'{venue_prefix}/{year}/Conference'
                
                # ... existing V1 logic (omitted for brevity, older years are usually accepted) ...
                # For simplicity, if user asks for Under Review for old years, we might return empty or just search submissions
                if status == "Under Review":
                     invitation = f'{venue_prefix}/{year}/Conference/-/Blind_Submission'
                     notes = client.get_all_notes(invitation=invitation)
                else:
                    notes = client.get_all_notes(content={'venueid': venue_id})
                
                for note in notes:
                    title = note.content.get('title', '')
                    abstract = note.content.get('abstract', '')
                    authors = note.content.get('authors', [])
                    keywords = note.content.get('keywords', [])
                    pdf = note.content.get('pdf', '')
                    
                    if self._match(keyword, title, abstract, keywords):
                        results.append({
                            "title": title,
                            "authors": authors,
                            "abstract": abstract,
                            "keywords": keywords,
                            "link": f"https://openreview.net/forum?id={note.id}",
                            "pdf": f"https://openreview.net{pdf}" if pdf else None,
                            "status": f"{conference} {year}"
                        })

        except Exception as e:
            print(f"Error searching {conference}: {e}")
            
        return results

    def search_cvf(self, conference, year, keyword):
        results = []
        
        # Validate year for biennial conferences
        year_int = int(year)
        if conference == "ECCV" and year_int % 2 != 0:
            print(f"ECCV is not held in odd years ({year}).")
            return []
        if conference == "ICCV" and year_int % 2 == 0:
            print(f"ICCV is not held in even years ({year}).")
            return []

        # Papers hosted on openaccess.thecvf.com
        # Supports CVPR, ICCV, ECCV
        
        # Construct URL based on conference
        # CVPR: CVPR2023
        # ICCV: ICCV2023
        # ECCV: ECCV2022
        
        base_url = f"https://openaccess.thecvf.com/{conference}{year}"
        urls_to_try = [f"{base_url}?day=all", base_url]
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        soup = None
        for url in urls_to_try:
            try:
                response = requests.get(url, headers=headers, verify=False, timeout=15, proxies=self.proxies)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    break
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")
        
        if soup:
            # CVF uses <dt class="ptitle"> for titles
            titles = soup.find_all('dt', class_='ptitle')
            
            for dt in titles:
                title_tag = dt.find('a')
                if title_tag:
                    title = title_tag.text.strip()
                    link = "https://openaccess.thecvf.com" + title_tag['href']
                    
                    # Check keyword in title
                    if keyword.lower() in title.lower():
                        # Find authors in the next <dd>
                        dd = dt.find_next_sibling('dd')
                        authors = []
                        if dd:
                            authors_tag = dd.find_all('form')[0].find_next_sibling('div', id='authors')
                            if authors_tag:
                                authors = [a.text.strip() for a in authors_tag.find_all('a')]
                        
                        # Find PDF link
                        pdf_link = None
                        if dd:
                            pdf_tag = dd.find('a', string='pdf')
                            if pdf_tag:
                                pdf_link = "https://openaccess.thecvf.com" + pdf_tag['href']
                            
                        results.append({
                            "title": title,
                            "authors": authors,
                            "abstract": "Abstract not available in list view",
                            "keywords": [],
                            "link": link,
                            "pdf": pdf_link,
                            "status": f"{conference} {year}"
                        })
                        
        return results

    def search_aaai(self, year, keyword):
        results = []
        # Use arXiv API to search for AAAI papers
        # arXiv is usually accessible and many AAAI papers are on arXiv
        
        import xml.etree.ElementTree as ET
        
        # arXiv API search
        api_url = "http://export.arxiv.org/api/query"
        
        # Search for papers mentioning AAAI and the keyword
        search_query = f"all:{keyword} AND all:AAAI AND all:{year}"
        
        params = {
            'search_query': search_query,
            'start': 0,
            'max_results': 50,
            'sortBy': 'relevance'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            # arXiv uses HTTP, not HTTPS - often works better with proxies
            # Try with proxy first
            if self.proxies:
                try:
                    response = requests.get(api_url, params=params, headers=headers, timeout=30, proxies=self.proxies)
                except:
                    # Fallback to direct connection
                    response = requests.get(api_url, params=params, headers=headers, timeout=30)
            else:
                response = requests.get(api_url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Parse XML response
                root = ET.fromstring(response.content)
                
                # Define namespace
                ns = {
                    'atom': 'http://www.w3.org/2005/Atom',
                    'arxiv': 'http://arxiv.org/schemas/atom'
                }
                
                entries = root.findall('atom:entry', ns)
                
                for entry in entries:
                    # Get metadata
                    comment = entry.find('arxiv:comment', ns)
                    journal_ref = entry.find('arxiv:journal_ref', ns)
                    
                    comment_text = comment.text.lower() if comment is not None and comment.text else ""
                    journal_text = journal_ref.text.lower() if journal_ref is not None and journal_ref.text else ""
                    
                    # Strict AAAI Filtering
                    # Must contain "aaai" AND the target year in metadata (comments or journal ref)
                    # This filters out papers that just cite AAAI or mention it in abstract
                    target_year_str = str(year)
                    is_aaai = False
                    
                    meta_text = f"{comment_text} {journal_text}"
                    
                    if "aaai" in meta_text and target_year_str in meta_text:
                        is_aaai = True
                    
                    if not is_aaai:
                        continue

                    title = entry.find('atom:title', ns)
                    title = title.text.strip().replace('\n', ' ') if title is not None else ''
                    
                    summary = entry.find('atom:summary', ns)
                    abstract = summary.text.strip().replace('\n', ' ') if summary is not None else ''
                    
                    # Get authors
                    authors = []
                    for author in entry.findall('atom:author', ns):
                        name = author.find('atom:name', ns)
                        if name is not None:
                            authors.append(name.text)
                    
                    # Get link
                    link = ''
                    pdf = None
                    for l in entry.findall('atom:link', ns):
                        if l.get('type') == 'text/html':
                            link = l.get('href', '')
                        elif l.get('title') == 'pdf':
                            pdf = l.get('href', '')
                    
                    if not link:
                        id_elem = entry.find('atom:id', ns)
                        link = id_elem.text if id_elem is not None else ''
                    
                    results.append({
                        "title": title,
                        "authors": authors,
                        "abstract": abstract,
                        "keywords": [],
                        "link": link,
                        "pdf": pdf,
                        "status": f"AAAI {year} (via arXiv)"
                    })
                        
        except Exception as e:
            print(f"Error searching AAAI via arXiv: {e}")
            
        return results

    def _match(self, keyword, title, abstract, keywords):
        q = keyword.lower()
        if q in title.lower():
            return True
        if abstract and q in abstract.lower():
            return True
        if keywords and any(q in k.lower() for k in keywords):
            return True
        return False

# Factory/Helper function
def get_search_engine(api_key=None):
    return SearchEngine(api_key)

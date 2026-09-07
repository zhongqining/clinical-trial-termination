import requests, json, time, os
from datetime import date

BASE = 'https://clinicaltrials.gov/api/v2/studies'
OUT_DIR = 'data/raw'

def fetch_all(max_records=30000, page_size=1000, delay=0.25):
    studies = []
    token = None
    page = 0 #counter for number of batches pulled so far
    while len(studies) < max_records:
        params = {
            "filter.overallStatus": "COMPLETED|TERMINATED",
            "pageSize": page_size,
            "format": "json",
        }
        if token: #after first pass through, token is initialized
            params["pageToken"] = token
        else: #first pass through to get the total count
            params["countTotal"] = "true"
            
        response = requests.get(BASE, params=params, timeout=60)
        response.raise_for_status() #checks if the api actually succeeded
        
        data = response.json() #requests version of json.loads(), creates dict
        
        batch = data.get("studies", []) #[] is fallback incase studies is empty
        if not batch:
            break
        studies.extend(batch)
        page += 1
        
        print(f"page {page}: +{len(batch)} (total {len(studies)})")
        
        token = data.get("nextPageToken")
        if not token: #meaning this was teh last page
            break
        
        time.sleep(delay) #0.25 delay to avoid triggering rate-limit
        
    return studies #fully populated studies of 30k trials


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True) #data/raw, okay if it already exists
    
    studies = fetch_all() #actual api call
    #studies = fetch_all(max_records=2000) #test run to make sure it works
    stamp = date.today().isoformat() #stamps today's date
    
    path = f"{OUT_DIR}/studies_{stamp}.json"
    
    with open(path, "w") as f: #destructive file creation, with auto-closes
        json.dump(studies, f)
        
    print(f"saved {len(studies)} studies to {path}")
        
        
        
            

            
import json, glob
import pandas as pd

AGE_UNITS = { #everything will be done in units of years
    "year": 1.0, 
    "month": 1/12, 
    "week": 1/52, 
    "day": 1/365, 
    "hour": 1/(365 * 24),
    "minute": 1/(365 * 24 * 60),
    "second": 1/(365 * 24 * 60 * 60)
} 

def parse_age(age): #to turn a string describing the age into actual numerical values
    if not isinstance(age, str): #missing values = None
        return None
    parts = age.strip().split() #returns a list of strings the age
    if (len(parts) < 2):
        return None
    try: #if first arg isn't a number, we return None instead
        value = float(parts[0])
    except ValueError:
        return None
        
    unit = parts[1].lower().rstrip('s') #convert the unit to lower case and remove trailing 's'
    
    age_factor = AGE_UNITS.get(unit)
    if age_factor is None: #if the unit was not found in AGE_UNITS, we treat it as unparseable
        return None
    return value * age_factor

def flatten(study): #takes a singular study (dict) and flattens it into another dict
    
    #root directory
    p = study.get("protocolSection", {}) or {} #or {} incase teh value exists but is None
    
    #container folders
    identification = p.get("identificationModule", {}) or {}
    status = p.get("statusModule", {}) or {}
    design = p.get("designModule", {}) or {}
    sponsor_collaborators = p.get("sponsorCollaboratorsModule", {}) or {}
    conditions = p.get("conditionsModule", {}) or {}
    eligibility = p.get("eligibilityModule", {}) or {}
    arms_intervention = p.get("armsInterventionsModule", {}) or {}
    contacts_location = p.get("contactsLocationsModule", {}) or {}
    
    #sub-fields with more nested subfields
    start_date_struct = status.get("startDateStruct", {}) or {}
    enrollment = design.get("enrollmentInfo", {}) or {}
    design_info = design.get("designInfo", {}) or {}
    masking_info = design_info.get("maskingInfo", {}) or {}
    lead_sponsor = sponsor_collaborators.get("leadSponsor", {}) or {}
    locations = contacts_location.get("locations", []) or [] #locations is a list, not a dict
    
    #the actual subfields
    return{
        "nct_id": identification.get("nctId"), #unique id
        "status": status.get("overallStatus"), #status: compeleted or terminated, target
        "study_type": design.get("studyType"), #study type: intervention or observational
        "phase": (design.get("phases") or [None])[0], #phase: 
        "enroll_count": enrollment.get("count"), #target enrollment number
        "enroll_type": enrollment.get("type"), #if the enrollment count is a target or actual
        "start_date_string": start_date_struct.get("date"), #date string
        "sponsor_class": lead_sponsor.get("class"), #what kind of org is sponsoring the trial: industry, federal, etc
        "collaborator_count": len(sponsor_collaborators.get("collaborators") or []), #number of collabs
        "conditions": conditions.get("conditions") or [], #list of medical problems the trial is treatingsp
        "sites_count": len(locations), #number of sites
        "countries_count": len({loc.get("country") for loc in locations if loc.get("country")}), #number of countries
        "min_age_raw": eligibility.get("minimumAge"), #min age string, use parse_age on
        "max_age_raw": eligibility.get("maximumAge"), #max age string, use parse_age on
        "sex": eligibility.get("sex"), #male, female, all
        "healthy_volunteers": eligibility.get("healthyVolunteers"), #boolean, whether healthy volunteers are accepted or not
        "eligibility_criteria": eligibility.get("eligibilityCriteria"), #string explaining who is eligible
        "intervention_types": [intervention.get("type") for intervention in (arms_intervention.get("interventions") or [])], #drug, device, biological, etc
        "allocation": design_info.get("allocation"), #how participants are assigned to groups: randomized, non-randomized
        "masking": masking_info.get("masking") #masking level: none, single, double, triple/quadruple
    }
    
    
def build(raw_glob = "data/raw/studies_*.json"):
    path = sorted(glob.glob(raw_glob))[-1] #finds the most recent, there should be only 1
    with open(path) as f:
        studies = json.load(f)
    df = pd.DataFrame([flatten(s) for s in studies])
    starting_count = len(df)
    drops = {}
    
    #dropping
    #interventional only
    df = df[df["study_type"] == 'INTERVENTIONAL']
    drops["not_interventional"] = starting_count - len(df)
    new_count = len(df)
    
    #start date
    df["start_date"] = pd.to_datetime(df['start_date_string'], 
                                      format="mixed", errors="coerce") #change date string into date format, NaT for wrong ones
    df = df[df["start_date"].notna()] #drop Na rows
    drops["bad_start_date"] = new_count - len(df) #update drops dict
    new_count = len(df)
    df = df[(df["start_date"].dt.year >= 2010) & (df["start_date"].dt.year <= 2022)] #filter between 2010 and 2022
    drops["outside_date_range"] = new_count - len(df)
    new_count = len(df)
    
    #eligibility text
    df = df[(df["eligibility_criteria"].notna()) & (df["eligibility_criteria"].str.len() >= 50)] #drop no criteria or criteria that are too short
    drops["no_criteria"] = new_count - len(df)
    new_count = len(df)
    
    #target column
    df["terminated"] = (df["status"] == "TERMINATED").astype(int) #true -> 1, false -> 0
    
    #ages
    df["min_age"] = df["min_age_raw"].apply(parse_age)
    df["max_age"] = df["max_age_raw"].apply(parse_age)
    df["snapshot"] = path.split("_")[-1].replace(".json", "")
    
    
    print(f"start {starting_count} trials -> final {len(df)} trials")
    print("drops:", drops)
    print("termination rate:", round(df["terminated"].mean(), 4))
    return df, drops
    
    
if __name__ == "__main__":
    df, drops = build()
    df.to_parquet("data/processed/trials.parquet", index=False)
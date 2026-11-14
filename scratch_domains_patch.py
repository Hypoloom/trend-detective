# scratch_domains_patch.py  (run from backend/; writes domains_new.json, leaves domains.json untouched)
import json

SUN_KEY = "swgdn"   # leave as is for now

d = json.load(open("domains.json", encoding="utf-8"))
dom = {x["id"]: x for x in d["domains"]}

# wording: avoid overclaiming
for x in d["domains"]:
    for ax in x["axes"]:
        if ax["why_it_matters"].startswith("Not available from satellite or model data"):
            ax["why_it_matters"] = "Not in NASA climate data."
        if ax.get("variable") == "sunlight":
            ax["variable"] = SUN_KEY

# pond: missing ask_user axis
pond = dom["pond"]
pond["axes"].insert(5, {
    "name": "fed_stocked", "label": "Fish stocked or fed", "source": "ask_user", "critical": False,
    "prompt": "Is the pond stocked with fish, and do you feed them?",
    "why_it_matters": "Only you can tell us this. Its effect is not sourced here.",
    "evidence_status": "UNVERIFIED"})

# citrus: night temperature + optional own series; tighter keywords
cit = dom["citrus"]
cit["axes"].insert(4, {
    "name": "night_temp", "label": "Night-time temperature", "source": "nasa_data", "critical": False,
    "variable": "t2m_min",
    "why_it_matters": "Checked from NASA data (monthly average of daily lows). Its effect on fruit size is not sourced here.",
    "evidence_status": "UNVERIFIED"})
cit["axes"].append({
    "name": "fruit_size_series", "label": "Your own fruit-size records", "source": "ask_user", "critical": False,
    "prompt": "Do you have fruit-size records by year? (optional)",
    "why_it_matters": "NASA has no fruit-size data. Your records are the only way to link size to climate.",
    "evidence_status": "UNVERIFIED"})
cit["keywords"] = ["citrus", "orange", "oranges", "mandarin", "lemon", "orchard", "grove", "small oranges", "fruit size"]

json.dump(d, open("domains_new.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("wrote domains_new.json")

# runtime check: every nasa_data variable must be a key in stream.VARIABLES
import stream
for x in d["domains"]:
    for ax in x["axes"]:
        if ax["source"] == "nasa_data":
            print(x["id"], ax["name"], ax["variable"], "OK" if ax["variable"] in stream.VARIABLES else "MISSING in VARIABLES")
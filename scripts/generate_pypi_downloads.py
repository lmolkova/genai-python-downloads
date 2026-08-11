import json
import os
import urllib.request
import urllib.error
import time
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
JSON_PATH = os.path.join(REPO_ROOT, "pypi_downloads.json")

packages_config = [
    # utils
    {"package_name": "opentelemetry-util-genai", "source": "python-genai"},
    
    # google-genai
    {"package_name": "opentelemetry-instrumentation-google-genai", "instruments": "google-genai", "source": "python-genai"},
    {"package_name": "openinference-instrumentation-google-genai", "instruments": "google-genai", "source": "openinference"},
    
    # google-generativeai (legacy Google AI SDK)
    {"package_name": "opentelemetry-instrumentation-google-generativeai", "instruments": "google-genai", "source": "openllmetry"},
    
    # openai-agents
    {"package_name": "opentelemetry-instrumentation-genai-openai-agents", "instruments": "openai-agents", "source": "python-genai"},
    {"package_name": "opentelemetry-instrumentation-openai-agents-v2", "instruments": "openai-agents", "source": "python-contrib"},
    {"package_name": "opentelemetry-instrumentation-openai-agents", "instruments": "openai-agents", "source": "openllmetry"},
    {"package_name": "openinference-instrumentation-openai-agents", "instruments": "openai-agents", "source": "openinference"},
    
    # openai
    {"package_name": "opentelemetry-instrumentation-genai-openai", "instruments": "openai", "source": "python-genai"},
    {"package_name": "opentelemetry-instrumentation-openai-v2", "instruments": "openai", "source": "python-contrib"},
    {"package_name": "opentelemetry-instrumentation-openai", "instruments": "openai", "source": "openllmetry"},
    {"package_name": "openinference-instrumentation-openai", "instruments": "openai", "source": "openinference"},
    
    # langchain
    {"package_name": "opentelemetry-instrumentation-genai-langchain", "instruments": "langchain", "source": "python-genai"},
    {"package_name": "opentelemetry-instrumentation-langchain", "instruments": "langchain", "source": "openllmetry"},
    {"package_name": "openinference-instrumentation-langchain", "instruments": "langchain", "source": "openinference"},
    
    # anthropic
    {"package_name": "opentelemetry-instrumentation-genai-anthropic", "instruments": "anthropic", "source": "python-genai"},
    {"package_name": "opentelemetry-instrumentation-anthropic", "instruments": "anthropic", "source": "openllmetry"},
    {"package_name": "openinference-instrumentation-anthropic", "instruments": "anthropic", "source": "openinference"}
]

cache = {}

# Seed cache from existing pypi_downloads.json if it exists
if os.path.exists(JSON_PATH):
    try:
        with open(JSON_PATH, "r") as f:
            old_data = json.load(f)
            for report in old_data:
                for lib, pkgs in report.get("reports", {}).items():
                    for pkg_data in pkgs:
                        name = pkg_data.get("package_name")
                        dls = pkg_data.get("downloads_last_month")
                        if name and dls is not None:
                            cache[name] = dls
    except Exception as e:
        pass

def get_latest_version(pkg):
    url = f"https://pypi.org/pypi/{pkg}/json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())["info"]["version"]
    except Exception as e:
        return "Unknown"

def get_downloads(pkg):
    url = f"https://pypistats.org/api/packages/{pkg}/recent"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla"})
    delay = 15
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())["data"]
                dl = data.get("last_month", 0)
                cache[pkg] = dl
                return dl
        except urllib.error.HTTPError as e:
            if e.code == 404:
                cache[pkg] = 0
                return 0
            elif e.code == 429:
                time.sleep(delay)
                delay *= 2
            else:
                time.sleep(5)
        except Exception as e:
            time.sleep(5)
            
    # Fallback to cache if fetching failed
    if pkg in cache:
        return cache[pkg]
    return 0

def main():
    report_by_instruments = {}
    
    for cfg in packages_config:
        pkg = cfg["package_name"]
        source = cfg["source"]
        instruments = cfg.get("instruments", "util")
        
        version = get_latest_version(pkg)
        downloads = 0
        if version != "Unknown":
            downloads = get_downloads(pkg)
            # Sleep to be polite to API rate limits (unless cached/failed immediately)
            if pkg not in cache or downloads == cache.get(pkg):
                time.sleep(15)
        else:
            # Fallback if package PyPI metadata fails
            if pkg in cache:
                downloads = cache[pkg]
        
        package_report = {
            "package_name": pkg,
            "pypi_link": f"https://pypi.org/project/{pkg}/",
            "latest_version": version,
            "downloads_last_month": downloads,
            "source": source
        }
        
        if instruments in report_by_instruments:
            report_by_instruments[instruments].append(package_report)
        else:
            report_by_instruments[instruments] = [package_report]
            
    for inst, pkgs in report_by_instruments.items():
        pkgs.sort(key=lambda x: x["downloads_last_month"], reverse=True)
        
    report = {
        "date_collected": datetime.now().strftime("%Y-%m-%d"),
        "reports": report_by_instruments
    }
    
    with open(JSON_PATH, "w") as f:
        json.dump([report], f, indent=2)
        
    print(f"Success: Updated {JSON_PATH}")

if __name__ == "__main__":
    main()

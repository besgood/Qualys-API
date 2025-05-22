import requests
import time
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth
import getpass

# === Prompt User for Input ===
print("== Qualys Report Generator ==")
USERNAME = input("Qualys Username: ")
PASSWORD = getpass.getpass("Qualys Password: ")
asset_group_input = input("Enter one or more Asset Group IDs (comma-separated): ")
ASSET_GROUP_IDS = ','.join([x.strip() for x in asset_group_input.split(',') if x.strip().isdigit()])
TEMPLATE_ID = input("Report Template ID: ")
REPORT_TITLE = f"Scan Report for Asset Groups {ASSET_GROUP_IDS}"
OUTPUT_FORMAT = 'xlsx'
DOWNLOAD_FILE_NAME = f'qualys_report_{ASSET_GROUP_IDS.replace(",", "_")}.{OUTPUT_FORMAT}'

# === Config ===
QUALYS_BASE_URL = 'https://qualysapi.qualys.com'
HEADERS = {
    'X-Requested-With': 'PythonScript',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# === Step 1: Launch Report ===
def launch_report():
    url = f'{QUALYS_BASE_URL}/api/2.0/fo/report/'
    data = {
        'action': 'launch',
        'report_title': REPORT_TITLE,
        'report_type': 'Scan',
        'template_id': TEMPLATE_ID,
        'output_format': OUTPUT_FORMAT,
        'asset_group_ids': ASSET_GROUP_IDS,
    }
    response = requests.post(url, headers=HEADERS, auth=HTTPBasicAuth(USERNAME, PASSWORD), data=data)
    root = ET.fromstring(response.text)
    report_id_elem = root.find('.//ITEM[@key="id"]')
    if report_id_elem is not None:
        return report_id_elem.text
    raise Exception("Failed to extract report ID from response.")

# === Step 2: Wait for Report to Finish ===
def wait_for_report(report_id, timeout=600, interval=15):
    url = f'{QUALYS_BASE_URL}/api/2.0/fo/report/?action=list&id={report_id}'
    elapsed = 0
    while elapsed < timeout:
        response = requests.get(url, headers=HEADERS, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        root = ET.fromstring(response.text)
        status = root.find('.//STATUS').text
        print(f"[~] Report status: {status}")
        if status.lower() == 'finished':
            return True
        elif status.lower() in ['canceled', 'failed']:
            raise Exception(f"Report generation failed: {status}")
        time.sleep(interval)
        elapsed += interval
    raise TimeoutError("Report generation timed out.")

# === Step 3: Download the Completed Report ===
def download_report(report_id):
    url = f'{QUALYS_BASE_URL}/api/2.0/fo/report/?action=fetch&id={report_id}'
    response = requests.get(url, headers=HEADERS, auth=HTTPBasicAuth(USERNAME, PASSWORD), stream=True)
    if response.status_code == 200:
        with open(DOWNLOAD_FILE_NAME, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"[+] Report downloaded successfully as: {DOWNLOAD_FILE_NAME}")
    else:
        raise Exception(f"Failed to download report. Status code: {response.status_code}")

# === Main Flow ===
if __name__ == "__main__":
    try:
        print("\n[+] Launching report...")
        report_id = launch_report()
        print(f"[+] Report launched. Report ID: {report_id}")
        if wait_for_report(report_id):
            print("[+] Report is ready. Downloading...")
            download_report(report_id)
    except Exception as e:
        print(f"[!] Error: {e}")

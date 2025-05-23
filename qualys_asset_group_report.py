import requests
import getpass
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth
import time
import os

# Constants
QUALYS_BASE_URL = 'https://qualysapi.qualys.com'
HEADERS = {'X-Requested-With': 'Python Script'}
REPORT_TITLE = f"Qualys_Report_{int(time.time())}"
OUTPUT_FORMAT = 'excel'

# Prompt for credentials
USERNAME = input("Qualys Username: ").strip()
PASSWORD = getpass.getpass("Qualys Password: ").strip()

# Prompt for template ID
TEMPLATE_ID = input("Enter the Report Template ID: ").strip()

# Prompt for input method
print("\nSelect target input method:")
print("1. Use Asset Group ID(s)")
print("2. Use Host File (host.txt)")
mode = input("Enter option [1 or 2]: ").strip()

TARGET_PARAM = {}

if mode == "1":
    group_ids = input("Enter one or more Asset Group IDs (comma-separated): ").strip()
    TARGET_PARAM['asset_group_ids'] = group_ids
    input_mode = "asset_group"

elif mode == "2":
    host_file_path = input("Enter path to host file (one IP or FQDN per line): ").strip()

    if not os.path.exists(host_file_path):
        print(f"❌ File not found: {host_file_path}")
        exit(1)

    with open(host_file_path, 'r') as f:
        hosts = [line.strip() for line in f if line.strip()]

    if not hosts:
        print("❌ Host file is empty.")
        exit(1)

    host_list = ",".join(sorted(set(hosts)))
    TARGET_PARAM['ips'] = host_list
    input_mode = "host_file"

else:
    print("❌ Invalid option.")
    exit(1)


def launch_report():
    url = f'{QUALYS_BASE_URL}/api/2.0/fo/report/'

    if 'ips' in TARGET_PARAM:
        data = {
            'action': 'launch',
            'report_title': REPORT_TITLE,
            'report_type': 'Scan',
            'template_id': TEMPLATE_ID,
            'output_format': OUTPUT_FORMAT,
            'ips': TARGET_PARAM['ips']
        }
    else:
        data = {
            'action': 'launch',
            'report_title': REPORT_TITLE,
            'report_type': 'Scan',
            'template_id': TEMPLATE_ID,
            'output_format': OUTPUT_FORMAT,
            'asset_group_ids': TARGET_PARAM['asset_group_ids']
        }

    response = requests.post(url, headers=HEADERS, auth=HTTPBasicAuth(USERNAME, PASSWORD), data=data)

    if not response.text.strip():
        raise Exception("❌ Empty response from Qualys API.")

    print("📩 API response received. Parsing...")
    try:
        root = ET.fromstring(response.text)
        report_id_elem = root.find('.//ITEM[@key="id"]')
        if report_id_elem is not None:
            return report_id_elem.text
        print("🚫 Full response:")
        print(response.text)
        raise Exception("❌ Report ID not found in response.")
    except ET.ParseError as e:
        raise Exception(f"❌ Failed to parse XML response: {e}\nResponse was:\n{response.text}")


def check_report_status(report_id):
    url = f'{QUALYS_BASE_URL}/api/2.0/fo/report/?action=list&id={report_id}'
    while True:
        response = requests.get(url, headers=HEADERS, auth=HTTPBasicAuth(USERNAME, PASSWORD))
        root = ET.fromstring(response.text)
        status_elem = root.find('.//ITEM[@key="status"]')
        if status_elem is not None and status_elem.text == "Finished":
            print("✅ Report is ready for download.")
            return
        print("⌛ Waiting for report to finish...")
        time.sleep(10)


def download_report(report_id):
    url = f'{QUALYS_BASE_URL}/api/2.0/fo/report/?action=fetch&id={report_id}'
    response = requests.get(url, headers=HEADERS, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    filename = f"{REPORT_TITLE}.xlsx"
    with open(filename, 'wb') as f:
        f.write(response.content)
    print(f"📄 Report downloaded: {filename}")


def main():
    print("\n🚀 Launching report...")
    report_id = launch_report()
    print(f"🆔 Report ID: {report_id}")
    check_report_status(report_id)
    download_report(report_id)


if __name__ == '__main__':
    main()

import argparse
import requests
import os
import subprocess
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def extract_values_by_key(data, key):
    if isinstance(data, dict):
        for k, v in data.items():
            if k == key:
                yield v
            elif isinstance(v, (dict, list)):
                yield from extract_values_by_key(v, key)
    elif isinstance(data, list):
        for item in data:
            yield from extract_values_by_key(item, key)

def check_file_output(file_path):
    # Run the 'file' command on the specified file
    result = subprocess.run(['file', file_path], stdout=subprocess.PIPE, text=True)

    # Check if the output contains "Git index"
    return "Git index" in result.stdout

def check(url):
	try:
		extension = "index"
		url_https = 'https://' + url.strip() + '/.git/' + extension

		response = requests.get(url_https, verify = False, allow_redirects=False, timeout = 5)

		if response.status_code == 200:
			output_folder = "maxgit/" + url
			output_file = os.path.join(output_folder, extension)
			os.makedirs(output_folder, exist_ok = True)
			subprocess.run(["curl","-k","-s","-o",output_file, url_https])
			if check_file_output(output_file):
				print(url + "confirmed git file")
				index_json = output_file + ".json"
				subprocess.run(["gin", "-j", output_file], stdout=open(index_json, "w"))
				with open(index_json, 'r') as file:
					# Load the JSON data
					data = json.load(file)

				key_to_extract = "name"
				name_values = list(extract_values_by_key(data, key_to_extract))

				# Write the extracted values to the output file
				with open(output_file + "_extracted.txt", 'w') as file:
					for value in name_values:
						file.write(str(value) + '\n')
					print("files extracted from index")
			else:
				print(url + "false output, might be simple html")
			print("--------------------------")


	except Exception as e:
		pass

	

def printheader():
	print("""\
  _______  __  .___________.    __    __  .______       __         .___________.  ______     ______    __      
 /  _____||  | |           |   |  |  |  | |   _  \     |  |        |           | /  __  \   /  __  \  |  |     
|  |  __  |  | `---|  |----`   |  |  |  | |  |_)  |    |  |        `---|  |----`|  |  |  | |  |  |  | |  |     
|  | |_ | |  |     |  |        |  |  |  | |      /     |  |            |  |     |  |  |  | |  |  |  | |  |     
|  |__| | |  |     |  |        |  `--'  | |  |\  \----.|  `----.       |  |     |  `--'  | |  `--'  | |  `----.
 \______| |__|     |__|         \______/  | _| `._____||_______|       |__|      \______/   \______/  |_______|
                                                                                                               
		By: maxime_vhw
		""")


parser = argparse.ArgumentParser(description='Check if /.git/HEAD exists for a list of URLs.')
parser.add_argument("-f","--file", required=True, help='Path to the file containing URLs.')
args = parser.parse_args()
printheader();
with open(args.file, 'r') as file:
    for url in file:
        check(url)

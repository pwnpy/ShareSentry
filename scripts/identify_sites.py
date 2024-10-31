import urllib3
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from typing import List, Tuple
import logging
from tqdm import tqdm
from colorama import Fore, Style, init
import os

init(autoreset=True)

# Disable SSL warnings
urllib3.disable_warnings()

def print_banner():
    banner = """
    ╔══════════════════════════════════════════╗
    ║        Enumerating SharePoint Sites      ║
    ╚══════════════════════════════════════════╝
    """
    print(Fore.CYAN + banner + Style.RESET_ALL)

def disable_ssl(request):
    request.verify = False

def get_all_sites_new(ctx: ClientContext, row_limit: int = 500) -> List[str]:
    # row limit can be incraesed to 1000
    sites = set()
    start_row = 0 
    more_results = True
    logging.info("Starting SharePoint site enumeration.")
    with tqdm(desc="Fetching sites", unit=" batch") as pbar:
        while more_results:
            query = "contentclass:STS_Site OR contentclass:STS_Web"
            results = ctx.search.query(query, row_limit=row_limit, start_row=start_row).execute_query().value.PrimaryQueryResult.RelevantResults
            result_count = len(results.Table.Rows)
            if result_count > 0:
                for row in results.Table.Rows:
                    sites.add(row.Cells["Path"])
                start_row += row_limit
                pbar.update(1)
            else:
                more_results = False
    
    return list(sites)

def authenticate(auth_info: Tuple) -> ClientContext:
    auth_method, *auth_details = auth_info
    if auth_method == 'user_pass':
        _, username, password, url = auth_info
        ctx = ClientContext(url).with_credentials(UserCredential(username, password))
    else:  # Azure app auth
        _, cert_settings, tenant, url = auth_info
        ctx = ClientContext(url).with_client_certificate(tenant, **cert_settings)
    
    ctx.pending_request().beforeExecute += disable_ssl
    return ctx

def save_sites(sites: List[str], filename: str):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        for site in sites:
            f.write(f"{site}\n")
    print(Fore.GREEN + f"Identified sites saved to {filename}" + Style.RESET_ALL)

def main(auth_info: Tuple):
    print_banner()
    
    try:
        ctx = authenticate(auth_info)
        logging.info("Authentication successful")
        
        print(Fore.YELLOW + "Fetching SharePoint sites..." + Style.RESET_ALL)
        sites = get_all_sites_new(ctx)
        
        output_file = 'output/all_sites_new.txt'
        save_sites(sites, output_file)
        
        print(Fore.GREEN + f"Total sites identified: {len(sites)}" + Style.RESET_ALL)
        logging.info("SharePoint Site enumeration Finished.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(Fore.RED + f"An error occurred: {e}" + Style.RESET_ALL)

if __name__ == "__main__":
    print(Fore.RED + "This script should be run from the main.py file." + Style.RESET_ALL)
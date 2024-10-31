import urllib3
import logging
from colorama import Fore, Style, init
from tqdm import tqdm
from typing import Tuple
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

urllib3.disable_warnings()

# Initialize colorama
init(autoreset=True)

def disable_ssl(request):
    request.verify = False  # Disable certification verification

def print_banner():
    banner = """
    ╔══════════════════════════════════════════╗
    ║    Identifying Sites with Write Access   ║
    ╚══════════════════════════════════════════╝
    """
    print(Fore.CYAN + banner + Style.RESET_ALL)

def test_write_permission(site_url: str, auth_info: Tuple) -> bool:
    try:
        if auth_info[0] == 'user_pass': 
            _, username, password, _ = auth_info
            ctx = ClientContext(site_url).with_credentials(UserCredential(username, password))
        else:
            _, cert_settings, tenant, _ = auth_info
            ctx = ClientContext(site_url).with_client_certificate(tenant, **cert_settings)

        ctx.pending_request().beforeExecute += disable_ssl

        # Create a test document
        result = ctx.web.default_document_library().create_document_with_default_name("", "docx").execute_query()

        # Delete the test document
        file_url = f"Shared Documents/{result.value}"
        file = ctx.web.get_file_by_server_relative_url(file_url)
        file.delete_object().execute_query()

        # Check if the file still exists
        try:
            file = ctx.web.get_file_by_server_relative_url(file_url).get().execute_query()
            file_exists = file.exists
        except:
            file_exists = False

        if file_exists:
            with open('output/failed_to_delete.txt', 'a', encoding='utf-8') as f:
                f.write(f"{site_url}: {result.value}\n")
            logging.warning(f"Failed to delete file: {result.value} in {site_url}")
            print(f"{Fore.RED}Failed to delete file: {result.value} in {site_url}{Style.RESET_ALL}")
            return False
        return True
    except Exception as e:
        #logging.error(f"Failed to write to {site_url}: {e}")
        #print(f"{Fore.RED}Failed to write to {site_url}: {e}{Style.RESET_ALL}")
        return False

def main(auth_info: Tuple):
    print_banner()
    
    default_input_file = 'output/all_sites_new.txt'
    default_output_file = 'output/writable_spaces.txt'
    
    input_file = input(f"Enter input file path (or press Enter for default: {default_input_file}): ").strip() or default_input_file
    output_file = input(f"Enter output file path (or press Enter for default: {default_output_file}): ").strip() or default_output_file
    
    print(f"\n{Fore.CYAN}Input file: {input_file}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Output file: {output_file}{Style.RESET_ALL}\n")
    
    try:
        with open(input_file, 'r') as f:
            sites = f.read().splitlines()
    except Exception as e:
        logging.error(f"Error reading {input_file}: {e}")
        print(f"{Fore.RED}Error reading {input_file}: {e}{Style.RESET_ALL}")
        return
    
    writable_count = 0
    with tqdm(total=len(sites), desc="Testing write permission", ncols=100, unit="site") as pbar:
        for site_url in sites:
            if test_write_permission(site_url, auth_info):
                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write(f"{site_url}\n")
                writable_count += 1
            pbar.update(1)
    
    logging.info(f"Found {writable_count} writable spaces out of {len(sites)} sites.")
    print(f"\n{Fore.LIGHTGREEN_EX}Found {writable_count} writable spaces out of {len(sites)} sites.{Style.RESET_ALL}")
    print(f"{Fore.LIGHTGREEN_EX}Writable spaces saved to {output_file}{Style.RESET_ALL}")

if __name__ == "__main__":
    print(f"{Fore.YELLOW}This script should be run from the main.py file.{Style.RESET_ALL}")
import json
import urllib3, os
import random
import logging
from datetime import datetime, timedelta
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.fields.user_value import FieldUserValue
from office365.runtime.client_request_exception import ClientRequestException
from random import choice
from tqdm import tqdm
from colorama import Fore, Style, init

init(autoreset=True)  # Initialize colorama

urllib3.disable_warnings()

def disable_ssl(request):
    request.verify = False  # Disable certification verification

def get_random_filename(template_name):
    if template_name.endswith('.vault'):
        ext_list = ['vault', 'kdbx', 'kdb', 'kpdx', 'mscx', 'msim', 'dash', '1PUX']
        wordlist_path = 'wordlists/passwdvault_filenames.txt'
    elif template_name.endswith('.db'):
        ext_list = ['sql', 'db', 'sqlite', 'sqlite3', 'odb', 'OQY']
        wordlist_path = 'wordlists/sql_filenames.txt'
    elif template_name.endswith('.conf'):
        ext_list = ['cnf', 'conf', 'cfg', 'config']
        wordlist_path = 'wordlists/config_filenames.txt'
    elif template_name.endswith('.pst'):
        ext_list = ['pst', 'ost', 'msg']
        wordlist_path = 'wordlists/outlook_filenames.txt'
    elif template_name.endswith('.bak'):
        ext_list = ['bak', 'sql', 'bak2', 'backup', 'iso', 'old', 'bckp', 'vbox-prev', 'img', 'dmg', 'dd', 'vhd', 'edb', 'dat']
        wordlist_path = 'wordlists/backup_filenames.txt'
    elif template_name.endswith('.key'):
        ext_list = ['key', 'pem', 'pfx', 'pem', 'ppk']
        wordlist_path = 'wordlists/keys_filenames.txt'
    elif template_name.endswith('.zip') or template_name.endswith('.7z'):
        ext_list = ['zip', '7z', 'gzip', 'tar', 'tar.gz']
        wordlist_path = 'wordlists/archive_filenames.txt'
    elif template_name.endswith('.doc') or template_name.endswith('.docx'):
        ext_list = ['doc', 'docx']
        wordlist_path = 'wordlists/document_filenames.txt'
    elif template_name.endswith('.csv'):
        ext_list = ['csv']
        wordlist_path = 'wordlists/csv_filenames.txt'
    else:
        ext_list = []
        wordlist_path = ''

    if wordlist_path:
        with open(wordlist_path, 'r') as f:
            words = f.readlines()
        filename = choice(words).strip() + "." + choice(ext_list)
        return filename
    return None

def get_site_owner(client):
    try:
        web = client.web.get().expand(["Author"]).execute_query()
        return web.author
    except Exception as e:
        logging.error(f"Unable to get site owner, an error occurred: {e}")
        print(f"Error getting site owner: {e}")
        return None

def generate_random_datetime(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds())),
    )

def update_file_metadata(client, list_title, file_name, new_author, new_created_date, new_modified_date):
    try:
        target_list = client.web.lists.get_by_title(list_title)
        items = target_list.items.get().filter(f"FileLeafRef eq '{file_name}'").execute_query()
        
        if len(items) == 0:
            print(f"File '{file_name}' not found.")
            return False
        
        item_to_update = items[0]
        
        update_data = {
            "Editor": FieldUserValue.from_user(new_author),
            "Modified": new_modified_date,
            "Created": new_created_date,
            "Author": FieldUserValue.from_user(new_author),
        }
        
        result = item_to_update.validate_update_list_item(
            update_data,
            dates_in_utc=True,
            new_document_update=True,
        ).execute_query()

        has_any_error = any([item.HasException for item in result.value])
        if has_any_error:
            print("Item update completed with errors, for details refer 'ErrorMessage' property")
            for item in result.value:
                if item.HasException:
                    print(f"Error: {item.ErrorMessage}")
            return False
        else:
            return True
    except Exception as e:
        logging.error(f"Error updating file metadata, an error occurred: {e}")
        print(f"Error updating file metadata: {e}")
        return False
    
def write_to_output_file(file_path, content):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'a') as f:
        f.write(content + '\n')

def deploy_honeytokens(auth_info, templates_folder, writable_spaces):
    output_file = 'output/deployed_tokens.txt'
    logging.info("Starting deployment of decoys")
    for space in tqdm(writable_spaces, desc="Deploying honeytokens", unit="site"):
        print(f"\n{Fore.CYAN}Attempting to deploy honeytoken to {space}{Style.RESET_ALL}")
        if auth_info[0] == 'user_pass':
            _, username, password, _ = auth_info
            ctx = ClientContext(space).with_credentials(UserCredential(username, password))
        else:  # Azure app auth
            _, cert_settings, tenant, _ = auth_info
            ctx = ClientContext(space).with_client_certificate(tenant, **cert_settings)

        ctx.pending_request().beforeExecute += disable_ssl

        try:
            default_lib = ctx.web.default_document_library().get().execute_query()
            print(f"{Fore.WHITE}Found default document library: {default_lib.properties['Title']}{Style.RESET_ALL}")
        except ClientRequestException as e:
            logging.error(f"Error accessing default document library: {e}")
            print(f"{Fore.RED}Error accessing default document library: {e}{Style.RESET_ALL}")
            continue

        site_owner = get_site_owner(ctx)
        if not site_owner:
            print(f"{Fore.RED}Couldn't get site owner for {space}. Skipping...{Style.RESET_ALL}")
            continue
        
        # Choose one random template file
        templates = [t for t in os.listdir(templates_folder) if t.startswith('template')]
        if not templates:
            print(f"{Fore.RED}No template files found in {templates_folder}. Skipping...{Style.RESET_ALL}")
            continue
        
        template = random.choice(templates)
        random_filename = get_random_filename(template)
        if random_filename:
            template_path = os.path.join(templates_folder, template)
            try:
                with open(template_path, 'rb') as file_content:
                    file_content_bytes = file_content.read()
                    uploaded_file = ctx.web.default_document_library().root_folder.upload_file(random_filename, file_content_bytes).execute_query()
                print(f"{Fore.GREEN}Deployed honeytoken {random_filename} to {space}{Style.RESET_ALL}")

                # Generate new dates
                current_time = datetime.utcnow()
                start_date = current_time - timedelta(days=365*3)  # 3 years ago
                end_date = current_time - timedelta(days=30)  # 1 month ago

                new_created_date = generate_random_datetime(start_date, end_date)
                new_modified_date = generate_random_datetime(new_created_date, current_time)

                # Update file metadata
                update_success = update_file_metadata(ctx, default_lib.properties['Title'], random_filename, site_owner, new_created_date, new_modified_date)
                if update_success:
                    print(f"{Fore.WHITE}Attempting to Update metadata for {random_filename}{Style.RESET_ALL}")
                    # Write to output file
                    write_to_output_file(output_file, f"{space}/{random_filename}")
                else:
                    print(f"{Fore.RED}Failed to update metadata for {random_filename}{Style.RESET_ALL}")
            except ClientRequestException as e:
                print(f"{Fore.RED}Error uploading {random_filename} to {space}: {e}{Style.RESET_ALL}")
                print(f"{Fore.RED}Response content: {e.response.content if e.response else 'No response content'}{Style.RESET_ALL}")
                continue

def main(auth_info):
    templates_folder = 'templates'
    with open('output/writable_spaces.txt', 'r') as f:
        writable_spaces = [line.strip() for line in f]

    deploy_honeytokens(auth_info, templates_folder, writable_spaces)
    print(f"\n{Fore.YELLOW}Deployment complete. Output written to 'output/deployed_tokens.txt'{Style.RESET_ALL}")
    logging.info("Deployment complete. Output written to deployed_tokens.txt")

if __name__ == "__main__":
    print("This script should be run from the main.py file.")
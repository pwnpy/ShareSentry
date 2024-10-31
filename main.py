import logging
from logging.handlers import RotatingFileHandler
from typing import Tuple, Dict, Optional
from dotenv import load_dotenv
import os
import colorama
from colorama import Fore, Back, Style
from pyfiglet import Figlet

# Initialize colorama
colorama.init(autoreset=True)

# Load environment variables
load_dotenv()

def setup_logging():
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Set up logging to file
    file_handler = RotatingFileHandler(
        'logs/Audit.log', 
        maxBytes=1024 * 1024 * 5,  # 5 MB
        backupCount=5
    )
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Configure the root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler]
    )

    # Create a separate logger for console output
    console_logger = logging.getLogger('console')
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    console_logger.addHandler(console_handler)
    console_logger.setLevel(logging.INFO)

    return console_logger

def print_banner():
    f = Figlet(font='slant')
    print(Fore.CYAN + f.renderText('ShareSentry'))
    print(Fore.CYAN + "Defend, Discover, Deploy")
    print(Fore.YELLOW + "SharePoint Recon & Deception Tool")
    print(Fore.YELLOW + "=" * 50)
    print(Style.RESET_ALL)

def get_credentials() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    try:
        username = os.getenv('SHAREPOINT_USERNAME')
        password = os.getenv('SHAREPOINT_PASSWORD')
        url = input("Enter the SharePoint site URL (e.g., https://your-tenant.sharepoint.com): ").strip()
        if not all([username, password, url]):
            raise ValueError("Missing SharePoint credentials in environment variables")
        return username, password, url
    except Exception as e:
        logging.error(f"Error loading credentials: {e}")
        return None, None, None

def get_azure_credentials() -> Tuple[Optional[Dict], Optional[str], Optional[str]]:
    try:
        client_id = os.getenv('AZURE_CLIENT_ID')
        thumbprint = os.getenv('AZURE_THUMBPRINT')
        cert_path = input("Enter the path to the Azure certificate (e.g., config/Azure.pem): ").strip()
        tenant = os.getenv('AZURE_TENANT')
        site_url = input("Enter the SharePoint site URL (e.g., https://your-tenant.sharepoint.com): ").strip()
        
        if not all([client_id, thumbprint, cert_path, tenant, site_url]):
            raise ValueError("Missing Azure credentials in environment variables")
        
        return {
            'client_id': client_id,
            'thumbprint': thumbprint,
            'cert_path': cert_path
        }, tenant, site_url
    except Exception as e:
        logging.error(f"Error loading Azure credentials: {e}")
        return None, None, None

def get_auth_method() -> str:
    while True:
        print(Fore.CYAN + "\nChoose authentication method:")
        print(Fore.WHITE + "1. Username/Password")
        print(Fore.WHITE + "2. Azure AD App")
        choice = input(Fore.GREEN + "Enter your choice (1/2): " + Style.RESET_ALL)
        if choice in ['1', '2']:
            return choice
        print(Fore.RED + "Invalid choice. Please enter 1 or 2.")

def authenticate() -> Optional[Tuple]:
    auth_method = get_auth_method()
    
    if auth_method == '1':
        username, password, url = get_credentials()
        if username and password and url:
            return ('user_pass', username, password, url)
    else:
        cert_settings, tenant, site_url = get_azure_credentials()
        if cert_settings and tenant and site_url:
            return ('azure', cert_settings, tenant, site_url)
    
    logging.error("Authentication failed. Please check your credentials.")
    print(Fore.RED + "Authentication failed. Please check your credentials.")
    return None

def run_script(script_name: str, auth_info: Tuple):
    try:
        print(Fore.CYAN + f"\nRunning...\n")
        module = __import__(f"scripts.{script_name[:-3]}", fromlist=['main'])
        if script_name == 'deploy_honeytokens.py':
            print(Fore.YELLOW + "Warning: Please ensure you have high privileges or FullControl over the selected sites (You can use Site.Selected)" + Style.RESET_ALL)
            print(Fore.YELLOW + "File metadata will not change if there are insufficient privileges" + Style.RESET_ALL)
            print("This can be granted in the Azure (Entra ID) API permissions.")
            confirm = input("Are you sure you want to continue? (y/n): ")
            if confirm.lower() != 'y':
                print(Fore.RED + "Deployment cancelled" + Style.RESET_ALL)
                return
        module.main(auth_info)
        #print(Fore.GREEN + f"{script_name} completed successfully.")
    except ImportError as e:
        logging.error(f"Failed to import script {script_name}: {e}")
        print(Fore.RED + f"Failed to import script {script_name}: {e}")
    except Exception as e:
        logging.error(f"Error running script {script_name}: {e}")
        print(Fore.RED + f"Error running script {script_name}: {e}")

def main():
    setup_logging()
    print_banner()
    
    auth_info = authenticate()
    if not auth_info:
        return

    options = {
        '1': ('scan_sharepoint.py', "Scan SharePoint for sensitive files"),
        '2': ('identify_sites.py', "Identify all SharePoint sites the account is a member of"),
        '3': ('identify_writable_spaces.py', "Check write permissions on identified SharePoint sites"),
        '4': ('deploy_honeytokens.py', "Deploy honeytokens"),
        '5': (None, "Exit")
    }

    while True:
        print(Fore.CYAN + "\nSelect an option:")
        for key, (_, description) in options.items():
            print(Fore.WHITE + f"{key}. {description}")
        
        choice = input(Fore.GREEN + "Enter your choice: " + Style.RESET_ALL)

        if choice not in options:
            print(Fore.RED + "Invalid choice. Please try again.")
            continue

        script, _ = options[choice]
        if script is None:
            print(Fore.YELLOW + "Exiting ShareSentry. Goodbye!")
            break

        run_script(script, auth_info)

if __name__ == "__main__":
    main()
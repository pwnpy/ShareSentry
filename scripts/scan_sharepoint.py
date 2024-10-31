import urllib3
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from typing import List, Set, Tuple, Optional, Dict
from datetime import datetime
import logging
from tqdm import tqdm
import os
import time
import json
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich import print as rprint
from pathlib import Path

# Configure urllib3
urllib3.disable_warnings()

# Initialize Rich console
console = Console()

class SharePointScanner:
    def __init__(self, ctx: ClientContext, auth_type: str = 'user_pass'):
        self.ctx = ctx
        self.ctx.pending_request().beforeExecute += self._disable_ssl
        self.auth_type = auth_type
        self.last_request_time = 0
        # Set rate limit based on auth type
        self.request_limit = 0.1 if auth_type == 'user_pass' else 0.04  # 10 req/s or 25 req/s

    @staticmethod
    def _disable_ssl(request):
        """Disable SSL verification for the request."""
        request.verify = False

    def _throttle_request(self):
        """Implement request throttling based on auth type."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_limit:
            time.sleep(self.request_limit - time_since_last)
        self.last_request_time = time.time()

    def get_keywords(self, keywords_file: str = 'config/keywords.txt') -> List[str]:
        """Load keywords from a file."""
        try:
            with open(keywords_file, 'r') as f:
                keywords = [k.strip() for k in f.read().splitlines() if k.strip()]
            logging.info(f"Successfully loaded {len(keywords)} keywords from {keywords_file}")
            return keywords
        except Exception as e:
            logging.error(f"Error loading keywords from {keywords_file}: {e}")
            return []

    def get_predefined_queries(self, queries_file: str = 'queries.md') -> Dict[str, str]:
        """Load predefined queries from markdown/text file."""
        try:
            queries = {}
            current_title = None
            current_query = []
            
            with open(queries_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('##'):  # Query title
                        if current_title and current_query:
                            queries[current_title] = ' '.join(current_query)
                        current_title = line.lstrip('#').strip()
                        current_query = []
                    elif line and not line.startswith('#'):  # Query content
                        current_query.append(line)
                
                # Add last query
                if current_title and current_query:
                    queries[current_title] = ' '.join(current_query)
            
            logging.info(f"Successfully loaded {len(queries)} predefined queries")
            return queries
        except Exception as e:
            logging.error(f"Error loading predefined queries: {e}")
            return {}

    def custom_query(self) -> str:
        """Build a custom search query based on user input."""
        try:
            custom_keywords = [k.strip() for k in Prompt.ask("Enter custom keywords [cyan](separated by comma)").split(',')]
            logic_operator = Prompt.ask(
                "Choose logic operator", 
                choices=["AND", "OR", "BOTH"], 
                default="OR"
            )
            
            if logic_operator == "BOTH":
                query = Prompt.ask("Enter your custom query (Keywords + operator only. Do not input date range and file extensions as it is previously set)")
            else:
                # Wrap keywords in quotes and join with logic operator
                query = f" {logic_operator} ".join(f'"{k}"' for k in custom_keywords if k)
                query = f"({query})"
            
            logging.info(f"Custom query created: {query}")
            return query
        except Exception as e:
            logging.error(f"Error creating custom query: {e}")
            raise

    def search_files(
        self, 
        query: str, 
        extensions: Optional[List[str]] = None, 
        last_modified: Optional[str] = None,
        row_limit: int = 500
    ) -> List[str]:
        """Search for files in SharePoint based on given criteria."""
        files: Set[str] = set()
        start_row = 0
        more_results = True
        total_processed = 0

        with console.status("[bold green]Searching SharePoint...") as status:
            while more_results:
                try:
                    # Apply throttling
                    self._throttle_request()
                    
                    # Build search query
                    search_query = query
                    if extensions:
                        ext_query = f" AND ({' OR '.join([f'FileExtension:{ext}' for ext in extensions])})"
                        search_query += ext_query
                    if last_modified:
                        search_query += f" AND {last_modified}"
                    
                    results = (self.ctx.search
                             .post_query(query_text=search_query, row_limit=row_limit, start_row=start_row)
                             .execute_query()
                             .value
                             .PrimaryQueryResult
                             .RelevantResults)
                    
                    result_count = len(results.Table.Rows)
                    if result_count > 0:
                        for row in results.Table.Rows:
                            files.add(row.Cells["Path"])
                        total_processed += result_count
                        status.update(f"[bold green]Found {total_processed} files...")
                        start_row += row_limit
                    else:
                        more_results = False
                        
                except Exception as e:
                    logging.error(f"Error during search at row {start_row}: {e}")
                    break

        logging.info(f"Search completed. Found {len(files)} unique files")
        return list(files)

def get_search_type() -> str:
    """Get search type from user."""
    console.print("\n[cyan]Search Type:[/cyan]")
    console.print("1. Use predefined queries (recommended)")
    console.print("2. Use predefined keywords from keywords.txt")
    console.print("3. Enter custom keywords and logic")
    
    search_type = Prompt.ask(
        "\nChoose search type",
        choices=["1", "2", "3"],
        default="1"
    )

    return {
        "1": "predefined_queries",
        "2": "predefined",
        "3": "custom"
    }[search_type]

def get_file_extensions() -> List[str]:
    """Get and validate file extensions input from user."""
    console.print("\n[cyan]File Extensions:[/cyan]")
    console.print("Specify which file extensions to search for.")
    console.print("Default extensions: txt, doc, docx, xls, xlsx, json")
    console.print("Example: Enter 'docx,pdf' to search only for Word and PDF files")
    
    extensions_input = Prompt.ask(
        "\nEnter file extensions to search for (comma-separated)",
        default="txt,doc,docx,xls,xlsx,json"
    )
    
    extensions = [ext.strip().lower() for ext in extensions_input.split(',') if ext.strip()]
    
    if not extensions:
        raise ValueError("At least one file extension must be specified")
    
    console.print(f"\n[green]Will search for files with extensions: {', '.join(extensions)}[/green]")
    return extensions

def get_date_range() -> str:
    """Get and validate date range input from user."""
    console.print("\n[cyan]Date Range:[/cyan]")
    console.print("Specify the time period for the search.")
    console.print("Options:")
    console.print("1. Press Enter to search for files modified 'this year'")
    console.print("2. Enter a date range in format: YYYY-MM-DD,YYYY-MM-DD")
    console.print("   Example: 2024-01-01,2024-04-26")
    
    last_modified_input = Prompt.ask(
        "\nEnter last modified time interval",
        default="this year",
        show_default=True
    )

    if not last_modified_input or last_modified_input.lower() == 'this year':
        console.print("[green]Using default: Files modified this year[/green]")
        return 'LastModifiedTime="this year"'

    try:
        if ',' in last_modified_input:
            start_date, end_date = last_modified_input.split(',')
            # Validate dates
            datetime.strptime(start_date.strip(), '%Y-%m-%d')
            datetime.strptime(end_date.strip(), '%Y-%m-%d')
            date_range = f'LastModifiedTime>={start_date.strip()} AND LastModifiedTime<={end_date.strip()}'
            console.print(f"[green]Searching for files modified between {start_date.strip()} and {end_date.strip()}[/green]")
            return date_range
    except ValueError as e:
        logging.error(f"Invalid date format: {e}")
        console.print("[red]Invalid date format. Using default 'this year'[/red]")
        return 'LastModifiedTime="this year"'

def save_results(files: List[str], output_file: str, query_title: Optional[str] = None):
    """Save search results to file."""
    with open(output_file, 'a', encoding='utf-8') as f:
        if query_title:
            f.write(f"\nQuery: {query_title}\n")
            f.write("-" * 80 + "\n")
        for file in files:
            f.write(f"{file}\n")
        if query_title:
            f.write("\n")

def main(auth_info: Tuple):
    # Display banner
    console.print(Panel.fit(
        "[bold green]SharePoint Scanner[/bold green]\n"
        "[yellow]Scan for sensitive files across SharePoint sites[/yellow]",
        border_style="blue"
    ))

    try:
        # Initialize SharePoint context
        auth_type, *auth_details = auth_info
        if auth_type == 'user_pass':
            _, username, password, url = auth_info
            ctx = ClientContext(url).with_credentials(UserCredential(username, password))
        else:  # Azure app auth
            _, cert_settings, tenant, url = auth_info
            ctx = ClientContext(url).with_client_certificate(tenant, **cert_settings)

        scanner = SharePointScanner(ctx, auth_type)

        # Get search type first
        search_type = get_search_type()

        # Get output file path
        console.print("\n[cyan]Output File:[/cyan]")
        console.print("Press Enter to use default output_search.txt")
        console.print("Or specify custom output file path")
        
        output_file = Prompt.ask(
            "Enter output file path",
            default="output/output_search.txt"
        )

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Clear previous content if file exists
        if os.path.exists(output_file):
            open(output_file, 'w').close()

        if search_type == "predefined_queries":
            # Load predefined queries
            queries = scanner.get_predefined_queries()
            if not queries:
                raise ValueError("No predefined queries found")

            console.print("\n[cyan]Running predefined queries...[/cyan]")
            for title, query in queries.items():
                console.print(f"\n[yellow]Running query: {title}[/yellow]")
                files = scanner.search_files(query)
                save_results(files, output_file, title)
                
        else:
            # Get file extensions and date range for other search types
            extensions = get_file_extensions()
            last_modified = get_date_range()

            if search_type == "predefined":
                # Allow custom keywords file
                console.print("\n[cyan]Keywords File:[/cyan]")
                console.print("Press Enter to use default keywords.txt")
                console.print("Or specify path to your custom keywords file")
                
                keywords_file = Prompt.ask(
                    "Enter path to keywords file",
                    default="keywords.txt"
                )
                
                keywords = scanner.get_keywords(keywords_file)
                if not keywords:
                    raise ValueError("No keywords found in the specified file")
                query = " OR ".join(f'"{k}"' for k in keywords)
                console.print(f"\n[green]Using {len(keywords)} keywords from file[/green]")
            else:  # custom
                query = scanner.custom_query()

            # Perform search
            console.print("\n[cyan]Searching SharePoint...[/cyan]")
            files = scanner.search_files(query, extensions, last_modified)
            save_results(files, output_file)

        console.print(f"\n[green]✓[/green] Search completed. Results saved to: {output_file}")
        logging.info(f"Search completed. Results saved to {output_file}")

    except Exception as e:
        logging.error(f"Error in main execution: {e}")
        console.print(f"[red]Error: {str(e)}[/red]")
        return

if __name__ == "__main__":
    console.print("[yellow]This script should be run from the main.py file.[/yellow]")
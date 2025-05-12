"""
This script checks the availability of URLs listed in a JSON file. It reads the JSON file,
parses the sections containing URLs, and performs HTTP GET requests to verify their status.
JSON File Format:
The JSON file should be structured as follows:
{
    "Section Heading 1": [
        {
            "url": "http://example.com",
            "description": "Example website"
        },
        {
            "url": "http://another-example.com",
            "description": "Another example website"
        }
    ],
    "Section Heading 2": [
        {
            "url": "http://example2.com",
            "description": "Second example website"
        }
    ]
}
Functions:
- read_json_file(file_path): Reads a JSON file from the specified file path and returns its content.
- check_urls(sections): Iterates through the sections and URLs, checking their availability and printing the results.
- main(): The entry point of the script. Reads the JSON file path from the command line arguments, parses the file, and checks the URLs.
Usage:
Run the script from the command line with the path to the JSON file as an argument:
    python web-checker.py <json_file_path>
"""

from datetime import datetime
import json
from jsonschema import validate, ValidationError
import requests
import sys
import urllib3
from rich import print
from fpdf import FPDF
from fpdf.enums import XPos, YPos

class PDF(FPDF):
    # Set up functions to create the PDF
    # Using functions makes it easier to modify the PDF and maintain a consistent style
    # Define the header and footer
    def header(self):
        try:
            self.image("logo.png", 10, 8, 33)
        except:
            print("[bold red]Logo not found, skipping[/bold red]")
        self.set_font("Helvetica", style="B", size=8)
        self.cell(0, 10, "Web Checker Report", 0, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", style="I", size=8)
        self.cell(0,10,f"page {self.page_no()}",0,align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Define a section title, used at the start of each section
    def heading(self, title=str):
        self.set_y(self.get_y() + 1)
        self.set_font("Helvetica", style="B", size=12)
        self.cell(text=title, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_y(self.get_y() + 0.5)

    # Define the sub heading
    def subheading(self, title=str):
        self.set_y(self.get_y() + 0.25)
        self.set_font("Helvetica", style="B", size=10)
        self.cell(0, 6, title, 0, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_y(self.get_y() + 1)

    # Define the body text
    def paragraph(self, text=str, textStyle=None):
        self.set_y(self.get_y() + 0.25)
        if textStyle:
            self.set_font("Helvetica", style=textStyle, size=10)
        else:
            self.set_font("Helvetica", size=10)
        self.multi_cell(0, 6, text, 0, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Define a horizontal line
    def horizontal_line(self):
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())


def generatePDF(runInfo, filename:str):
    """Generates a PDF file with the given text and filename."""
    lineSpace = 6
    pdf = PDF()
    pdf.add_page()

    # Create metadata for the PDF
    pdf.set_title("Web Proxy Checker Report")

    if "engineer" in runInfo or "company" in runInfo:
        pdf.heading("Report Information")

    if "engineer" in runInfo:
        pdf.set_font("Helvetica", size=10)
        pdf.paragraph(f"Report run by: {runInfo['engineer']}")
        pdf.set_author(runInfo["engineer"])

    if "company" in runInfo:
        pdf.set_font("Helvetica", size=10)
        pdf.paragraph(f"Company: {runInfo['company']}")
        pdf.set_keywords(runInfo["company"])
        pdf.set_subject(f'Report run for {runInfo["company"]} on {runInfo["date"]}')

    if "date" in runInfo:
        pdf.set_font("Helvetica", size=10)
        pdf.paragraph(f"Date: {runInfo['date']}")
    
    if "engineer" in runInfo or "company" in runInfo or "date" in runInfo:
        # Draw a horizontal line to seperate the sections
        pdf.horizontal_line()
        pdf.cell(0, lineSpace, "", 0, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    if "extendedChecks" in runInfo:
        # Print the extended checks
        if "PUBLIC-IP" in runInfo["extendedChecks"]:
            # Print the result of the public IP check
            pdf.heading("Public IP information from the test device")
            pdf.paragraph(f"Public IP: {runInfo['extendedChecks']['PUBLIC-IP']['ip']}")
            pdf.paragraph(f"Provider: {runInfo['extendedChecks']['PUBLIC-IP']['org']}")
            pdf.paragraph(f"Location: {runInfo['extendedChecks']['PUBLIC-IP']['loc']}")
            pdf.paragraph(f"City: {runInfo['extendedChecks']['PUBLIC-IP']['city']}")
            pdf.paragraph(f"Region: {runInfo['extendedChecks']['PUBLIC-IP']['region']}")
            pdf.paragraph(f"Country: {runInfo['extendedChecks']['PUBLIC-IP']['country']}")
            pdf.paragraph(f"Timezone: {runInfo['extendedChecks']['PUBLIC-IP']['timezone']}")

        if  "tlsVersions" in runInfo["extendedChecks"]:
            # Print the result of the TLS version checks
            pdf.heading("TLS Version Checks")
            pdf.paragraph("This test checks which versions of TLS are permitted, versions 1.0 and 1.1 are considered insecure so should be blocked.")
            
            for tlsCheck in runInfo["extendedChecks"]["tlsVersions"]:
                pdf.paragraph(f"{tlsCheck['version']} - {lookup_error_code(tlsCheck['status'])}")
        
        if "EICAR" in runInfo["extendedChecks"]:
            # Print the result of the EICAR check
            pdf.heading("EICAR Virus Check")
            if runInfo["extendedChecks"]["EICAR"]:
                pdf.paragraph("EICAR test file downloaded successfully. Whilst the EICAR file is not an active virus this shows that your proxy settings have allowed the virus to be downloaded to the test PC.", "BI")
            else:
                pdf.paragraph("The EICAR test file failed to dowload, this is an indication that it has been blocked.")
    
    # Print the URL checks
    if "urlChecks" in runInfo:
        # Print the heading
        pdf.heading("URL tests")
        for category in runInfo["urlChecks"]:
            # Print the category heading
            pdf.subheading(f"Category: {category['category']}")
            for urls in category["urls"]:
                url = urls['url']
                description = urls['description']
                status = urls['status']
                pdf.paragraph(f"{description} ({url}) - {lookup_error_code(status)} ({status})")

    # Write the PDF
    pdf.output(filename)


def lookup_error_code(code):
    """Lookup the error code and return the description."""
    try:
        error_codes = {
            200: "OK",
            201: "Created",
            202: "Accepted",
            204: "No Content",
            301: "Moved Permanently",
            302: "Found",
            303: "See Other",
            304: "Not Modified",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            408: "Request Timeout",
            429: "Too Many Requests",
            500: "Internal Server Error"
        }
        return error_codes.get(code, "Unknown Error")
    except Exception as e:
        return "Unknown Error"

def read_json_file(file_path):
    """Reads a JSON file and returns its content.
    Data is validated against the schema defined in web-checker-schema.json.
    The JSON file should contain sections with URLs and descriptions.
    """
    try:
        print(f"Reading configuration file: {file_path} ", end="")
        with open("web-checker-schema.json") as s, open(file_path) as d:
            try:
                schema = json.load(s)
            except json.JSONDecodeError as e:
                print(f"[bold red]Error reading schema file: {e}[/bold red]")
                sys.exit(1)
            try:
                data = json.load(d)
            except json.JSONDecodeError as e:
                print(f"[bold red]Error reading JSON file: {e}[/bold red]")
                sys.exit(1)
        try:
            validate(instance=data, schema=schema)
            print("[bold green]configuration valid[/bold green]")
            return data
        
        except ValidationError as e:
            print("[bold red]Invalid configuration:[/bold red]", e.message)
            print("Diagnostic information:")
            print("Path    :", list(e.path))
            print("Schema  :", e.schema_path)
            sys.exit(1)
    except FileNotFoundError as e:
        print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[bold red]Error reading JSON file: {e}[/bold red]")
        sys.exit(1)
    except Exception as e:
        print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)

def check_urls(sections):
    """Checks the URLs in each section and prints the results.
    Each section is checked for the availability of its URLs.
    The results are printed to the console.
    """
    try:
        results = []
        for section_heading, urls in sections.items():
            print(f"  Category: [bold]{section_heading}[/bold]")
            sectionCheck = {}
            sectionCheck["category"] = section_heading
            urlChecks=[]
            for url_info in urls:
                urlCheck = {}
                url = url_info.get("url")
                description = url_info.get("description", "No description provided")
                print(f"    Checking {description}: {url}", end="")
                try:
                    response = requests.get(url, timeout=5, verify=False)
                    if response.status_code == 200:
                        # URL connected successfully
                        print("[bold green]    OK ({})[/bold green]".format(response.status_code))
                        urlCheck["url"] = url
                        urlCheck["description"] = description
                        urlCheck["status"] = response.status_code
                    else:
                        # URL returned an error status code
                        print(f"[bold red]    Error: {lookup_error_code(response.status_code)} ({response.status_code})[/bold red]")
                        urlCheck["url"] = url
                        urlCheck["description"] = description
                        urlCheck["status"] = response.status_code
                except requests.RequestException as e:
                    # URL connection failed, display the error
                    print(f"    Connection error: {e}")
                urlChecks.append(urlCheck)
            sectionCheck["urls"] = urlChecks
            results.append(sectionCheck)
        return results
    except Exception as e:
        print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)

def check_TLSversions():
    """Check the TLS versions supported by the server.
    This function checks the TLS versions supported by the server by making requests to specific URLs.
    The URLs used for the checks are:
    - https://tls10.browserleaks.com/
    - https://tls11.browserleaks.com/
    - https://tls12.browserleaks.com/
    - https://tls13.browserleaks.com/
    """
    try:
        tlsChecks = []
        tlsVersions=["TLSv1.0", "TLSv1.1", "TLSv1.2", "TLSv1.3"]
        # loop through the different TLS versions
        for tlsVersion in tlsVersions:
            tlsCheck = {}
            tlsCheck["version"] = tlsVersion
            # Set the URL for each check
            match tlsVersion:
                case "TLSv1.0":
                    url="https://tls10.browserleaks.com/"
                case "TLSv1.1":
                    url="https://tls11.browserleaks.com/"
                case "TLSv1.2":
                    url="https://tls12.browserleaks.com/"
                case "TLSv1.3":
                    url="https://tls13.browserleaks.com/"    
            print(f'    Checking TLS version: {tlsVersion} (URL: {url}) ', end='')
            try:
                response = requests.get(url, timeout=5, verify=False)
                if response.status_code == 200:
                    print("[bold green]    OK ({})[/bold green]".format(response.status_code))
                    tlsCheck["status"] = response.status_code
                else:
                    print(f"[bold red]    Error: {lookup_error_code(response.status_code)} ({response.status_code})[/bold red]")
                    tlsCheck["status"] = response.status_code
            except requests.RequestException as e:
                # Handle connection errors
                print(f"Connection error: {e}")
                tlsCheck["status"] = "Connection error"
            tlsChecks.append(tlsCheck)
        return tlsChecks
    except Exception as e:
        print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)

def download_EICAR():
    """Download the EICAR test file to check for antivirus detection.
    The EICAR test file is a harmless file used to test antivirus software.
    It is designed to trigger antivirus alerts without being a real virus.
    Downloaded from https://secure.eicar.org/eicar.com.txt"""
    try:
        url = "https://secure.eicar.org/eicar.com.txt"
        print(f"  Downloading EICAR test file from {url} ", end="")
        try:
            response = requests.get(url, timeout=5, verify=False)
            #response.raise_for_status()
            if response.status_code == 200:
                print("[bold red]    OK[/bold red]",end="")
                with open("eicar.com.txt", "wb") as f:
                    f.write(response.content)
                print(" EICAR test file downloaded successfully.")
                print("[bold red]Please delete the file after testing.[/bold red]")
                return True
            else:
                print(f"[bold green]    Error: {lookup_error_code(response.status_code)} ({response.status_code})[/bold green]")
                return False
        except requests.RequestException as e:
            print(f"Connection error: {e}")
            return False
    except Exception as e:
        print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)

def check_public_ip():
    """Check the public IP of the connection """
    try:
        url = "https://api.ipify.org?format=json"
        print(f"  Checking public IP address using {url} ", end="")
        try:
            response = requests.get(url, timeout=5, verify=False)
            #response.raise_for_status()
            if response.status_code == 200:
                print("[bold green]    OK[/bold green]")
                data = response.json()
                print(f"     [bold blue]Public IP: {data['ip']}[/bold blue]")
                providerInfo = get_provider_info(data['ip'])
                return providerInfo
            else:
                print(f"[bold red]    Error: {lookup_error_code(response.status_code)} ({response.status_code})[/bold red]")
                return None
        except requests.RequestException as e:
            print(f"Connection error: {e}")
            return None
    except Exception as e:
        print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)

def get_provider_info(ip:str):
    """Check the provider of the public IP address using ipinfo.io
    The function retrieves information about the IP address, including the organization,
    location, city, region, country, and timezone.
    The information is printed to the console and returned as a dictionary.
    If the PC is behind a proxy, the IP address may not be the public IP of the PC.
    """
    try:
        url = f"https://ipinfo.io/{ip}/json"
        print(f"  Checking provider ", end="")
        try:
            providerInfo = {}
            response = requests.get(url, timeout=5, verify=False)
            #response.raise_for_status()
            if response.status_code == 200:
                print("[bold green]    OK[/bold green]")
                data = response.json()
                print(f"     [bold blue]{data['org']}[/bold blue]")
                print(f"     [bold blue]Location: {data['loc']}[/bold blue]")
                print(f"     [bold blue]City: {data['city']}[/bold blue]")
                print(f"     [bold blue]Region: {data['region']}[/bold blue]")
                print(f"     [bold blue]Region: {data['country']}[/bold blue]")
                print(f"     [bold blue]Region: {data['timezone']}[/bold blue]")
                providerInfo["ip"] = ip
                providerInfo["org"] = data['org']
                providerInfo["loc"] = data['loc']
                providerInfo["city"] = data['city']
                providerInfo["region"] = data['region']
                providerInfo["country"] = data['country']
                providerInfo["timezone"] = data['timezone']
                return providerInfo
            else:
                print(f"[bold red]    Error: {lookup_error_code(response.status_code)} ({response.status_code})[/bold red]")
                return None
        except requests.RequestException as e:
            print(f"Connection error: {e}")
            return None
    except Exception as e:
        print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)

def main():
    """Main function to run the web checker.
    It reads the JSON file path from the command line arguments,
    parses the file, and checks the URLs.
    The JSON file should be structured as described in the schema file web-checker-schema.json.
    The script outputs to the console and generates a PDF report with the results of the checks.
    """
    try:
        if len(sys.argv) < 2:

            #print("[bold red]Error: Missing JSON file path argument[/bold red]")
            #sys.exit(1)
            json_file_path = "test.json"
        else:
            json_file_path = sys.argv[1]
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        webcheck = read_json_file(json_file_path)
    
        print(f"Report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", end="")
        if webcheck.get("Engineer"):
            print(f" by {webcheck.get('Engineer', 'Not provided')}", end="")
        if webcheck.get("Company"):
            print(f" for {webcheck.get('Company', 'Not provided')}", end="")
        print("")
        try:
            extendedChecks = {}
            extended = webcheck.get("Extended Checks", {})
            if len(extended) > 0:
                print("Running extended checks")
                for check in extended:
                    if check.upper() == "TLS-VERSIONS":
                        extendedChecks['tlsVersions'] = check_TLSversions()
                    if check.upper() == "EICAR":
                        extendedChecks['EICAR'] = download_EICAR()
                    if check.upper() == "PUBLIC-IP":
                        extendedChecks['PUBLIC-IP'] = check_public_ip()

        except Exception as e:
            print(f"[bold red]Error: {e}[/bold red]")
            sys.exit(1)
        try:
            categories = webcheck.get("URL Checks", {})
            print("Running category checks")
            urlChecks = check_urls(categories)
        except Exception as e:
            print(f"[bold red]Error: {e}[/bold red]")
            sys.exit(1)
        try:
            # Do the PDF report
            runInfo = {}
            if "Engineer" in webcheck:
                runInfo["engineer"] = webcheck["Engineer"]
            if "Company" in webcheck:
                runInfo["company"] = webcheck["Company"]
            runInfo["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            runInfo["extendedChecks"] = extendedChecks
            runInfo["urlChecks"] = urlChecks
            print("Generating PDF report")
            pdf_filename = f"web-checker-report"
            if "company" in runInfo:
                pdf_filename = f"{pdf_filename}-{runInfo['company']}"
            pdf_filename = f'{pdf_filename}-{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.pdf'
            generatePDF(runInfo, pdf_filename)
            print(f"PDF report generated: {pdf_filename}")
        except Exception as e:
            print(f"[bold red]Error: {e}[/bold red]")
            sys.exit(1)
    except Exception as e:
        print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
        main()
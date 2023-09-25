from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.parse import urlparse, urljoin
from urllib.error import HTTPError
from collections import deque

# Define the URL you want to start scraping
initial_url = "https://www.qemu.org/"

def scrape_links(initial_url, max_depth):
    visited = set()
    queue = deque([(initial_url, 0)])

    while queue:
        url, depth = queue.popleft()

        if depth > max_depth:
            continue

        try:
            # Create a Request object and open the URL
            req = Request(url)
            html_page = urlopen(req)
        except HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason} - Skipping URL: {url}")
            continue

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_page, "lxml")

        # Define a list of extensions to exclude (e.g., ".pdf", ".jpg", ".png")
        excluded_extensions = [".pdf", ".jpg", ".png"]

        # Find all 'a' tags and extract the 'href' attribute
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                # Combine relative links with the base URL
                absolute_url = urljoin(url, href)
                # Check if the absolute URL starts with the desired prefix
                if absolute_url.startswith("https://www.qemu.org/"):
                    # Check if the URL does not end with any of the excluded extensions
                    if not any(absolute_url.endswith(ext) for ext in excluded_extensions):
                        visited.add(absolute_url)
                        queue.append((absolute_url, depth + 1))

    return visited

# Set the maximum depth for recursion
max_depth = 2

# Start the scraping process with the initial URL
unique_links = scrape_links(initial_url, max_depth)

# Define the path for the output file
output_file_path = "links.txt"

# Store the unique links in the specified file
with open(output_file_path, "w") as file:
    for link in unique_links:
        file.write(link + "\n")

print(f"Unique links from {initial_url} have been saved to {output_file_path}")

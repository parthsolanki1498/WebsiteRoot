from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.parse import urlparse, urljoin
from urllib.error import HTTPError
import csv
from collections import deque

# Define the URL you want to start scraping
initial_url = "https://www.qemu.org/"


def scrape_links(initial_url, max_depth):
    visited = set()  # Use a set to store unique links
    unique_links_list = []  # Use a list to preserve the order of unique links
    queue = deque([(initial_url, 0)])
    total_links = 0  # To keep track of the total number of links discovered

    # Create an empty dictionary for the interconnection matrix
    interconnection_matrix = {}

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
        index_page_title = "Index Page"
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                # Combine relative links with the base URL
                absolute_url = urljoin(url, href)
                # Check if the absolute URL starts with the desired prefix
                if absolute_url.startswith("https://www.qemu.org/"):
                    # Check if the URL does not end with any of the excluded extensions
                    if not any(absolute_url.endswith(ext) for ext in excluded_extensions):
                        unique_link = f"{index_page_title} - {depth} - {absolute_url}"
                        if unique_link not in visited:  # Check for uniqueness
                            visited.add(unique_link)
                            unique_links_list.append(unique_link)
                            queue.append((absolute_url, depth + 1))
                            total_links += 1
                            print(f"Discovered: {unique_link}")  # Print the discovered link

                            # Update the interconnection matrix
                            if url not in interconnection_matrix:
                                interconnection_matrix[url] = []
                            interconnection_matrix[url].append(absolute_url)

    return unique_links_list, interconnection_matrix


# Set the maximum depth for recursion
max_depth = 2

# Start the scraping process with the initial URL
unique_links, interconnection_matrix = scrape_links(initial_url, max_depth)

# Define the path for the output files
output_file_path = "links.txt"
interconnection_matrix_csv_path = "interconnection_matrix.csv"

# Store the unique links in the specified file
with open(output_file_path, "w") as file:
    for link in unique_links:
        file.write(link + "\n")

# Store the interconnection matrix in a CSV file
with open(interconnection_matrix_csv_path, "w", newline='') as csv_file:
    writer = csv.writer(csv_file)

    # Write header row
    header = [''] + list(interconnection_matrix.keys())
    writer.writerow(header)

    for page, connected_pages in interconnection_matrix.items():
        row = [page] + ['Y' if page in connected_pages else 'N' for page in interconnection_matrix.keys()]
        writer.writerow(row)

print(f"Unique links from {initial_url} have been saved to {output_file_path}")
print(f"Interconnection matrix has been saved to {interconnection_matrix_csv_path}")

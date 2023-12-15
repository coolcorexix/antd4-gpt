import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import psycopg2
from psqlConnection import startConnection, closeConnection

def is_valid_url(url):
    """
    Checks if the url is valid and belongs to the same domain
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_links(url, domain):
    """
    Returns all valid links on the given page
    """
    links = set()
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                continue
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if not is_valid_url(href) or domain not in href:
                continue
            links.add(href)
        return links
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return set()

# Function to insert multiple rows into the scanned_documents table
def insert_multiple(connection, data_list):
    try:
        cursor = connection.cursor()

        # Define the SQL query to insert data
        insert_query = """
        INSERT INTO scanned_document (href, text_content)
        VALUES (%s, %s)
        RETURNING id;
        """

        # Execute the SQL query for each row in the data_list
        for data in data_list:
            print(f"Inserting row: {data}")
            cursor.execute(insert_query, data)
        
        connection.commit()
        print(f"Inserted {len(data_list)} rows")

    except (Exception, psycopg2.Error) as error:
        print(f"Error while inserting data: {error}")
    finally:
        if cursor:
            cursor.close()


def main(start_url):
    """
    Crawl starting from the given URL
    """
    connection = startConnection()

    if connection:
        domain = urlparse(start_url).netloc
        counter = 0
        visited = set()
        urls_to_visit = {start_url}
        dataList=[]

        while urls_to_visit:
            current_url = urls_to_visit.pop()
            if current_url in visited:
                continue
            if counter == 2:
                break
            counter += 1
            print(f"Crawling: {current_url}")
            visited.add(current_url)
            links = get_all_links(current_url, domain)
            urls_to_visit = urls_to_visit.union(links)
            text =  extract_text_from_linked_page(current_url)
            dataList.append((current_url, text))

        insert_multiple(connection, dataList)
        closeConnection(connection)

def extract_text_from_linked_page(full_url):
    try:
        # Combine the base URL and the href to get the full URL
        full_url

        # Send an HTTP GET request to the linked page
        response = requests.get(full_url)
        response.raise_for_status()

        # Parse the HTML content of the linked page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract all the text content from the parsed HTML
        text_content = soup.get_text()

        return text_content
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":
    start_url = "https://4x.ant.design/"  # Replace with your starting URL
    main(start_url)
    
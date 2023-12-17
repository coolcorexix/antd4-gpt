from openai import OpenAI

client = OpenAI(api_key='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')
from psqlConnection import startConnection, closeConnection
import psycopg2
import numpy as np

def get_documents_to_process(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, text_content, token_count FROM scanned_document WHERE embeddings IS NULL")
        documents = cursor.fetchall()
        cursor.close()
        return documents
    except (Exception, psycopg2.Error) as error:
        print(f"Error while fetching data: {error}")
        return []

def generate_embeddings(text):
      # Replace with your OpenAI API key

    response = client.embeddings.create(input=text, model='text-embedding-ada-002')
    print(response)
    return response.data[0].embedding

def update_embeddings(connection, document_id, embeddings):
    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE scanned_document SET embeddings = %s WHERE id = %s", (embeddings, document_id))
        connection.commit()
        cursor.close()
    except (Exception, psycopg2.Error) as error:
        print(f"Error while updating data: {error}")

def main():
    connection = startConnection()
    if connection:
        documents = get_documents_to_process(connection)
        for document_id, text_content, token_count in documents:
            if not token_count or token_count > 8192:
                continue
            embeddings = generate_embeddings(text_content)
            update_embeddings(connection, document_id, embeddings)
        closeConnection(connection)

if __name__ == "__main__":
    main()

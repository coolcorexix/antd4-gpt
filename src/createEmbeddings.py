import openai
from psqlConnection import startConnection, closeConnection
import psycopg2
import numpy as np

def get_documents_to_process(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, text_content FROM scanned_document WHERE embeddings IS NULL")
        documents = cursor.fetchall()
        cursor.close()
        return documents
    except (Exception, psycopg2.Error) as error:
        print(f"Error while fetching data: {error}")
        return []

def generate_embeddings(text):
    openai.api_key = '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'  # Replace with your OpenAI API key

    response = openai.Embedding.create(
        input=text,
        engine="text-embedding-ada-002"  # Or another suitable engine
    )
    return response['data'][0]['embedding']

def update_embeddings(connection, document_id, embeddings):
    try:
        cursor = connection.cursor()
        embeddings_array = np.array(embeddings, dtype=float)
        cursor.execute("UPDATE scanned_document SET embeddings = %s WHERE id = %s", (embeddings_array, document_id))
        connection.commit()
        cursor.close()
    except (Exception, psycopg2.Error) as error:
        print(f"Error while updating data: {error}")

def main():
    connection = startConnection()
    if connection:
        documents = get_documents_to_process(connection)
        for document_id, text_content in documents:
            embeddings = generate_embeddings(text_content)
            update_embeddings(connection, document_id, embeddings)
        closeConnection(connection)

if __name__ == "__main__":
    main()

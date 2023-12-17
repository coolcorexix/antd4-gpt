from psqlConnection import startConnection, closeConnection
import psycopg2
from transformers import GPT2Tokenizer

def calculate_token_count(text):
    """
    Calculate the token count using GPT-2's tokenizer.
    """
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    tokens = tokenizer.encode(text, add_special_tokens=False)
    return len(tokens)

def update_token_count(connection, document_id, token_count):
    """
    Update the token_count in the scanned_document table for a specific document.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE scanned_document SET token_count = %s WHERE id = %s", (token_count, document_id))
        connection.commit()
        cursor.close()
    except (Exception, psycopg2.Error) as error:
        print(f"Error while updating token count: {error}")

def process_documents(connection):
    """
    Process each document to calculate and update the token count.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id, text_content FROM scanned_document WHERE token_count IS NULL")
        documents = cursor.fetchall()
        for document_id, text_content in documents:
            if text_content:
                token_count = calculate_token_count(text_content)
                update_token_count(connection, document_id, token_count)
        cursor.close()
    except (Exception, psycopg2.Error) as error:
        print(f"Error while processing documents: {error}")

def main():
    connection = startConnection()
    if connection:
        process_documents(connection)
        closeConnection(connection)

if __name__ == "__main__":
    main()
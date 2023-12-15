import psycopg2

def startConnection():
    try:
        connection = psycopg2.connect(
            host="127.0.0.1",
            database="antd4_gpt",
            user="postgres",
            password="postgres"
        )
        print("Connected to the database")
        return connection
    except (Exception, psycopg2.Error) as error:
        print(f"Error while connecting to PostgreSQL: {error}")
        return None
    
# Function to close a database connection
def closeConnection(connection):
    if connection:
        connection.close()
        print("Database connection closed")

def update_embeddings(connection, document_id, embeddings):
    try:
        cursor = connection.cursor()
        embeddings_array = np.array(embeddings, dtype=float)
        cursor.execute("UPDATE scanned_document SET embeddings = %s WHERE id = %s", (embeddings_array, document_id))
        connection.commit()
        cursor.close()
    except (Exception, psycopg2.Error) as error:
        print(f"Error while updating data: {error}")
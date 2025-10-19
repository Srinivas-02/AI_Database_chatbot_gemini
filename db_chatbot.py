import re
import os
from dotenv import load_dotenv
from google import genai
import psycopg2
load_dotenv()

client = genai.Client()


def getSql(client : genai.Client, question, chat_history):
    prompt = """
        You ae a Text-to-SQL assistant. Given a user's natural language question and the schema below, generate a valid and executable PostgreSQL query that answers the question. 

        ## General Instructions:
        - Always use **only the tables and columns** provided in the schema.
        - Be **concise and correct**, with proper SQL syntax.
        - Do **not add any assumptions** beyond the schema.
        - Use **JOINs, GROUP BY, ORDER BY, etc.** where needed.
        - Return **only the SQL query** and nothing else.
        - Refer to the schema below before answering.
        - Use the chat history attached to get the context of the current question , if it depends on any of previous chats.
        - If the requested question can't be converted to a valid sql with given schema - return - 'Invalid'

        ---

        ## Few-Shot Examples:

        ### Q1: List all books ordered by Alice Smith.
        output : ```sql
        SELECT b.title
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN books b ON oi.book_id = b.book_id
        WHERE c.name = 'Alice Smith';
        ```


        ###Q2 : Find total amount spent by each customer.
        output : ``` sql 
        SELECT c.name, SUM(b.price * oi.quantity) AS total_spent
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN books b ON oi.book_id = b.book_id
        GROUP BY c.name;
        ```

        Database Schema:

        Table: customers
            customer_id (PK): integer
            name: text
            email: text

        Table: books
            book_id (PK): integer
            title: text
            author: text
            price: numeric(6,2)

        Table: orders
            order_id (PK): integer
            customer_id (FK → customers.customer_id): integer
            order_date: date

        Table: order_items
            order_item_id (PK): integer
            order_id (FK → orders.order_id): integer
            book_id (FK → books.book_id): integer
            quantity: integer

            

        Question : How many books are there in total.
    """
    response = client.models.generate_content(
        model = "gemini-2.5-flash",
        contents = f"context : {prompt} ,  Question : {question} , chat_history : {chat_history}"
    )
    query = re.sub(r"^```[ \t]*sql[ \t]*\n?","", response.text,flags=re.IGNORECASE)
    query = re.sub(r"\n?```$","", query)
    return query


def getNLPAnswer(client: genai.Client, question, response, chat_history):
    prompt = f"""
        You are part of a system that converts SQL query results into natural language responses within an ongoing chat conversation.

        ### Task
        Given the following:
        - **User Question/Message:** {question}
        - **SQL Response (from the database):** {response}
        - **Conversation Context / Chat History:** {chat_history}

        Your job is to produce a natural language reply that is:
        1. Clear, helpful, and easy to understand.
        2. Contextually appropriate — take the conversation history into account to maintain a coherent dialogue.
        3. Sensitive to the **intent of the user’s message** — some messages may be follow-ups, acknowledgments, or casual remarks that do not require factual data from the SQL response.

        ### Guidelines
        - If the SQL response contains relevant data, summarize it clearly and naturally.
        - If the SQL response is empty, invalid, or doesn’t match the user’s intent:
            - Determine if the user message is a general remark or conversational acknowledgment (e.g., “oh nice”, “good to know”, “thanks”) — in this case, respond politely without referencing the SQL or pointing out an error.
            - If the user is clearly asking a follow-up **query** but the response is empty or mismatched, indicate that there may be no data or a misunderstanding, in a graceful and helpful tone.
        - **Never repeat the SQL query or raw response.** Focus solely on providing a smooth natural language reply.
        - Keep responses polite, relevant, and conversational.

        ### Output
        Respond only with the natural language answer.
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text



def getValuefromDB(command):
    try : 
        if "invalid" in command.lower():
            return 'Invalid'
        conn = psycopg2.connect(    
                                    database = os.environ.get('DB_NAME', 'test'),
                                    user = os.environ.get('DB_USER', 'postgres'), 
                                    password = os.environ.get('DB_PASS', 'pass'), 
                                    host = os.environ.get('DB_HOST', 'localhost'),
                                    port = os.environ.get('DB_PORT', 5432)
                                )
        cur = conn.cursor()
        cur.execute(command)
        res = cur.fetchall()        
        cur.close()
        conn.close()
        return res
    except Exception as e :        
        return 'Invalid'
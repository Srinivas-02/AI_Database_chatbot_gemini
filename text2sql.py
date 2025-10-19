from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load model and tokenizer for Codet5
tokenizer = AutoTokenizer.from_pretrained("Salesforce/codet5-large")
model = AutoModelForSeq2SeqLM.from_pretrained("Salesforce/codet5-large")

# Define the system prompt and context
system_prompt = """You are an AI that converts natural language queries into SQL queries. 
Use the following database schema as context and generate a valid SQL query:

Schema:
- Users: user_id (INT, PK), first_name (VARCHAR), last_name (VARCHAR), email (VARCHAR, Unique), password_hash (VARCHAR), phone_number (VARCHAR), address (TEXT), created_at (TIMESTAMP), updated_at (TIMESTAMP)
- Orders: order_id (INT, PK), user_id (INT, FK), product_id (INT), quantity (INT), order_date (TIMESTAMP)
- Products: product_id (INT, PK), product_name (VARCHAR), price (DECIMAL)
- Payments: payment_id (INT, PK), order_id (INT, FK), payment_method (VARCHAR), payment_status (VARCHAR), payment_date (TIMESTAMP)

Now, please convert the following user query into an SQL query:"""

context = """
1. Users
user_id: INT, Primary Key, Auto Increment
first_name: VARCHAR(100)
last_name: VARCHAR(100)
email: VARCHAR(255), Unique
password_hash: VARCHAR(255)
phone_number: VARCHAR(15)
address: TEXT
created_at: TIMESTAMP, Default: CURRENT_TIMESTAMP
updated_at: TIMESTAMP, Default: CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

2. Orders
order_id: INT, Primary Key, Auto Increment
user_id: INT, Foreign Key (References Users(user_id))
product_id: INT, Foreign Key (References Products(product_id))
quantity: INT
order_date: TIMESTAMP

3. Products
product_id: INT, Primary Key, Auto Increment
product_name: VARCHAR(255)
price: DECIMAL

4. Payments
payment_id: INT, Primary Key, Auto Increment
order_id: INT, Foreign Key (References Orders(order_id))
payment_method: VARCHAR(100)
payment_status: VARCHAR(50)
payment_date: TIMESTAMP
"""

# Example input query
query = "How many users have placed an order?"

# Combine the system prompt, user query, and context into one text input
text_input = system_prompt + "\nquery: " + query + "\n" + context

# Tokenize the input text
input_ids = tokenizer(text_input, return_tensors="pt").input_ids

# Generate SQL query with a reasonable max length
generated_ids = model.generate(input_ids, max_length=100, num_beams=5, no_repeat_ngram_size=2)

# Decode the generated text to get the SQL query
generated_sql = tokenizer.decode(generated_ids[0], skip_special_tokens=True)

# Print the generated SQL query
print("Generated SQL Query: ", generated_sql)

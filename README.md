# Django Project Setup and API Testing Guide

## Project Setup

### 1. Install Requirements

First, ensure you're in your project directory, then run:

```bash
pip install -r requirements.txt
```

### 2. Database Setup

Run the following commands to set up your database:
(make sure you are inside the project articlesdatabase in your path)
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser

Create an admin user:

```bash
python manage.py createsuperuser
```

Follow the prompts to set username, email, and password.

### 4. Run the Server

Start the Django development server:

```bash
python manage.py runserver
```

The server should now be running at `http://localhost:8000`.

## API Testing

Open a new terminal in VS Code to run the following API calls. Replace `usertoken` with the actual token you receive after authentication.

### User Registration and Authentication

```bash
# Register users
curl -X POST http://localhost:8000/api/register/ -H "Content-Type: application/json" -d "{\"username\": \"user1\", \"password\": \"A!@#$%^&*()\", \"password2\": \"A!@#$%^&*()\", \"email\": \"user1@example.com\", \"first_name\": \"User\", \"last_name\": \"One\"}"
curl -X POST http://localhost:8000/api/register/ -H "Content-Type: application/json" -d "{\"username\": \"user2\", \"password\": \"A!@#$%^&*()\", \"password2\": \"A!@#$%^&*()\", \"email\": \"user2@example.com\", \"first_name\": \"User\", \"last_name\": \"Two\"}"
curl -X POST http://localhost:8000/api/register/ -H "Content-Type: application/json" -d "{\"username\": \"user3\", \"password\": \"A!@#$%^&*()\", \"password2\": \"A!@#$%^&*()\", \"email\": \"user3@example.com\", \"first_name\": \"User\", \"last_name\": \"Three\"}"

# Get tokens (replace USER with user1, user2, or user3)
curl -X POST http://localhost:8000/api-token-auth/ -H "Content-Type: application/json" -d "{\"username\": \"USER\", \"password\": \"A!@#$%^&*()\"}"
```

### Article Management

```bash
# Create articles
curl -X POST http://localhost:8000/api/articles/ -H "Content-Type: application/json" -H "Authorization: Token user1token" -d "{\"identifier\": \"art2\", \"title\": \"New Article\", \"abstract\": \"This is a test article.\", \"publication_date\": \"2024-03-15\", \"authors\": [\"user1\"], \"tags\":[\"test\", \"article\"]}"

curl -X POST http://localhost:8000/api/articles/ -H "Content-Type: application/json" -H "Authorization: Token user2token" -d "{\"identifier\": \"art3\", \"title\": \"Science of Beef\", \"abstract\": \"A scientific approach to beef.\", \"publication_date\": \"2024-03-02\", \"authors\": [\"user1\", \"user2\"], \"tags\":[\"science\", \"beef\"]}"

curl -X POST http://localhost:8000/api/articles/ -H "Content-Type: application/json" -H "Authorization: Token user3token" -d "{\"identifier\": \"art4\", \"title\": \"Database\", \"abstract\": \"This is a test article.\", \"publication_date\": \"2024-03-15\", \"authors\": [\"user3\"], \"tags\":[\"science\", \"database\"]}"

# List articles by user
curl -X GET "http://localhost:8000/api/articles/?authors=user3" -H "Authorization: Token usertoken"

# Filter articles
curl -X GET "http://localhost:8000/api/articles/?year=2024&month=3" -H "Authorization: Token usertoken"
curl -X GET "http://localhost:8000/api/articles/?keywords=test" -H "Authorization: Token usertoken"
curl -X GET "http://localhost:8000/api/articles/?tags=test" -H "Authorization: Token usertoken"

# Update article
curl -X PATCH "http://localhost:8000/api/articles/art3/" -H "Content-Type: application/json" -H "Authorization: Token usertoken" -d "{\"title\": \"Updated Title 2\", \"abstract\": \"Updated abstract.\"}"

# Paginate results
curl -X GET "http://localhost:8000/api/articles/?page=1&page_size=2" -H "Authorization: Token usertoken"

# Delete article
curl -X DELETE "http://localhost:8000/api/articles/delete_by_identifier/?identifier=art2" -H "Authorization: Token user1token"

# Download CSV
curl -X GET "http://localhost:8000/api/articles/download_csv/?identifiers=art3,art4" -H "Authorization: Token usertoken" -o articles.csv
curl -X GET "http://localhost:8000/api/articles/download_csv/?year=2024&month=3" -H "Authorization: Token usertoken" -o articles.csv
curl -X GET "http://localhost:8000/api/articles/download_csv/?authors=user1" -H "Authorization: Token usertoken" -o articles.csv
curl -X GET "http://localhost:8000/api/articles/download_csv/?tags=beef" -H "Authorization: Token usertoken" -o articles.csv
curl -X GET "http://localhost:8000/api/articles/download_csv/?year=2024&authors=user1&tags=science" -H "Authorization: Token usertoken" -o articles.csv
```

### Comment Management

```bash
# Create comments
curl -X POST http://localhost:8000/api/comments/ -H "Content-Type: application/json" -H "Authorization: Token user1token" -d "{\"article\": \"art3\", \"content\": \"coolf!\"}"
curl -X POST http://localhost:8000/api/comments/ -H "Content-Type: application/json" -H "Authorization: Token user2token" -d "{\"article\": \"art3\", \"content\": \"okay.\"}"
curl -X POST http://localhost:8000/api/comments/ -H "Content-Type: application/json" -H "Authorization: Token user3token" -d "{\"article\": \"art4\", \"content\": \"Interesting database article!\"}"

# List comments
curl -X GET "http://localhost:8000/api/comments/?user__username=user1" -H "Authorization: Token usertoken"
curl -X GET "http://localhost:8000/api/comments/article_comments/?article_identifier=art3" -H "Authorization: Token usertoken"

# Update comment (replace COMMENT_ID with actual ID)
curl -X PATCH http://localhost:8000/api/comments/COMMENT_ID/ -H "Content-Type: application/json" -H "Authorization: Token user1token" -d "{\"content\": \"Updated: updated!\"}"

# Delete comment (replace COMMENT_ID with actual ID)
curl -X DELETE http://localhost:8000/api/comments/COMMENT_ID/ -H "Authorization: Token user1token"

# Test permissions (should fail)
curl -X PATCH http://localhost:8000/api/comments/user3commentid/ -H "Content-Type: application/json" -H "Authorization: Token user2token" -d "{\"content\": \"Trying to change someone else's comment!\"}"
curl -X DELETE http://localhost:8000/api/comments/COMMENT_ID/ -H "Authorization: Token user2token"
```

Remember to replace `usertoken`, `user1token`, `user2token`, `user3token`, and `COMMENT_ID` with actual values you receive during testing.
# Barbeque Nation Chatbot

A conversational AI agent for handling inbound enquiries and bookings for Barbeque Nation restaurants in Delhi and Bangalore.

## Features

- FAQ Management
- Booking Management (New, Update, Cancel)
- Property-specific Information
- Post-call Analysis
- Custom Chatbot Interface

## Project Structure

```
chatbot/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── endpoints/
│   │   │   ├── __init__.py
│   │   │   ├── knowledge_base.py
│   │   │   ├── chatbot.py
│   │   │   └── post_call.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── knowledge_base.py
│   │   ├── state_manager.py
│   │   └── conversation.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── data/
│   ├── knowledge_base/
│   └── prompts/
├── tests/
│   └── __init__.py
├── .env
├── requirements.txt
└── main.py
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with the following variables:
```
RETELL_API_KEY=your_api_key
DATABASE_URL=your_database_url
```

4. Run the application:
```bash
python main.py
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Accessing the Application and API Endpoints

Once the server is running (by default on `http://localhost:8001`, though this can be changed in `main.py`):

- **Chatbot Frontend:** Access the web chatbot interface in your browser at `http://localhost:8001/`, it also in the static folder as index.html.
- **API Documentation (Swagger UI):** Explore the available API endpoints (including Knowledge Base and Chatbot) at `http://localhost:8001/docs`.
- **Knowledge Base API Endpoints:** Specific endpoints for accessing knowledge base data are available under the `/api/knowledge` prefix (details in API documentation).

**Note:** The **Post-Call Analysis Excel Sheet** and **Agent Linked Phone Number** features are not implemented in this simplified version of the project.

## Knowledge Base

The knowledge base contains information about:
- Restaurant locations in Delhi and Bangalore
- Menu items and pricing
- Operating hours
- Booking policies
- FAQ information

## State Management

The chatbot uses a state-based conversation flow with the following states:
1. Initial Greeting
2. City Selection
3. Restaurant Selection
4. Query Type (FAQ/Booking)
5. Information Collection
6. Confirmation
7. Farewell

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 
# Citizen Care – AI-Powered Citizen Support Platform

Citizen Care is a web-based citizen support and complaint management platform built with **Python, Django, Bootstrap, and AI integration**.

The platform provides a centralized solution for managing citizen complaints, handling user interactions, and improving communication through WhatsApp Cloud API. It also integrates an AI-powered assistant to help users get relevant information and assistance.

## 🚀 Technology Stack

### Backend
- Python
- Django
- Django ORM

### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap 5

### Database
- PostgreSQL
- SQLite (Local Development)

### AI Integration
- OpenAI API
- LangChain
- Retrieval-Augmented Generation (RAG)

### Communication
- WhatsApp Cloud API
- Meta Graph API
- Webhooks

### Deployment & Tools
- Git & GitHub
- Gunicorn
- WhiteNoise
- Cloudinary

## ✨ Key Features

### 1. User Authentication
- User registration and login
- Custom Django user model
- Authentication and authorization
- User account management

### 2. Complaint Management
- Citizen complaint submission
- Complaint record management
- Complaint status tracking
- Centralized complaint handling

### 3. AI-Powered Assistant
- AI-powered conversational assistance
- Natural language query processing
- Context-aware responses
- RAG-based knowledge retrieval
- Integration with OpenAI API

### 4. WhatsApp Cloud API Integration
- Send and receive WhatsApp messages
- WhatsApp webhook integration
- Manage WhatsApp contacts
- Store conversation history
- Incoming and outgoing message tracking
- Automated AI-powered WhatsApp responses

### 5. Dashboard
- Centralized administration dashboard
- Complaint overview
- User management
- Application module management

### 6. Notification Management
- Notification handling
- Communication updates
- User notifications

## 📁 Project Structure

```text
citizen-care/
│
├── accounts/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── ai_assistant/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── complaints/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── dashboard/
│
├── notifications/
│
├── pages/
│
├── whatsapp/
│
├── static/
├── templates/
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 🛠️ Getting Started

### Prerequisites

- Python 3.11+
- pip
- Git
- PostgreSQL (if using PostgreSQL)

### 1. Clone the Repository

```bash
git clone https://github.com/jeyabalaganesh-s/citizen-care.git
```

### 2. Navigate to the Project

```bash
cd citizen-care
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment.

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root directory.

Example configuration:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True

OPENAI_API_KEY=your_openai_api_key

WHATSAPP_API_VERSION=your_api_version
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
WHATSAPP_VERIFY_TOKEN=your_webhook_verify_token
META_APP_SECRET=your_meta_app_secret
```

Configure database credentials and any additional environment variables required by your Django settings.

**Security:** Never expose API keys, access tokens, or secret credentials in a public repository.

### 6. Apply Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create an Administrator Account

```bash
python manage.py createsuperuser
```

### 8. Run the Development Server

```bash
python manage.py runserver
```

Open the application in your browser:

```text
http://127.0.0.1:8000/
```

## 📱 WhatsApp Cloud API Configuration

Citizen Care integrates with Meta's WhatsApp Cloud API to enable communication between citizens and the platform.

Integration requirements:

1. Create an application in Meta for Developers.
2. Configure the WhatsApp product.
3. Obtain the WhatsApp Phone Number ID.
4. Generate an access token.
5. Configure the webhook callback URL.
6. Verify the webhook using the verification token.
7. Subscribe the WhatsApp Business Account (WABA) to the Meta application.
8. Configure the required webhook event subscriptions.

## 🤖 AI Assistant Configuration

The AI assistant uses OpenAI API integration to process user queries and generate contextual responses.

For knowledge-based responses, the application can use Retrieval-Augmented Generation (RAG) to retrieve relevant information from an indexed knowledge base.

Configure your API key in the `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
```

## 🔐 Security

- Django authentication and permission management.
- Environment-based secret management.
- CSRF protection.
- Input validation.
- Secure API credential handling.
- Webhook verification.
- HTTPS configuration for production.

## 🚀 Deployment

The application can be deployed using a suitable Python hosting environment.

Production configuration should include:

- `DEBUG=False`
- Secure Django secret key
- Production database configuration
- Allowed hosts configuration
- HTTPS
- Static file collection
- Secure environment variables

Collect static files:

```bash
python manage.py collectstatic
```

## 🌐 Live Application

**Website:** https://citizen-care.jeyabalaganesh.site/

**GitHub Repository:** https://github.com/jeyabalaganesh-s/citizen-care

## 📌 Future Enhancements

- Advanced complaint analytics
- AI-powered complaint classification
- Improved complaint tracking
- Automated citizen notifications
- Multilingual AI assistance
- Enhanced administrative reporting

## 📄 License

This project is developed as a citizen support and complaint management platform.

All rights reserved.

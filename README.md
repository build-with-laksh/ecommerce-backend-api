# E-Commerce Backend API

A production-style **E-Commerce REST API** built with **Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT Authentication, Pytest, and Docker**.

The project implements the core backend workflow of an e-commerce system including user authentication, product management, shopping cart operations, order checkout, inventory updates, role-based authorization, database migrations, automated testing, and containerization.

---

## Features

### User Management & Authentication
- User registration
- User login
- Secure password hashing
- JWT-based authentication
- Retrieve authenticated user profile
- Retrieve users by ID
- Admin role support

### Product Management
- Create products
- Retrieve all products
- Retrieve individual products
- Update products
- Delete products
- Admin-only product management
- Product stock tracking

### Shopping Cart
- Add products to cart
- View authenticated user's cart
- Update cart item quantity
- Remove items from cart
- User-specific cart ownership

### Order & Checkout System
- Checkout products from cart
- Create orders and order items
- Calculate total units and total bill
- Store product price at the time of purchase
- Validate product stock before checkout
- Automatically reduce inventory after successful checkout
- Automatically clear cart after checkout
- Retrieve order history
- Retrieve individual orders

### Authorization
Protected endpoints use JWT authentication.

Administrative product operations are restricted to users with admin privileges.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Python** | Backend programming language |
| **FastAPI** | REST API framework |
| **PostgreSQL** | Relational database |
| **SQLAlchemy** | ORM and database interaction |
| **Alembic** | Database migrations |
| **Pydantic** | Request/response validation |
| **JWT** | Authentication |
| **Pytest** | Automated testing |
| **HTTPX** | Async API testing |
| **Docker** | Application containerization |
| **Uvicorn** | ASGI server |

---

## Project Architecture

```text
ecommerce-backend-api/
│
├── app/
│   ├── routers/
│   │   ├── users.py
│   │   ├── products.py
│   │   ├── cartitems.py
│   │   └── orders.py
│   │
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   └── db.py
│
├── alembic/
├── tests/
├── Dockerfile
├── .dockerignore
├── alembic.ini
├── requirements.txt
└── README.md
```

---

## Application Flow

```text
Client
  │
  ▼
FastAPI
  │
  ├── Authentication / Authorization
  │
  ├── Users
  ├── Products
  ├── Cart
  └── Orders
  │
  ▼
SQLAlchemy
  │
  ▼
PostgreSQL
```

---

## Authentication Flow

Users authenticate using their username and password.

After successful authentication, the API generates a **JWT access token**.

The token is then used to access protected endpoints.

```text
Register
   ↓
Login
   ↓
JWT Access Token
   ↓
Protected API
   ↓
Current User
```

Admin-protected endpoints additionally verify the authenticated user's admin status from the database.

---

## Checkout Flow

The checkout system handles the complete cart-to-order workflow.

```text
User Cart
   ↓
Validate Cart Items
   ↓
Validate Product Stock
   ↓
Create Order
   ↓
Create Order Items
   ↓
Calculate Total Bill & Units
   ↓
Reduce Product Stock
   ↓
Clear User Cart
   ↓
Commit Transaction
   ↓
Return Created Order
```

Each order stores the product's **purchase price at checkout time**, ensuring historical order data remains consistent even if product prices change later.

---

## Database Models

The application contains the following primary entities:

### User
Stores user account information and administrative status.

### Product
Stores product information including category, price, and available stock.

### CartItem
Connects users with products they have added to their shopping cart.

### Order
Stores checkout-level information including:

- Total bill
- Total units
- Order status
- Purchase timestamp

### OrderItem
Stores individual products purchased within an order, including their purchase price and quantity.

---

## API Routes

### Users

```text
POST   /users/register
POST   /users/login
GET    /users/me
GET    /users/{user_id}
```

### Products

```text
POST   /products
GET    /products
GET    /products/{product_id}
PATCH  /products/{product_id}
DELETE /products/{product_id}
```

Product creation, modification, and deletion require **admin privileges**.

### Cart

```text
POST   /cart
GET    /cart
PATCH  /cart/{cart_item_id}
DELETE /cart/{cart_item_id}
```

### Orders

```text
POST   /order/checkout
GET    /order
GET    /order/{order_id}
```

### Health Check

```text
GET /health
```

The health endpoint verifies that the application can successfully communicate with the PostgreSQL database.

---

## Automated Testing

The project includes an asynchronous test suite built with:

- Pytest
- HTTPX AsyncClient
- ASGITransport
- SQLAlchemy AsyncSession
- Dedicated PostgreSQL test database

Tests cover the primary application flows including:

```text
Authentication
Users
Products
Cart
Orders / Checkout
Admin authorization
```

The test environment uses database transaction isolation to prevent individual tests from permanently modifying test data.

Run the test suite with:

```bash
pytest
```

---

## Docker

The FastAPI application can be packaged and run using Docker.

The Docker image:

1. Uses a lightweight Python base image
2. Installs dependencies from `requirements.txt`
3. Copies the application source code
4. Starts the API using Uvicorn

The application container can communicate with a PostgreSQL container through a shared Docker network.

```text
Browser / Client
       │
       ▼
Host :8000
       │
       ▼
FastAPI Container :8000
       │
       │ Docker Network
       ▼
PostgreSQL Container :5432
```

Build the application image:

```bash
docker build -t ecommerce_backend .
```

> Database credentials and application secrets should be supplied through environment variables and must not be committed to source control.

---

## Environment Variables

Create a `.env` file in the project root for local development.

Example:

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/database_name
SECRET_KEY=your_secret_key
```

Do **not** commit `.env` files or real credentials to GitHub.

---

## Database Migrations

Database schema changes are managed using **Alembic**.

Apply existing migrations:

```bash
alembic upgrade head
```

Create a new migration after changing database models:

```bash
alembic revision --autogenerate -m "migration description"
```

---

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/build-with-laksh/ecommerce-backend-api.git
cd ecommerce-backend-api
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it and install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create your local `.env` file and configure the PostgreSQL database connection and JWT secret.

### 4. Apply database migrations

```bash
alembic upgrade head
```

### 5. Start the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## Interactive API Documentation

FastAPI automatically provides interactive API documentation.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

Swagger UI can be used to explore and test the API endpoints directly from the browser.

---

## Security

The project implements:

- Password hashing
- JWT-based authentication
- Protected API routes
- Admin-only operations
- User-specific resource access
- Environment-based secrets
- Input validation using Pydantic

Sensitive values such as database credentials and JWT secrets are excluded from the Docker image and source control.

---

## Future Improvements

Potential future additions include:

- Docker Compose
- CI/CD pipeline
- Cloud deployment
- Pagination and filtering
- Product search
- Refresh tokens
- Structured logging
- Extended integration and edge-case testing

---

## Author

**Laksh Rathore**

Backend development project built with Python and FastAPI.

GitHub: `build-with-laksh`

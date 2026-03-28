# Project Structure Documentation

## Project Folder Structure

```
Project Folder/
├── Readme.md
├── Src/
│   ├── __init__.py
│   ├── main.py
│   ├── Config/
│   ├── Loggers/
│   ├── Routers/
│   ├── Controllers/
│   ├── Service/
│   ├── Repository/
│   ├── Utilities/
│   ├── Database/
│   ├── Cache/
│   ├── Middleware/
│   └── DTO/
│   └── Models/
│   └── Migration/
│   └── Error-Codes/
├── Test/
├── requirements.txt
└── DockerFile
```

## Component Details

### Readme.md
Project documentation and setup instructions.

### Src

#### `__init__.py`
To access all the files in the folders easily.

#### `main.py`
**Server Configuration**
- All server configuration to initiate the FastAPI backend server will be defined here
- Execute all table creation and CORS configuration
- Include routers from the Routers folder with `app.include_router()`
- Exception handlers for validation and application errors
- Lifespan management for startup and shutdown events

### Config
Application configuration management.

**Key Points:**
- Loads configuration from environment variables or AWS Secrets Manager

### Loggers
Structured logging system for the application.

**Key Points:**
- JSON formatted logging
- Multiple log levels (debug, info, warn, error, fatal)
- Structured fields support for better log analysis

### Routers
All routers are initialized here with their respective prefixes for all the APIs.

**RESTful Routes Definition:**
- Include all routes
- Define GET, PUT, POST, DELETE RESTful routes

### Controllers
Requests are routed to the Controllers where Pydantic validation is performed in the DTO. Once validated, requests are forwarded to the Service layer.

**Key Points:**
- Act as intermediary between routers and service layer
- Call service layer functions with validated data
- **No business logic here** - only service calls

Need to define all the routes that are required for the project. **No need to define the functions here**.

**HTTP Methods:**
- **GET** - To fetch data from any source
- **PUT** - To update existing data in any source
- **POST** - To insert new data in any source

**Business Logic Breakdown:**
- Need to breakdown the visuals into business (i.e., each objective/purpose in the screen will be considered as one business)
- Need to check whether we have common purpose/objective across all the business
- Need to check whether the common purpose/objective shares same data layer (i.e., Same Backend Table)
  - **If yes for both**, then the common purpose/objective will be treated as separate business
  - **If it's not sharing a common data layer**, we should not treat the common purpose as a separate business
- Each business will be treated as a separate API/Route which will have separate python file with naming convention as `purposename_controller` inside controller

### Service
Need to define all the functions that consists business logic for entire application.

**Guidelines:**
- Need to replicate the folder structure exactly like controller's folder structure
- Need to create a separate python files under each folder for every route/API we have in controller with naming convention as `logicname_service`
- Contains all business logic and data processing
- Calls repository layer for database operations
- Need to analyze if any logic functions shares with more than one routes/APIs wrt the business
  - **If yes**, then need to create it as a common python file which we can share among the controllers

### Repository
Need to define all the functions that interacts with database which will be utilized in Service layer. Along with this we also have database schema for ORM usage.

**Structure:**
- Need to create a folder called **"MODELS"** that consists of entire database schema as objects for ORM utilization
- Need to create a separate python file for database engine and connection string wrapped with context manager
- Need to create separate repository files for each service folder
- Each file should contains all the ORM function against respective service irrespective of number of business logics in service folder
- Contains all database queries and ORM operations
- Uses SQLAlchemy for database interactions

### Utilities
Contains reusable helper functions in separate Python files that can be shared across the application to support common functionality.


### Database
Database connection and session management.

**Key Points:**
- Database engine initialization
- Connection string management with context manager
- Connection testing and health checks
- Do ensure to use only asynccontextmanager

### Cache
**LRU (Least Recently Used):** It will delete the least recently used based on default time limit.

**TTL (Time to Leave):** It will delete all the records after the certain time period (we will set the time).

### Middleware
We need to have payload encryption and decryptions.

### Models
Database schema defined as SQLAlchemy ORM models.

**Key Points:**
- Contains table definitions using SQLAlchemy
- Defines relationships between tables
- Used by repository layer for database operations

### Migration
Handles database schema migrations and versioning.

**Key Points:**
- Auto migration functionality for table creation
- Tracks migration history

### Error-Codes
Centralized error code definitions for the application.

**Key Points:**
- Custom application error classes
- Standardized error codes and messages


### DTO (Data Transfer Object)
Data transfer objects for structured data handling.

**Key Points:**
- Pydantic models for request and response validation
- Defines data structure for API requests and responses
- Ensures type safety and data validation

### Test
- Need to replicate all the source folder structure along with files
- Need to write a testing scripts for each functions present in each files using pytest

### requirements.txt
Python package dependencies.

### DockerFile
Need to run the application in Gunicorn to have smoother asynchronous functionality in production.
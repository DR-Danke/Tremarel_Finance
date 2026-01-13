# Conditional Documentation Guide

This prompt helps you determine what documentation you should read based on the specific changes you need to make in the codebase. Review the conditions below and read the relevant documentation before proceeding with your task.

## Instructions
- Review the task you've been asked to perform
- Check each documentation path in the Conditional Documentation section
- For each path, evaluate if any of the listed conditions apply to your task
  - IMPORTANT: Only read the documentation if any one of the conditions match your task
- IMPORTANT: You don't want to excessively read documentation. Only read the documentation if it's relevant to your task.

## Conditional Documentation

- README.md
  - Conditions:
    - When operating on anything under Server
    - When operating on anything under Client
    - When first understanding the project structure
    - When you want to learn the commands to start or stop the Server or Client

- Client/src/style.css
  - Conditions:
    - When you need to make changes to the Client's style

- .claude/commands/classify_adw.md
  - Conditions:
    - When adding or removing new `adws/adw_*.py` files

- adws/README.md
  - Conditions:
    - When you're operating in the `adws/` directory

- app_docs/feature-0f0d4c36-fastapi-backend-setup.md
  - Conditions:
    - When setting up or modifying the FastAPI Server project structure
    - When working with Server/main.py or application entry point
    - When configuring CORS, environment variables, or settings
    - When adding new routers or API endpoints to the Server
    - When troubleshooting Server startup or configuration issues

- app_docs/feature-2a0579e1-frontend-react-vite-setup.md
  - Conditions:
    - When setting up or modifying the Client folder structure
    - When working with Vite configuration or path aliases
    - When configuring Material-UI theming for the application
    - When troubleshooting axios interceptor or JWT token handling
    - When deploying the Client to Vercel
    - When adding new React dependencies or updating package.json

- app_docs/feature-db5f36c7-database-schema-tables.md
  - Conditions:
    - When working with Finance Tracker database tables or schema
    - When implementing user authentication or JWT-based auth
    - When working with entities, categories, transactions, or budgets tables
    - When modifying Server/database/schema.sql
    - When troubleshooting foreign key constraints or database relationships
    - When implementing multi-entity support (family/startup separation)

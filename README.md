# Dashboard Backend

Build the application with `docker-compose build`
Start the application with `docker-compose up`

### Database

PostgreSQL is used for the database. To run a migration of the database after changing columns/tables, run:
`alembic revision --autogenerate -m "<Changed X fields>"`
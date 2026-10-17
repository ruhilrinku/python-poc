from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "Employee Management API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database identity.
    db_name: str = "postgres"
    db_schema: str = "employee_management"

    # SQLAlchemy runtime connection.
    database_url: str = (
        "postgresql+psycopg2://postgres:password@localhost:5432/postgres?sslmode=disable"
    )
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # Liquibase / JDBC connection.
    jdbc_url: str = "jdbc:postgresql://localhost:5432/postgres"
    db_user: str = "postgres"
    db_password: str = "password"
    liquibase_changelog: str = "db-migrations/changelog-master.yaml"
    run_migrations_on_startup: bool = True
    fail_on_migration_error: bool = False
    # Optional explicit JDK path for Liquibase; auto-detected when empty.
    java_home: str = ""

    log_level: str = "INFO"
    log_json: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()

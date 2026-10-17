import glob
import logging
import os
import tempfile
from pathlib import Path

from app.infrastructure.config import Settings, get_settings
from app.infrastructure.logging import configure_logging

logger = logging.getLogger(__name__)


def _is_java_home(path: str | None) -> bool:
    """A usable JAVA_HOME contains a JVM shared library under bin/ or lib/."""
    if not path:
        return False
    root = Path(path)
    jvm_libs = ["bin/server/jvm.dll", "bin/client/jvm.dll", "lib/server/libjvm.so", "lib/server/libjvm.dylib"]
    return any((root / lib).is_file() for lib in jvm_libs)


def _discover_java_home() -> str | None:
    """Look for a JDK/JRE in common install locations when JAVA_HOME is unset."""
    patterns = [
        r"C:\Program Files\Java\*",
        r"C:\Program Files\Eclipse Adoptium\*",
        r"C:\Program Files\Microsoft\jdk*",
        "/usr/lib/jvm/*",
        "/Library/Java/JavaVirtualMachines/*/Contents/Home",
    ]
    for pattern in patterns:
        for candidate in sorted(glob.glob(pattern), reverse=True):
            if _is_java_home(candidate):
                return candidate
    return None


def _ensure_java_home(settings: Settings) -> None:
    """Resolve JAVA_HOME so pyjnius can locate a JVM for Liquibase."""
    if _is_java_home(os.environ.get("JAVA_HOME")):
        return
    resolved = settings.java_home or _discover_java_home()
    if _is_java_home(resolved):
        os.environ["JAVA_HOME"] = resolved  # type: ignore[arg-type]
        logger.info("java.home.resolved", extra={"extra_fields": {"java_home": resolved}})



def _write_properties(settings: Settings) -> Path:
    """Render a liquibase.properties file from the active settings."""
    content = "\n".join(
        [
            f"changeLogFile: {settings.liquibase_changelog}",
            f"url: {settings.jdbc_url}",
            f"username: {settings.db_user}",
            f"password: {settings.db_password}",
            "driver: org.postgresql.Driver",
            f"defaultSchemaName: {settings.db_schema}",
            f"liquibaseSchemaName: {settings.db_schema}",
        ]
    )
    path = Path(tempfile.gettempdir()) / "employee-management.liquibase.properties"
    path.write_text(content, encoding="utf-8")
    return path


def _ensure_schema(settings: Settings) -> None:
    """Create the target schema before Liquibase writes its tracking tables there."""
    from sqlalchemy import create_engine, text

    engine = create_engine(settings.database_url)
    try:
        with engine.begin() as conn:
            conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{settings.db_schema}"'))
    finally:
        engine.dispose()


def run_migrations(settings: Settings | None = None) -> None:
    """Apply all pending Liquibase changesets against the configured database."""
    from pyliquibase import Pyliquibase

    settings = settings or get_settings()
    _ensure_java_home(settings)
    _ensure_schema(settings)
    properties_file = _write_properties(settings)
    logger.info(
        "liquibase.update.start",
        extra={"extra_fields": {"changelog": settings.liquibase_changelog}},
    )
    liquibase = Pyliquibase(defaultsFile=str(properties_file))
    liquibase.update()
    logger.info("liquibase.update.complete")


if __name__ == "__main__":
    active_settings = get_settings()
    configure_logging(active_settings.log_level, active_settings.log_json)
    run_migrations(active_settings)

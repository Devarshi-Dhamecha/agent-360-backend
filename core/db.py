"""
Database utilities for PostgreSQL connection management.
"""
import logging
from django.db import connection
from django.db.utils import OperationalError

logger = logging.getLogger(__name__)


def check_database_connection():
    """
    Check if database connection is active.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        logger.info('Database connection successful')
        return True
    except OperationalError as e:
        logger.error(f'Database connection failed: {str(e)}')
        return False


def get_db_info():
    """
    Get database connection information.
    
    Returns:
        dict: Database connection details
    """
    db_config = connection.settings_dict
    return {
        'engine': db_config.get('ENGINE'),
        'name': db_config.get('NAME'),
        'user': db_config.get('USER'),
        'host': db_config.get('HOST'),
        'port': db_config.get('PORT'),
    }

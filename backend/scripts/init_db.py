#!/usr/bin/env python3
"""
Database initialization script for AI Stack Backend
"""

import os
import sys
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from app.config import settings
from app.database import engine, Base
from app.models import Workflow, Document, ChatSession
import structlog

logger = structlog.get_logger()


def create_database():
    """Create database if it doesn't exist"""
    try:
        # Parse database URL to get connection details
        db_url = settings.database_url
        if db_url.startswith('postgresql://'):
            # Extract database name from URL
            db_name = db_url.split('/')[-1]
            # Create connection URL without database name
            base_url = '/'.join(db_url.split('/')[:-1])
            
            # Connect to PostgreSQL server
            engine = create_engine(base_url + '/postgres')
            
            with engine.connect() as conn:
                # Check if database exists
                result = conn.execute(text(
                    "SELECT 1 FROM pg_database WHERE datname = :db_name"
                ), {"db_name": db_name})
                
                if not result.fetchone():
                    # Create database
                    conn.execute(text(f"CREATE DATABASE {db_name}"))
                    logger.info(f"Database '{db_name}' created successfully")
                else:
                    logger.info(f"Database '{db_name}' already exists")
                    
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        raise


def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise


def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def create_sample_data():
    """Create sample data for testing"""
    try:
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as db:
            # Check if sample workflow already exists
            existing_workflow = db.query(Workflow).filter(
                Workflow.name == "Sample Document Q&A Workflow"
            ).first()
            
            if not existing_workflow:
                # Create sample workflow
                sample_workflow = Workflow(
                    name="Sample Document Q&A Workflow",
                    description="A sample workflow for answering questions about documents",
                    nodes=[
                        {
                            "id": "1",
                            "type": "userQuery",
                            "position": {"x": 100, "y": 100},
                            "data": {}
                        },
                        {
                            "id": "2",
                            "type": "knowledgeBase",
                            "position": {"x": 300, "y": 100},
                            "data": {
                                "similarityThreshold": 0.7,
                                "topK": 5
                            }
                        },
                        {
                            "id": "3",
                            "type": "llmEngine",
                            "position": {"x": 500, "y": 100},
                            "data": {
                                "provider": "openai",
                                "model": "gpt-3.5-turbo",
                                "temperature": 0.7,
                                "maxTokens": 1000
                            }
                        },
                        {
                            "id": "4",
                            "type": "output",
                            "position": {"x": 700, "y": 100},
                            "data": {}
                        }
                    ],
                    edges=[
                        {"source": "1", "target": "2"},
                        {"source": "2", "target": "3"},
                        {"source": "3", "target": "4"}
                    ],
                    is_active=True
                )
                
                db.add(sample_workflow)
                db.commit()
                logger.info("Sample workflow created successfully")
            else:
                logger.info("Sample workflow already exists")
                
    except Exception as e:
        logger.error(f"Failed to create sample data: {e}")
        raise


def main():
    """Main initialization function"""
    logger.info("Starting database initialization...")
    
    try:
        # Test connection first
        if not test_connection():
            logger.info("Attempting to create database...")
            create_database()
            
            # Test connection again
            if not test_connection():
                logger.error("Database connection failed after creation")
                sys.exit(1)
        
        # Create tables
        create_tables()
        
        # Create sample data
        create_sample_data()
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
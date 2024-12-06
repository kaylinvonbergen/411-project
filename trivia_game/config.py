import os

class ProductionConfig():
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # This would almost universally be false in a Flask app
                                           # But we are doing unnecessarily complicated Redis
                                           # write-throughs
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', "DATABASE_URL=sqlite:////app/db/app.db")  # Production database URI from environment

class TestConfig():
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory database for tests
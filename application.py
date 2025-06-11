# This file is needed for AWS Elastic Beanstalk deployment
# It simply imports the app from api.py
from api import app as application

if __name__ == "__main__":
    application.run()

import logging
import os
import csv
import smtplib
import json
import sys


def main():
    # Create the logger
    logger = logging.getLogger(__name__)

    # Create a handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler("log.txt")

    # Formatting
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Set the levels and the formatting
    stdout_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add the handlers
    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)

    # Set log level
    logger.setLevel(logging.INFO)

    # Get the project directory
    directory = os.path.abspath(os.path.dirname(__file__))

    # Path to the app password
    config_path = os.path.join(directory, "config.json")

    # Check to see if config.json exists
    logger.info("Reading login from config.json")
    if not os.path.exists(config_path):
        logger.critical("config.json not found")

        # Create example
        logger.info("Creating empty sample config.json")
        with open(config_path, "w") as config_file:
            json.dump(
                {
                    "email": "johndoe@example.com",
                    "app_password": "password",
                    "smtp": "smtp.gmail.com",
                    "port": 465,
                },
                config_file,
            )

        raise RuntimeError("config.json not found")

    # Read the login data
    with open(config_path, "r") as config_file:
        login = json.load(config_file)

    # Start the smtp client
    logger.info("Starting SMTP")
    with smtplib.SMTP_SSL(login["smtp"], login["port"]) as smtp:
        # Log in
        logger.info("Logging in")
        try:
            smtp.login(login["email"], login["app_password"])
        except Exception as e:
            logger.critical(f"Failed to conenct and log in {e}")
            raise e

        # Path to the email
        email_path = os.path.join(directory, "email.txt")

        # Check if email exists
        if not os.path.exists(email_path):
            logger.critical("email.txt not found!")
            raise RuntimeError("email.txt not found")

        # Read the email
        with open(email_path, "r") as email_file:
            # Load the contents
            has_subject = False
            email_text = "".join(email_file.readlines())
            if not email_text.startswith("Subject:"):
                logger.warning('First line does not contain "Subject: " header')

        # Path to emails.csv
        csv_path = os.path.join(directory, "emails.csv")

        # Check to see if the emails.csv file exists
        logger.info("Reading emails from emails.csv")
        if not os.path.exists(csv_path):
            logger.critical("emails.csv not found!")
            raise RuntimeError("emails.csv not found!")

        # Read the emails.csv
        with open(csv_path, "r") as emails_file:
            # Creates the reader
            reader = csv.reader(emails_file)
            # Skip headers row
            next(reader)
            for row in reader:
                # Extract the name and email
                name, email = row
                # Path to email
                logger.info(f"Loading {name}.txt")

                # Load in the name
                personalized_email = email_text.replace("${NAME}", name)

                # Send the email
                logger.info(f"Sending email to {name} {email}")
                smtp.sendmail(login["email"], email, personalized_email)
        logger.info("Finished sending emails")
    logger.info("Exiting")


if __name__ == "__main__":
    main()

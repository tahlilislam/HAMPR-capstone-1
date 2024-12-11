API: Google Cloud NLP using AutoML Vertex AI
https://cloud.google.com/vertex-ai/docs/generative-ai/start/quickstarts/quickstart-text?authuser=1&hl=en


# HAMPR: Habit App for Mental Physical Rejuvination
## An app that allows users to self-reflect by journaling and create goals using the aid of an NLP model

### Introduction

An app that promotes healthy habits by allowing the user to journal, analyze their journal entries using an NLP model to identify common themes, and create goals they can stick to.

* Allows users to sign up/login/logout
* Allows users to create and edit journal entries.
* Allows users to classify their text from journal entries using Vertext AI from Google Cloud
    * The Vertex AI model has been custom trained using using custom datasets that allows the text to fall into 18 major catagories:
        1. Attention
        2. Spirituality
        3. Resilience
        4. Positive Outlook
        5. Anxiety
        6. Depression
        7. Self-Confidence
        8. Career
        9. Society and Social Acceptance
        10. Love and Relationships
        11. Family Trauma
        12. Body Image
        13. Procrasination
        14. Sexual Harrassment 
        15. Verbal Harrassment
        16. Motivation
        17. Boredom
        18. Addiction
    * These categories are meant to allow the user to self-reflect and identify common themes of their journal entries so that they can understand themselves better and take appropriate measures or create goals for themselves.
    * THEY ARE NOT MEANT AS A DIAGNOSIS TOOL FOR ANY PHYSICAL OR EMOTIONAL AILMENTS. PLEASE SEEK PROFESSIONAL HELP FOR SUCH INSTANCES.
    * They can also create a custom goal they need to stick to for two weeks to hold them accountable for their actions because habits take serious commitment.
        * Rules for Goals:
            * User can ONLY SET one active goal for a two week period.
            * They can choose the frequency of their goal for the two week period and a date and time they will like reminders to be sent to their email to complete their goal
            * If they do not check of their goal on the set date by logging into their account, the day will be marked as missed.
            * New goals can only be created once the active goal has been completed.

### To Run the Project:
    You can install the required libraries for this project using pip. Simply run the following command inside the local directory of the project:

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    flask run

### To run flask Migrations:


### For Testing:


### Key Technologies:

* Google Cloud SDK
* VERTEX AI from Google
* Flask
* Python 3.9.18 (It's ideal to use this version or later to prevent any errors on dependencies or modules such as the ZoneInfo module for handling timezone and datetime objects which is specific to python 3.9)
* Javascript
* Jinja2
* WTF Forms
* CeleryBeat
* Rabbit MQ
* PSQL Database


### Key Takeaways:
* Learned to utilize timezone and datetime objects using Zoneinfo library which uses the IANA time zone database directly, ensuring accuracy and consistency with official timezone definitions
* learned how to use celerybeat on a schedule for reminders
* Learned how to integrate a machine learning API

### Credits:
* To my mentor


### Future Ambitions:



    


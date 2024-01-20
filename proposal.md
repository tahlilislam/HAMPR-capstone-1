## **App Name:** HaMPR-Habits App for Mental Physical Rejuvenation

### **Proposal Details- Version 1--------**

**Goal:** Create an app to help promote healthy habits in efforts to improve mental health  

**Main Features:** 
- Do journal entries, surveys, and post-reflective entries and surveys
- Do sentiment analysis or text categorization using NLP APIs on journals and surveys to identify what habits could help the user improve well being
Show user their progress by displaying trends
- Encourage users using tokens and progress bars

**Users:**  
- Open for all users
- Most likely to use the app would be ages 18 and up
- Currently working or studying
People who are actively working to improve their mental and physical health
- Data: 
- User Input data based on Journal entries and surveys
- Stored to our database
Use Watson API from IBM or something similar

**Schema:**

User registration and authentication model with data:

- Username
- Password
- First and last name
- Age
- Ethnicity? (optional)
- Profession or In School?
- Financial Status Range (optional)
- Location - general

__Survey model:__  
Still need to work out the questions…

**Journal model:**  
- Journal entry text data
- Date
- User id
- categories identified by user- for - journal -What does the user think their problems is - Predetermined or determined by User -> 
- Can compare to what the AI think their issues are
- Categories identified by AI

**Progress model:**  
Data for displaying progress:
Still need to work this out

**Suggestions model:**  
Store improvement suggestions for each category

**Possible Issues with API:**  
- Categorization accuracy
- Rate limiting
- Many features could be paid
- Finding the right API to best suit needs
Understanding how to work natural language processing models (since it's not my field of expertise)
- Data wrangling
- Filtering out unnecessary data and keeping what’s its useful
- Formatting data properly if presented in different formats
- Understanding the data
- Loading it into database

**All user data should be secure since our entire app is sensitive data —--How???**

**Functionality:**  
- Do journal entries, surveys, and post-reflective entries and surveys
Do sentiment analysis OR text categorization using NLP APIs on journals and surveys to identify what habits could help the user improve well being
- Show user their progress by displaying trends
- Encourage users using tokens and progress bars

**User Flow:**
- Register and create account - will log in 
Initial survey -> What’s wrong with you? 
- Open up journaling
- Date
- Entry
- How would you categorize your entry?
- Submit button
- Suggestions List:
    - Predetermined list of things/ habits/ activities to do based on category
    - Each item on list is selectable: Choose the habits to do for the week
    - Send reminder notifications (configure how often you want to send the reminder)
        - Yes I did (get a token)
        - Not yet, still working on it
- At the end of the week/time period:
    - Do a reflection survey/questionare to understand thoughts/feelings
    - Get weekly tokens
    - Get progress report

Habit Tracker Check-In:
Each habit has a lifespan of 2 weeks. At the end of two weeks:
The user would have the option of renewing or subtracting habit
The user would have a limit of saving 1-2 habits per 2 week time frame
What makes it more than CRUD:
Bringing in different text classification from an API

### **Feedback From Mentor---------**

- MVPs - what are nice to haves?
- Limit the functionality for now -> to account to time limitations and constraints
- Making sure you are writing tests for things smartly-> to ensure things are working properly, keep in mind of the tests so which will also take more time
Functionality standpoint - meets the criteria
- Web apps- web filters ex using Middleware -> runs prior to web request and code -> better solution in the long run 
- Also enough to pass in current session’s user id’s in queries
Can also run filter after request
Dont need to go as far as encrypting the data -> but companies would do so
- Think about general design on CSS -> less time about design since I have more features to implement
- Find about basic survey questions from a psychology standpoint -> probably models out there for surveys relating to journals
- Think about user flow in more detail
Basic table of past journal entries that you can edit - Is it create or or edit?
Ability to filter tables -> from user’s standpoint?
- Search tables
- What would that look like in terms of buttons


#### **Main thing to focus on:** 
- Do Github Repo
- Create priority list for functionality
- Find the API

### **My Notes---------------------**
Text analysis- 
- The user can classify their journal entries and set goals at the same time, user sets goals on which they will reflect on at the end of the 2 week period
- Have a button that classifies all the journal entries, can specify time range
- Text classification identifies what themes your goals fall under
- But user can journal as much as they want
- User sets goals on the first journal entry of the 2 week period 
Using a general survey -> (no text classification)
- User cannot change goals until the end of the 2 week period. This is to hold them accountable for their actions because habits take serious commitment.

### **Revisions---------------**
### **Priorities:**  
1. Let users do a general survey and set goals without requiring journals.
2. Let users create journal entries and see their entries (journal history only) They can search or filter their entries by date.
3. The users can do text classification on their individual journal entry or journals for a date range to identify themes using the “Text Classification Button” -> Based on classification, they may be suggested goals that might be helpful.
4. Let users set custom goals and specify their frequency(e.g. Go for a run 3 times a week) for a 2 week period. They would not be able to edit their goal in that period and will get reminders on the days they need to work on their goals. It will be a yes or no question. They can get calendar notifications.
5. Users will do reflection surveys and set new goals.
6. Users will also be able to see their survey history.

**API:**
Google Cloud NLP API

**Table Schemas:**  
User Schema  
General Survey Schema  
Post-Reflection Survey Schema  
Text Classification Results Schema  
Journal Entries Schema  
Goals Schema   

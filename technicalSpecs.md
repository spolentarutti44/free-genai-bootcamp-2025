## Technical Specs

## Business Logic
Business Goal: 
A language learning school wants to build a prototype of learning portal which will act as three things:
Inventory of possible vocabulary that can be learned
Act as a  Learning record store (LRS), providing correct and wrong score on practice vocabulary
A unified launchpad to launch different learning apps

## Technical Restrictions:
Use SQLite3 as the database
You can use any language or framework 
Does not require authentication/authorization, assume there is a single user

## Backend
Routes

GET /words - Get paginated list of words with review statistics
GET /groups - Get paginated list of word groups with word counts
GET /groups/:id - Get words from a specific group (This is intended to be used by target apps)
POST /study_sessions - Create a new study session for a group
POST /study_sessions/:id/review - Log a review attempt for a word during a study session

GET /words
page: Page number (default: 1)
sort_by: Sort field ('kanji', 'romaji', 'english', 'correct_count', 'wrong_count') (default: 'kanji')
order: Sort order ('asc' or 'desc') (default: 'asc')

GET /groups/:id
page: Page number (default: 1)
sort_by: Sort field ('name', 'words_count') (default: 'name')
order: Sort order ('asc' or 'desc') (default: 'asc')

POST /study_sessions
group_id: ID of the group to study (required)
study_activity_id: ID of the study activity (required)


POST /study_sessions/:id/review


## Database
```xml
<?xml version="1.0" encoding="UTF-8"?>
<database>
  <entity name="groups">
    <field name="id" type="int" primaryKey="true"/>
    <field name="name" type="string"/>
    <field name="words_count" type="int"/>
  </entity>

  <entity name="study_activities">
    <field name="id" type="int" primaryKey="true"/>
    <field name="name" type="string"/>
    <field name="url" type="string"/>
  </entity>

  <entity name="study_sessions">
    <field name="id" type="int" primaryKey="true"/>
    <field name="group_id" type="int" foreignKey="true" references="groups"/>
    <field name="study_activity_id" type="int" foreignKey="true" references="study_activities"/>
    <field name="created_at" type="timestamp"/>
  </entity>

  <entity name="words">
    <field name="id" type="int" primaryKey="true"/>
    <field name="kanji" type="string"/>
    <field name="romaji" type="string"/>
    <field name="english" type="string"/>
    <field name="parts" type="json"/>
  </entity>

  <entity name="word_groups">
    <field name="word_id" type="int" foreignKey="true" references="words"/>
    <field name="group_id" type="int" foreignKey="true" references="groups"/>
  </entity>

  <entity name="word_review_items">
    <field name="id" type="int" primaryKey="true"/>
    <field name="word_id" type="int" foreignKey="true" references="words"/>
    <field name="study_session_id" type="int" foreignKey="true" references="study_sessions"/>
    <field name="correct" type="boolean"/>
    <field name="created_at" type="timestamp"/>
  </entity>

  <!-- Define relationships (Optional - could be derived from foreign keys) -->
  <relationship from="groups" to="study_sessions" type="has"/>
  <relationship from="study_activities" to="study_sessions" type="has"/>
  <relationship from="words" to="word_groups" type="has"/>
  <relationship from="groups" to="word_groups" type="has"/>
  <relationship from="study_sessions" to="word_review_items" type="has"/>
  <relationship from="words" to="word_review_items" type="has"/>
</database>
```
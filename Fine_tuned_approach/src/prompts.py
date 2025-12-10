ATS_ENTITY_EXTRACTION_PROMPT = """
-Goal-
Given a resume text, identify all entities of types [Person, Skill, Company, Role, School, Degree, Location] and all relationships among them.

-Steps-
1. Identify all entities. For each entity, extract the following information:
- entity_name: Name of the entity, capitalized
- entity_type: One of [Person, Skill, Company, Role, School, Degree, Location]
- entity_description: Comprehensive description of the entity's attributes and activities
Format each entity as ("entity" <|{tuple_delimiter}|> <entity_name> <|{tuple_delimiter}|> <entity_type> <|{tuple_delimiter}|> <entity_description>)
**IMPORTANT**: Exactly 4 fields per entity. Do NOT add confidence scores or extra notes.


2. From the entities identified in step 1, identify all relationships. For each relationship, extract the following information:
- source_entity: name of the source entity
- target_entity: name of the target entity
- relationship_description: explanation as to why you think the source entity and the target entity are related
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
- relationship_keywords: one or more high-level keywords that summarize the nature of relation, must be one of [HAS_SKILL, WORKED_AT, STUDIED_AT, LOCATED_IN, HAS_ROLE, HAS_DEGREE]
Format each relationship as ("relationship" <|{tuple_delimiter}|> <source_entity> <|{tuple_delimiter}|> <target_entity> <|{tuple_delimiter}|> <relationship_description> <|{tuple_delimiter}|> <relationship_keywords> <|{tuple_delimiter}|> <relationship_strength>)

3. Return output in English as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

4. When covering the content, please use the following guidelines:
- **Person**: The candidate's name.
- **Skill**: Technical skills, tools, languages (e.g., Python, AWS, React). **IMPORTANT**: Extract EACH skill from comma-separated lists or bullet points as a SEPARATE entity. Do not group them.
- **Company**: Employers or organizations.
- **Role**: Job titles (e.g., Software Engineer, Intern).
- **School**: Educational institutions.
- **Degree**: Degrees or certifications.
- **Location**: Cities or countries.
- **Relationships**:
    - Person -> HAS_SKILL -> Skill (IMPORTANT: Ensure EVERY extracted Skill entity is linked to the Person entity with a HAS_SKILL relationship. Pay special attention to "Programming Languages" and "Technical Skills" sections.)
    - Person -> WORKED_AT -> Company
    - Person -> HAS_ROLE -> Role
    - Person -> STUDIED_AT -> School
    - Person -> HAS_DEGREE -> Degree
    - Company -> LOCATED_IN -> Location

-Example-
Text:
John Doe is a Software Engineer at Google in New York. He knows Python and Java. He studied Computer Science at MIT.
Output:
("entity" <|{tuple_delimiter}|> "John Doe" <|{tuple_delimiter}|> "Person" <|{tuple_delimiter}|> "Candidate named John Doe")
{record_delimiter}
("entity" <|{tuple_delimiter}|> "Google" <|{tuple_delimiter}|> "Company" <|{tuple_delimiter}|> "Technology company Google")
{record_delimiter}
("entity" <|{tuple_delimiter}|> "Software Engineer" <|{tuple_delimiter}|> "Role" <|{tuple_delimiter}|> "Job title Software Engineer")
{record_delimiter}
("entity" <|{tuple_delimiter}|> "New York" <|{tuple_delimiter}|> "Location" <|{tuple_delimiter}|> "City of New York")
{record_delimiter}
("entity" <|{tuple_delimiter}|> "Python" <|{tuple_delimiter}|> "Skill" <|{tuple_delimiter}|> "Programming language Python")
{record_delimiter}
("entity" <|{tuple_delimiter}|> "Java" <|{tuple_delimiter}|> "Skill" <|{tuple_delimiter}|> "Programming language Java")
{record_delimiter}
("entity" <|{tuple_delimiter}|> "MIT" <|{tuple_delimiter}|> "School" <|{tuple_delimiter}|> "Massachusetts Institute of Technology")
{record_delimiter}
("entity" <|{tuple_delimiter}|> "Computer Science" <|{tuple_delimiter}|> "Degree" <|{tuple_delimiter}|> "Field of study Computer Science")
{record_delimiter}
("relationship" <|{tuple_delimiter}|> "John Doe" <|{tuple_delimiter}|> "Google" <|{tuple_delimiter}|> "John Doe works at Google" <|{tuple_delimiter}|> "WORKED_AT" <|{tuple_delimiter}|> 10)
{record_delimiter}
("relationship" <|{tuple_delimiter}|> "John Doe" <|{tuple_delimiter}|> "Software Engineer" <|{tuple_delimiter}|> "John Doe has the role of Software Engineer" <|{tuple_delimiter}|> "HAS_ROLE" <|{tuple_delimiter}|> 10)
{record_delimiter}
("relationship" <|{tuple_delimiter}|> "Google" <|{tuple_delimiter}|> "New York" <|{tuple_delimiter}|> "Google is located in New York" <|{tuple_delimiter}|> "LOCATED_IN" <|{tuple_delimiter}|> 10)
{record_delimiter}
("relationship" <|{tuple_delimiter}|> "John Doe" <|{tuple_delimiter}|> "Python" <|{tuple_delimiter}|> "John Doe knows Python" <|{tuple_delimiter}|> "HAS_SKILL" <|{tuple_delimiter}|> 10)

{record_delimiter}
######################
Text:
Skills: C++, Go, Rust.
Output:
("entity" <|{tuple_delimiter}|> "C++" <|{tuple_delimiter}|> "Skill" <|{tuple_delimiter}|> "Programming language C++")
{record_delimiter}
("entity" <|{tuple_delimiter}|> "Go" <|{tuple_delimiter}|> "Skill" <|{tuple_delimiter}|> "Programming language Go")
{record_delimiter}
("entity" <|{tuple_delimiter}|> "Rust" <|{tuple_delimiter}|> "Skill" <|{tuple_delimiter}|> "Programming language Rust")
{record_delimiter}
("relationship" <|{tuple_delimiter}|> "Candidate" <|{tuple_delimiter}|> "C++" <|{tuple_delimiter}|> "Candidate knows C++" <|{tuple_delimiter}|> "HAS_SKILL" <|{tuple_delimiter}|> 10)
{record_delimiter}
("relationship" <|{tuple_delimiter}|> "Candidate" <|{tuple_delimiter}|> "Go" <|{tuple_delimiter}|> "Candidate knows Go" <|{tuple_delimiter}|> "HAS_SKILL" <|{tuple_delimiter}|> 10)
{record_delimiter}
("relationship" <|{tuple_delimiter}|> "Candidate" <|{tuple_delimiter}|> "Rust" <|{tuple_delimiter}|> "Candidate knows Rust" <|{tuple_delimiter}|> "HAS_SKILL" <|{tuple_delimiter}|> 10)
{record_delimiter}
######################
-Real Data-
Text:
{input_text}
Output:
"""

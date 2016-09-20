# User Story Guidelines

All core requirements for MFW must be documented as epics and user stories.  
This is because we want everything that we develop to have a clear purpose and value to the user.

## User Story Format

User stories will be organized as github issues with the 'user story' tag.

User stories must include:
* A Value Statement
* A Discussion with the dev team
* A Definition of Done

**Issue: {user-story-function-statement}**
```markdown
# {user-story-function-statement}

## Epic:
See [{Epic-filename}]({full-url-to-epic-file})

## Value Statement:
  As a {user type},  
  I can {function},  
  So that {benefit}.

## Definition of Done:  
  -[ ] {Definition of Done}
  -[ ] {...}
```

In the issue thread, devs should actively discuss the details of the user story.  
The user story should constantly be updated to reflect the discussion.

## INVEST Criteria

All User Stories must be:

- **I**ndependent - **Does not overlap** or depend on other user stories.
- **N**egotiable  - The **details are negotiable**. It is a conversation, not a stone inscription.
- **V**aluable    - **Provides real value** to the user. Is written from user's perspective in end-user language.
- **E**stimable   - The story's completion can be estimated.
- **S**mall       - Small. Each story **can be completed in a sprint**.
- **T**estable    - Not too subjective, **can actually be user tested**.

Epics are an exception. They have to be Independent, Negotiable, & Valuable.

## Epics

Epics are larger, more general stories.  
They are placed above user stories,  
and describe the purpose of the project itself.

They will be organized as markdown docs in the `/docs/epics` directory,
and should be written as such:

**{user-type}-Epics.md:**
```markdown
# {user-type} Epics

## The Super Epic

As a {user type},  
I can {function},  
So that {benefit}.

## The Epics

As a {user type},  
I can {function},  
So that {benefit}.

As a {user type},  
I can {function2},  
So that {benefit2}.

As a {user type},  
I can {function3},  
So that {benefit3}.
```

## Reference

- [What is a User Story? Is it a conversation?](https://www.mountaingoatsoftware.com/agile/user-stories)
- [How specific should a user story be?]( https://help.rallydev.com/writing-great-user-story)

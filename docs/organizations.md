# Organization model

## Purpose

The initial `Organization` model allows to regroup `User` and `Team` under a same object.

While the purpose was purely technical in the first place, few features emerged afterward.


## Link with the `User` model

Each user must have a "default" organization. 

When a user logs in:

- The backend tries to get an existing organization from a "registration ID" or from the user's mail domain
- If the organization does not exist, it is created using the "registration ID" and fallbacks on the user's mail domain
- The user organization is set to this organization.

**Note:** While deploying the new code, we allow the already existing user to not have one.


## Organization-related features

### Organization UI

A new interface can be created to allow users to see all members of an organization. 
This could be used along with the contacts.


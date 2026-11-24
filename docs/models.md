# What is People?

Space Odyssey is a dynamic organization. They use the People application to enhance teamwork and
streamline communication among  their co-workers. Let's explore how this application helps them
interact efficiently.

Let's see how we could interact with Django's shell to recreate David's environment in the app.

## Profile

The system identifies Dave through the `sub` associated with his OIDC session.
The OIDC should also provide his email address.

Note: as some Identity Providers do not provide a constant `sub`, the system should be able to
fallback to the email address to find it the user is already in the database.

When Dave logs in for the first time, the system checks if he is already in the database. If not a new user is created for him.

Users needs to be linked to an Organization (see [organizations.md](./organizations.md)).

```python
space_odyssey, _created = Organization.objects.get_or_create(...)

david_user = User.objects.create(
    organization=space_odyssey,
    language="en-us",
    timezone="America/Los_Angeles",
    name="David Bowman",
    sub="1234567890",
    email="david.bowman@spaceodyssey.com",
)
```

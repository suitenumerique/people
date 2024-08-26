## Resource Server

For detailed information, please refer to the [OAuth 2.0 Resource Server documentation](https://www.oauth.com/oauth2-servers/the-resource-server/) and review the relevant commits that implement the resource server backend.

---
#### Overview

A resource server is a crucial component in an OAuth 2.0 ecosystem. It is responsible for accepting access tokens issued by the authorization server (in this case, Agent Connect), introspecting and validating those tokens, and then returning the requested protected resources to the client.

By implementing a resource server, we can securely share data between different services within La Suite. This ensures that only clients with the appropriate scopes and permissions can access specific resources, thereby enhancing security and maintaining proper access control across services.

---
#### Disclaimer

- Currently compatible only with Agent Connect.
- The development setup requires simplification, with dependencies on Agent Connect ideally mocked.
- Terminology aligns with the specification: what is referred to as a "resource server" is known as a "data provider" in Agent Connect.
- This documentation is WIP.

---
## Running Locally

#### Prerequisites

- **Agent Connect Stack**: Ensure the local Agent Connect stack is running. A solid understanding of its configuration and operation is recommended (advanced level).
- **People Stack**: Make sure the People stack is up and running.
- **Ngrok**: Install and set up Ngrok for secure tunneling.


---

### Update People's configurations

#### Environment variables


Agent Connect includes two pre-configured mocked data providers in its default stack (`bdd-fca-low`).

Use the client ID and client secret from one of these data providers. **Note:** Make sure to retrieve the decrypted secret, as it is stored encrypted in the database. You can find these values in the `dp.js` fixture file, where they are exposed in a comment.

Configure your environment with the following values from Agent Connect:

```
OIDC_RS_CLIENT_ID=<your-client-id-from-ac>
OIDC_RS_CLIENT_SECRET=<your-decrypted-client-secret-from-ac>

# In development, the resource server use insecure settings
OIDC_VERIFY_SSL=False

# Update the endpoints as follows
OIDC_OP_JWKS_ENDPOINT=https://core-fca-low.docker.dev-franceconnect.fr/api/v2/jwks
OIDC_OP_INTROSPECTION_ENDPOINT=https://core-fca-low.docker.dev-franceconnect.fr/api/v2/checktoken
OIDC_OP_URL=https://core-fca-low.docker.dev-franceconnect.fr/api/v2
```

#### Docker Network Configuration

To enable communication between the Docker networks for People and Agent Connect, update your docker-compose configuration. This setup is required because the Authorization Server and Resource Server will exchange requests over a back-channel, necessitating their accessibility to each other.

1. **Create a Network**: Define a new network to bridge the two Docker networks.

    ```yaml
    networks:
      authorization_server:
        external: true
        driver: bridge
        name: "${DESK_NETWORK:-fc_public}"
    ```

2. **Update Network for `app-dev`**: Ensure your `app-dev` service is connected to both the default network and the new `authorization_server` network.

    ```yaml
    app-dev:
      ...
      networks:
        - default
        - authorization_server
    ```


#### Ngrok

To expose your local resource server through an HTTP tunnel, use Ngrok. This is necessary because, in the Agent Connect development stack, the resource server needs to be accessible to a user agent via a publicly accessible URL.

```
$ ngrok http 8071
```

---


### Update AgentConnect's configurations

Modify the AgentConnect configuration to include the local resource server settings.

**Update `fsa1-low` Environment File**:

Add your Ngrok URL and configure the `DATA_APIS` list with the appropriate values.

 ```env
 App_DATA_APIS=[{"name":"Data Provider 1","url":"https://your-ngrok-url/api/v1.0/any-path","secret":"***"}, ...]
 ```

**Update Fixture in `dp.js`**:

Adjust the configuration for the data provider to match your local setup. Ensure that the `client_id`, `client_secret`, and other parameters are correctly set and aligned with your environment. This can be configured through environment variables.

 ```javascript
 const dps = [
   // Data Provider Configuration
   {
     uid: "6f21b751-ed06-48b6-a59c-36e1300a368a",
     title: "Mock Data Provider - 1",
     active: true,
     slug: "DESK",
     client_id: "***",
     client_secret: "***",
       // client_secret decrypted : ****
     jwks_uri: "https://your-ngrok-url/api/v1.0/jwks", // Update this line
     checktoken_signed_response_alg: "ES256",
     checktoken_encrypted_response_alg: "RSA-OAEP",
     checktoken_encrypted_response_enc: "A256GCM",
   },
 ];
 ```

**Note**: Ensure that the `jwks_uri` and other cryptographic parameters (e.g., `checktoken_signed_response_alg`, `checktoken_encrypted_response_alg`, and `checktoken_encrypted_response_enc`) match your actual setup and are configured via environment variables where necessary.

---

### Usage

This section is a work in progress. Please note the following important points:

#### User `sub` Matching

Ensure that the `sub` (subject) field for users in AgentConnect matches the corresponding value in the People database. To synchronize this, you can run `make demo`, then edit the user's `sub` field to match the value returned by AgentConnect. For this, you'll need to update the editable field in Django Admin, specifically in `admin.py`. Adjust the `get_readonly_fields` method as follows:

```python
def get_readonly_fields(self, request, obj=None):
    """The 'sub' field should only be editable during creation, not for updates."""
    if obj:
        return self.readonly_fields
    return self.readonly_fields + ["sub"]  # update this line adding 'sub'
```

#### Scope for `groups`
Ensure that the `groups` scope is requested from the service provider during authentication with AgentConnect.

#### Resource Server Requests
By default, the `fsa1-low` environment calls the resource server using a POST request.

#### Testing

Most of the testing has been done using the `/users/me` endpoint. Update the `api/viewset.py` configuration to allow both GET and POST methods for this endpoint:

```python
@decorators.action(
    detail=False,
    methods=["get", "post"], # update this line adding 'post'
    url_name="me",
    url_path="me",
)
```

#!/bin/bash

# Script to add a new client to Keycloak using the kcadm.sh CLI
# Usage: ./add-keycloak-client.sh [client_id] [client_secret]

# Default values
CLIENT_ID=${1:-"some-client-id"}
CLIENT_SECRET=${2:-"ThisIsAnExampleKeyForDevPurposeOnly"}
KEYCLOAK_URL=${KEYCLOAK_URL:-"http://keycloak:8080"}
KEYCLOAK_ADMIN=${KEYCLOAK_ADMIN:-"admin"}
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD:-"admin"}
REALM=${REALM:-"people"}

# Check for kcadm.sh in common locations
KCADM_LOCATIONS=(
  "/opt/keycloak/bin/kcadm.sh"
  "/opt/jboss/keycloak/bin/kcadm.sh"
  "/usr/local/bin/kcadm.sh"
  "./bin/kcadm.sh"
  "$(which kcadm.sh 2>/dev/null)"
)

KCADM=""
for loc in "${KCADM_LOCATIONS[@]}"; do
  if [ -x "$loc" ]; then
    KCADM="$loc"
    break
  fi
done

if [ -z "$KCADM" ]; then
  echo "Error: kcadm.sh not found. Please specify its location manually."
  echo "You can set the KCADM environment variable to the path of kcadm.sh"
  exit 1
fi

echo "Using Keycloak Admin CLI at: $KCADM"
echo "Logging in to Keycloak at $KEYCLOAK_URL..."

# Login to Keycloak
$KCADM config credentials \
  --server $KEYCLOAK_URL \
  --realm master \
  --user $KEYCLOAK_ADMIN \
  --password $KEYCLOAK_ADMIN_PASSWORD

if [ $? -ne 0 ]; then
  echo "Failed to login to Keycloak. Please check your credentials and try again."
  exit 1
fi

echo "Successfully logged in to Keycloak."
echo "Creating new client '$CLIENT_ID' in realm '$REALM'..."

# Create a temporary JSON file with client configuration
CLIENT_JSON=$(mktemp)
cat > "$CLIENT_JSON" << EOF
{
  "clientId": "$CLIENT_ID",
  "name": "",
  "description": "",
  "rootUrl": "",
  "adminUrl": "",
  "baseUrl": "",
  "surrogateAuthRequired": false,
  "enabled": true,
  "alwaysDisplayInConsole": false,
  "clientAuthenticatorType": "client-secret",
  "secret": "$CLIENT_SECRET",
  "redirectUris": [
    "http://localhost:8070/*",
    "http://localhost:8071/*",
    "http://localhost:3200/*",
    "http://localhost:8088/*",
    "http://localhost:3000/*"
  ],
  "webOrigins": [
    "http://localhost:3200",
    "http://localhost:8088",
    "http://localhost:8070",
    "http://localhost:3000"
  ],
  "notBefore": 0,
  "bearerOnly": false,
  "consentRequired": false,
  "standardFlowEnabled": true,
  "implicitFlowEnabled": false,
  "directAccessGrantsEnabled": false,
  "serviceAccountsEnabled": false,
  "publicClient": false,
  "frontchannelLogout": true,
  "protocol": "openid-connect",
  "attributes": {
    "access.token.lifespan": "-1",
    "client.secret.creation.time": "$(date +%s)",
    "user.info.response.signature.alg": "RS256",
    "post.logout.redirect.uris": "http://localhost:8070/*##http://localhost:3200/*##http://localhost:3000/*",
    "oauth2.device.authorization.grant.enabled": "false",
    "use.jwks.url": "false",
    "backchannel.logout.revoke.offline.tokens": "false",
    "use.refresh.tokens": "true",
    "tls-client-certificate-bound-access-tokens": "false",
    "oidc.ciba.grant.enabled": "false",
    "backchannel.logout.session.required": "true",
    "client_credentials.use_refresh_token": "false",
    "acr.loa.map": "{}",
    "require.pushed.authorization.requests": "false",
    "display.on.consent.screen": "false",
    "client.session.idle.timeout": "-1",
    "token.response.type.bearer.lower-case": "false"
  },
  "authenticationFlowBindingOverrides": {},
  "fullScopeAllowed": true,
  "nodeReRegistrationTimeout": -1,
  "defaultClientScopes": [
    "web-origins",
    "acr",
    "roles",
    "profile",
    "email"
  ],
  "optionalClientScopes": [
    "address",
    "phone",
    "offline_access",
    "microprofile-jwt"
  ]
}
EOF

# Create the client using kcadm.sh
$KCADM create clients -r "$REALM" -f "$CLIENT_JSON"

if [ $? -ne 0 ]; then
  echo "Failed to create client. Check the error message above."
  rm "$CLIENT_JSON"
  exit 1
fi

echo "✅ Client '$CLIENT_ID' created successfully!"
echo "  Client ID: $CLIENT_ID"
echo "  Client Secret: $CLIENT_SECRET"

# Clean up temporary file
rm "$CLIENT_JSON"

# Display the created client
echo "Client details:"
$KCADM get clients -r "$REALM" --query "clientId=$CLIENT_ID"

"""Forms for the demo helpers."""

from django import forms


class TokenExchangeDemoForm(forms.Form):
    """Simple form to craft a token exchange request payload."""

    client_id = forms.CharField(
        required=False,
        label="client_id (Basic Auth)",
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
        help_text="Used only to build the Authorization header",
    )
    client_secret = forms.CharField(
        required=False,
        label="client_secret (Basic Auth)",
        widget=forms.PasswordInput(render_value=True, attrs={"autocomplete": "off"}),
        help_text="Used only to build the Authorization header",
    )
    grant_type = forms.CharField(
        required=True,
        initial="urn:ietf:params:oauth:grant-type:token-exchange",
        widget=forms.TextInput(attrs={"size": 60}),
    )
    subject_token = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={"rows": 3, "placeholder": "Access token to exchange"}
        ),
    )
    subject_token_type = forms.CharField(
        required=True,
        initial="urn:ietf:params:oauth:token-type:access_token",
        widget=forms.TextInput(attrs={"size": 60}),
    )
    requested_token_type = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"size": 60}),
        help_text="Optional: e.g. urn:ietf:params:oauth:token-type:jwt",
    )
    audience = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"size": 60}),
        help_text="Optional: space separated audience identifiers",
    )
    scope = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"size": 60}),
        help_text="Optional: space separated scopes",
    )
    actor_token = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
    )
    actor_token_type = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"size": 60}),
    )
    resource = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"size": 60}),
    )
    expires_in = forms.IntegerField(
        required=False,
        min_value=1,
        help_text="Optional: lifetime in seconds",
    )

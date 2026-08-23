# Interoperability with Matrix API

Matrix is a protocol for secure, decentralized communication. It's the protocol used by [Tchap](https://www.tchap.gouv.fr/), another application of [La Suite](https://lasuite.numerique.gouv.fr/).

## Purpose

With webhooks using this protocol, you can automate the invitation and removal of your colleagues' accounts to Matrix chat rooms.

> [!NOTE]   
> The first version of this feature requires inviting a bot and giving it moderation permission to your Matrix room. This won't be necessary in future versions of the feature, as invitations/removal will be made in your name using OIDC tokens.

## For devs

Client methods follow syntax from [Matrix Client-Server API v1.14]https://spec.matrix.org/v1.14/client-server-api/
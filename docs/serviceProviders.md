# ServiceProvider model

## Purpose

The `ServiceProvider` model represents a ... service provider, also known as "tools using some data from this project".


## Link with the `Organization` model

An organization can be linked to several service providers. 
The goal here, is to allow users of an organization to have access, to a service provider or not.
The first implementation does not have any feature related, but the first feature will probably be
to list applications visible in the "all application menu" (aka "la gaufre").


## Link with the `Team` model

A team can be linked to several service providers.
This is used as a filter when a service provider calls the resource server, only the teams linked to
this service provider are returned. This is mandatory for data segregation: we don't want all service
providers to be able to list all data regarding other service providers.


## Limitations

There is currently no way to provision all the service providers automatically. So when a service provider
creates a team via the resource server, we create the `ServiceProvider` on the fly, without any understandable name.
This will need to be improved later.

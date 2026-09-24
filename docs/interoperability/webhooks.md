# General considerations on webhooks

Webhooks are small add-ons you can link to your teams to automate the sending of information from People to other apps. Configure your webhooks to point to the tools or ressources you want to share with your group (such as a chatroom, a kanban board or a specific collection in your knowledge base). Whenever you add (or remove) someone from your team in People, access will also be granted (or revoked) to your resources. 

## Requirements for webhook clients

Your webhook client must contain "invite_user_to_group" and "remove_user_from_group" methods, describing how to connect to your ressource and to grant and revoke accesses. 

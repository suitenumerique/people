# General considerations on webhooks

In People, webhooks send permissions to all the applications used by your team. Configure your webhooks to point to the resources you want to share with your group (such as a chatroom, your kanban board or your knowledge database), and then add or remove group members in People to automatically grant/revoke access to said ressources. 

People keeps track of all changes to group composition for security reasons.

## Requirements for webhooks

Your webhook client must contain "invite_user_to_group" and "remove_user_from_group" methods, describing how to connect to your ressource and to grant and revoke accesses. 

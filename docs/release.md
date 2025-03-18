# Releasing a new version

Whenever we are cooking a new release (e.g. `4.18.1`) we should follow a standard procedure described below:

1.  Checkout and pull changes from the `main` branch to ensure you have the latest updates.

    ```bash
    git checkout main
    git pull
    ```

2.  The next steps are automated in the `scripts/release.py`, you can run it using:

    ```bash
    make release
    ```

    This script will ask you for the version you want to release and the kind of release (patch, minor, major). It will then:

    - Create a new branch named: `release/4.18.1`.

    - Bump the release number for backend and frontend project.

    - Update the project's `Changelog` following the [keepachangelog](https://keepachangelog.com/en/0.3.0/) recommendations

    - Commit your changes with the following format: 🔖 release emoji, type of release (patch/minor/patch) and release version:
    
        ```text
        🔖(minor) release version 4.18.1
        ```

    - Triggers Crowdin translation action and open related PR

    - Open release PR. Wait for an approval from your peers and merge it.

    > [!NOTE]  
    > It also open the PR for pre-prod deployment, see following section.

3.  Following release script instructions, 

    - merge translation and release pulls requests

    - tag and push your commit:

    ```bash
    git tag v4.18.1 && git push origin tag v4.18.1
    ```

    This triggers the CI building new Docker images. You can ensure images were successfully built on Docker Hub [here for back-end](https://hub.docker.com/r/lasuite/people-backend/tags) and [here for front-end](https://hub.docker.com/r/lasuite/people-frontend/tags).


# Deploying 

## Staging

The `staging` platform is deployed automatically with every update of the `main` branch.

## Pre-prod and production

If you used the release script and had permission to push on [lasuite-deploiement](https://github.com/numerique-gouv/lasuite-deploiement), a deployment branch has been created. You can skip step 1.

Otherwise, for manual preprod and for production deployments :
1. Bump tag version for both front-end and back-end images in the `.gotmpl` file located in `manifests/<your-product>/env.d/<your-environment>/`, 
2. Add optional new secrets and variables, if applicable
3. Create a pull request
4. Submit to approval and merge PR

The release is now done! 🎉

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

    1.  Create a new branch named: `release/4.18.1`.

    2.  Bump the release number for backend and frontend project.

    3.  Update the project's `Changelog` following the [keepachangelog](https://keepachangelog.com/en/0.3.0/) recommendations

    4.  Commit your changes with the following format: the 🔖 release emoji, the type of release (patch/minor/patch) and the release version:
    
        ```text
        🔖(minor) release version 4.18.1
        ```

    5. Open a PR. Wait for an approval from your peers and merge it.

    > [!NOTE]  
    > It also open the PR for pre-prod deployment, see following section.

3.  Following release script instructions, tag and push your commit:

    ```bash
    git tag v4.18.1 && git push origin tag v4.18.1
    ```

    Doing this triggers the CI and tells it to build the new Docker image versions that you targeted earlier in the Helm files.
    
    You can ensure the new [backend](https://hub.docker.com/r/lasuite/people-backend/tags) and [frontend](https://hub.docker.com/r/lasuite/people-frontend/tags) image tags are on Docker Hub.


# Deploying 

## Staging

The `staging` platform is deployed automatically with every update of the `main` branch.

## Pre-prod and production

If you used the release script and had permission to push on [lasuite-deploiement](https://github.com/numerique-gouv/lasuite-deploiement), a deployment branch has been created. You can skip step 1.

Otherwise, for manual pre-prod and production deployments :
1. Bump tag version for both front-end and back-end images in the `.gotmpl` file located in `manifests/<your-product>/env.d/<your-environment>/`, 
2. Add optional new secrets and variables, if applicable
3. Create a pull request
4. Wait for approval and merge PR

The release is now done! 🎉

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

3.  Open a pull request ask you to wait for an approval from your peers and merge it.

4.  Ask you to tag and push your commit:

    ```bash
    git tag v4.18.1 && git push origin tag v4.18.1
    ```

    Doing this triggers the CI and tells it to build the new Docker image versions that you targeted earlier in the Helm files.

5.  Ensure the new [backend](https://hub.docker.com/r/lasuite/people-backend/tags) and [frontend](https://hub.docker.com/r/lasuite/people-frontend/tags) image tags are on Docker Hub.

6. Create a PR on the [lasuite-deploiement](https://github.com/numerique-gouv/lasuite-deploiement) repository to bump the preprod version.

7.  The release is now done!

# Deploying

> [!TIP]
> The `staging` platform is deployed automatically with every update of the `main` branch.

Making a new release doesn't publish it automatically in production.

Deployment is done by ArgoCD. ArgoCD checks for the `production` tag and automatically deploys the production platform with the targeted commit.

To publish, we mark the commit we want with the `production` tag. ArgoCD is then notified that the tag has changed. It then deploys the Docker image tags specified in the Helm files of the targeted commit.

To publish the release you just made:

```bash
git tag --force production v4.18.1
git push --force origin production
```

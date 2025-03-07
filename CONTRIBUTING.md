# Contributing to the Project

Thank you for taking the time to contribute! Please follow these guidelines to ensure a smooth and productive workflow. 🚀🚀🚀

To get started with the project, please refer to the [README.md](https://github.com/suitenumerique/docs/blob/main/README.md) for detailed instructions.

Please also check out our [dev handbook](https://suitenumerique.gitbook.io/handbook) to learn our best practices.

## Help us with translations

You can help us with translations on [Crowdin](https://crowdin.com/project/lasuite-people).
Your language is not there? Request it on our Crowdin page 😊.

## Creating an Issue

When creating an issue, please provide the following details:

1.  **Title**: A concise and descriptive title for the issue.
2.  **Description**: A detailed explanation of the issue, including relevant context or screenshots if applicable.
3.  **Steps to Reproduce**: If the issue is a bug, include the steps needed to reproduce the problem.
4.  **Expected vs. Actual Behavior**: Describe what you expected to happen and what actually happened.
5.  **Labels**: Add appropriate labels to categorize the issue (e.g., bug, feature request, documentation).

## Selecting an issue

We use a [GitHub Project](https://github.com/orgs/suitenumerique/projects/1) in order to prioritize our workload. 

Please check in priority the issues that are in the **TODO cette semaine** column. 

## Commit Message Format

All commit messages must adhere to the following format:

`<gitmoji>(type) title description`

*   <**gitmoji**>: Use a gitmoji to represent the purpose of the commit. For example, ✨ for adding a new feature or 🔥 for removing something, see the list here: <https://gitmoji.dev/>.
*   **(type)**: Describe the type of change. Common types include `backend`, `frontend`, `CI`, `docker` etc...
*   **title**: A short, descriptive title for the change, starting with a lowercase character.
*   **description**: Include additional details about what was changed and why.

### Example Commit Message

```
✨(frontend) add user authentication logic 

Implemented login and signup features, and integrated OAuth2 for social login.
```

## Changelog Update

Please add a line to the changelog describing your development. The changelog entry should include a brief summary of the changes, this helps in tracking changes effectively and keeping everyone informed. We usually include the title of the pull request, followed by the pull request ID to finish the log entry. The changelog line should be less than 80 characters in total.

### Example Changelog Message
```
## [Unreleased]

## Added

- ✨(frontend) add AI to the project #321
```

## Pull Requests

It is nice to add information about the purpose of the pull request to help reviewers understand the context and intent of the changes. If you can, add some pictures or a small video to show the changes.

### Don't forget to: 
- check your commits
- check the linting: `make lint && make frontend-lint`
- check the tests: `make test`
- add a changelog entry
- squash your commits
- rebase your branch on the latest `main` branch before pushing your changes `git pull --rebase origin main`

### Process to have a nice commit history

In the life time of your PR, you may need to add commits to fix things or add new features.
Commit after commit, your PR will be full of commits but you have to clean it up with the following commands before merging on `main`:

Gradually you can use `--fixup` to add commits to some of previous commit ( for example 1234567890).
```
git commit --fixup=1234567890
```
Then, you can squash your commits with the following command:
```
git rebase --autosquash -i -r  HEAD~<number-of-commits>
```

Or you can use:
```
git rebase -i HEAD~<number-of-commits>
```
and move, squash and/or rename your commits manually. You can squash them with previous commit replacing the `pick` by `f`. You can rename them with replacing the `pick` by `r`.
Tada! You have a clean commit history.

Once all the required tests have passed, you can request a review from the project maintainers.

## Code Style

Please maintain consistency in code style. Run any linting tools available to make sure the code is clean and follows the project's conventions.

## Tests

Make sure that all new features or fixes have corresponding tests. Run the test suite before pushing your changes to ensure that nothing is broken.

## Asking for Help

If you need any help while contributing, feel free to open a discussion or ask for guidance in the issue tracker. We are more than happy to assist!

Thank you for your contributions! 👍

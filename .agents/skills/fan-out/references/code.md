# Fan out: code

Use these steps along with SKILL.md when the batch is code.

## Split

- Ownership covers every kind of file: app code, web code, backend functions, and database migrations.
- If two workers each need a database or backend change, give each of them its own migrations and functions, so neither overwrites the other's.

## Workers

- Each worker runs as a side session in its own worktree, on its own branch.
- Workers build and run unit tests only. They don't use the simulator or a device, and they don't deploy. There is usually only one simulator and one dev environment, so you use those after merging.
- Each worker commits to its own branch and reports the branch name.

## While they work

- Build the main branch and take "before" screenshots of every screen the batch will change.

## Integrate and check

- Merge every branch into one integration branch. Resolve conflicts, and note each one on the review page.
- Run every test suite and build.
- Deploy to the dev or staging environment only, the way the project's rules say. Never production unless the user asks.
- Run the app and walk each change as a user would. Take each "after" screenshot from the same place as its "before".
- Check every shared rule everywhere it shows up: app, web, emails, push notifications.

## Hand over

- Open a draft PR for the integration branch, and link it from the review page.
- Put the screenshots in an `img/` folder next to the review page, and publish them with it.
- The review page's "Try it yourself" box says what's running now, what account it's signed in as, and how to get test data.

## After review

- Push fixes to the same branch, so the same PR updates.

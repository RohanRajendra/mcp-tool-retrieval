# Sample queries and relevance judgments

Ten of the 24 sample queries, judged against the real tool collection (`data/tools.jsonl`, 384 tools from 13 MCP servers). Machine-readable copy: `data/sample_judgments.jsonl`.

**Relevance scale**

- **3**: does the request, or one required step of a multi-step request, by itself.
- **2**: does it partly, or only with extra steps.
- **1**: related, but cannot do the request.
- **0**: not relevant.

**Equivalent tools** that do the same job share a group name (for example `file-metadata`), even when they come from different vendors.

**Which tools were judged:** for each query, the top 10 results of a plain keyword search (BM25 over tool name and description), plus tools added by hand that can do the job but the search missed.

## 1. List all tables in my local Postgres database

**Narrative.** The user is connected to a local Postgres database and wants the names of its tables, to get oriented before writing queries. A relevant tool returns the table names. A general SQL tool also works, but the agent must write a catalog query first. Tools that list schemas or roles, or show performance stats, do not answer the question.

BM25's top 10 contained 4 of the 5 relevant tools (grade 2 or 3) we found.

| Tool | Server | Grade | Group | Source | Why |
|---|---|---|---|---|---|
| `list_tables` | Postgres (antonorlov) | 3 | list-tables | bm25 #2 | Lists all tables in a schema |
| `pg_list_tables` | Postgres (YawLabs) | 3 | list-tables | bm25 #8 | Lists tables in a schema |
| `pg_query` | Postgres (YawLabs) | 2 | run-sql | bm25 #3 | Works, but needs a hand-written catalog query |
| `pg_readonly` | Postgres (YawLabs) | 2 | run-sql | bm25 #4 | Same as pg_query, read-only |
| `query` | Postgres (antonorlov) | 2 | run-sql | added by hand | Works, but needs a hand-written catalog query |
| `list_schemas` | Postgres (antonorlov) | 1 |  | bm25 #1 | Lists schemas, not tables |
| `pg_list_schemas` | Postgres (YawLabs) | 1 |  | added by hand | Lists schemas, not tables |
| `pg_list_roles` | Postgres (YawLabs) | 0 |  | bm25 #7 | Lists users and roles |
| `pg_top_queries` | Postgres (YawLabs) | 0 |  | bm25 #6 | Query performance stats |
| `pg_advisor` | Postgres (YawLabs) | 0 |  | bm25 #9 | Database health checks |
| `pg_inspect_locks` | Postgres (YawLabs) | 0 |  | bm25 #10 | Shows lock contention |
| `pg_kill` | Postgres (YawLabs) | 0 |  | bm25 #5 | Cancels running queries |

## 2. Show me the commits made on this repo yesterday

**Narrative.** The user wants the list of commits made yesterday in the repository they are working on (a local clone that is also on GitHub). Relevant tools list commit history and can filter by date. Tools that change history (rebase, cherry-pick, push) or show one commit or a diff are not what they asked for.

BM25's top 10 contained 2 of the 4 relevant tools (grade 2 or 3) we found.

| Tool | Server | Grade | Group | Source | Why |
|---|---|---|---|---|---|
| `git_log` | Git (reference) | 3 | commit-history | added by hand | Commit log with start and end time filters |
| `git_log` | Git (cyanheads) | 3 | commit-history | added by hand | Commit history with since/until filters |
| `list_commits` | GitHub (official) | 3 | commit-history | bm25 #5 | Lists commits on GitHub with since/until |
| `search_commits` | GitHub (official) | 2 | commit-history | bm25 #6 | Date search works, but default branch only |
| `git_show` | Git (cyanheads) | 1 |  | bm25 #7 | Shows one commit; needs its ID first |
| `git_diff` | Git (reference) | 1 |  | bm25 #9 | Shows changes, not the list of commits |
| `git_diff` | Git (cyanheads) | 1 |  | bm25 #10 | Shows changes, not the list of commits |
| `git_rebase` | Git (cyanheads) | 0 |  | bm25 #3 | Rewrites history |
| `git_cherry_pick` | Git (cyanheads) | 0 |  | bm25 #4 | Copies commits between branches |
| `git_push` | Git (cyanheads) | 0 |  | bm25 #8 | Uploads commits |
| `container_diff` | Docker (L337-org) | 0 |  | bm25 #1 | Docker container file changes |
| `image_list` | Docker (L337-org) | 0 |  | bm25 #2 | Lists Docker images |

## 6. Run my test suite in an isolated container and show any failures

**Narrative.** The user wants their tests to run in a fresh, throwaway container so their machine is not affected, and wants to see which tests failed. Steps: start a new container with the test command, then read its output. Running a command in a container that is already running, or reading logs, covers part of the job. Listing containers, installing plugins or diffing files does not help.

BM25's top 10 contained 4 of the 7 relevant tools (grade 2 or 3) we found.

| Tool | Server | Grade | Group | Source | Why |
|---|---|---|---|---|---|
| `container_run` | Docker (L337-org) | 3 | run-new-container | bm25 #7 | Runs a new container and can wait for the result |
| `compose_run` | Docker (L337-org) | 2 | run-new-container | bm25 #8 | Works only with a Compose file; output fetched separately |
| `container_exec` | Docker (L337-org) | 2 | run-in-running-container | bm25 #4 | Runs a command, but needs a running container |
| `exec_command` | Docker (ofershap) | 2 | run-in-running-container | added by hand | Runs a command, but needs a running container |
| `container_logs` | Docker (L337-org) | 2 | container-output | added by hand | Shows the test output after a detached run |
| `container_logs` | Docker (ofershap) | 2 | container-output | added by hand | Shows the test output after a detached run |
| `compose_logs` | Docker (L337-org) | 2 | container-output | bm25 #9 | Shows output of a Compose run |
| `container_start` | Docker (L337-org) | 1 |  | bm25 #10 | Starts an existing container; cannot create one |
| `container_list` | Docker (L337-org) | 0 |  | bm25 #1 | Lists containers |
| `container_diff` | Docker (L337-org) | 0 |  | bm25 #3 | Container file changes |
| `plugin_install` | Docker (L337-org) | 0 |  | bm25 #2 | Installs a Docker plugin |
| `replace_text` | Filesystem (j0hanz) | 0 |  | bm25 #6 | Edits files |
| `query` | Postgres (antonorlov) | 0 |  | bm25 #5 | Runs SQL |

## 7. Find the spending report files and move them to a new folder called expenditure

**Narrative.** The user has spending report files in their project and wants them gathered into a new folder named "expenditure". Steps: find the files by name, create the folder, move each file. A tool that fully does one of these steps is relevant. Browsing folders can find the files, but with extra work.

BM25's top 10 contained 5 of the 8 relevant tools (grade 2 or 3) we found.

| Tool | Server | Grade | Group | Source | Why |
|---|---|---|---|---|---|
| `search_files` | Filesystem (reference) | 3 | find-by-name | added by hand | Finds files by name pattern |
| `find_files` | Filesystem (j0hanz) | 3 | find-by-name | bm25 #6 | Finds files by name pattern |
| `create_directory` | Filesystem (reference) | 3 | make-folder | added by hand | Creates the new folder |
| `create` | Filesystem (j0hanz) | 3 | make-folder | bm25 #8 | Creates folders (and files) |
| `move_file` | Filesystem (reference) | 3 | move-file | bm25 #1 | Moves a file |
| `move` | Filesystem (j0hanz) | 3 | move-file | bm25 #7 | Moves files; creates missing folders too |
| `list_directory` | Filesystem (reference) | 2 | browse-folder | added by hand | Can find the files by browsing, with extra steps |
| `list` | Filesystem (j0hanz) | 2 | browse-folder | bm25 #2 | Can find the files by browsing, with extra steps |
| `search_text` | Filesystem (j0hanz) | 1 |  | bm25 #10 | Searches inside files, not names |
| `stat` | Filesystem (j0hanz) | 1 |  | bm25 #5 | Checks a path exists; cannot find or move |
| `delete` | Filesystem (j0hanz) | 0 |  | bm25 #3 | Deletes files |
| `git_worktree` | Git (cyanheads) | 0 |  | bm25 #4 | Git working trees |
| `git_checkout` | Git (cyanheads) | 0 |  | bm25 #9 | Switches Git branches |

## 12. Add the “bug” label to issue 42 and assign it to me

**Narrative.** The user is triaging issue 42 in their GitHub repository and wants it labeled "bug" and assigned to themselves. A tool that updates an issue's labels and assignees does it in one call. Looking up the user's own login helps fill in "me". Commenting, reading, or assigning someone else does not do the job.

BM25's top 10 contained 1 of the 2 relevant tools (grade 2 or 3) we found.

| Tool | Server | Grade | Group | Source | Why |
|---|---|---|---|---|---|
| `issue_write` | GitHub (official) | 3 | update-issue | bm25 #7 | Updates labels and assignees in one call |
| `get_me` | GitHub (official) | 2 | who-am-i | added by hand | Finds the user's login to assign |
| `assign_copilot_to_issue` | GitHub (official) | 1 |  | bm25 #1 | Assigns Copilot, not the user |
| `issue_read` | GitHub (official) | 1 |  | bm25 #6 | Reads the issue; cannot change it |
| `get_label` | GitHub (official) | 1 |  | bm25 #10 | Checks the label exists; cannot apply it |
| `ui_get` | GitHub (official) | 1 |  | bm25 #8 | Lists labels and assignees; cannot apply them |
| `add_issue_comment` | GitHub (official) | 0 |  | bm25 #2 | Adds a comment, not a label |
| `update_issue_comment` | GitHub (official) | 0 |  | bm25 #9 | Edits a comment |
| `sub_issue_write` | GitHub (official) | 0 |  | bm25 #3 | Links sub-issues |
| `list_issue_types` | GitHub (official) | 0 |  | bm25 #5 | Issue types are not labels |
| `network_connect` | Docker (L337-org) | 0 |  | bm25 #4 | Docker networking |

## 15. How big is backup.zip and when was it last changed?

**Narrative.** The user wants two facts about one file: its size and when it was last modified, for example to check that a backup is recent. A tool that returns a file's metadata answers both. A folder listing with sizes answers only half. Database, container, browser and Git tools are not relevant.

BM25's top 10 contained 0 of the 4 relevant tools (grade 2 or 3) we found.

| Tool | Server | Grade | Group | Source | Why |
|---|---|---|---|---|---|
| `get_file_info` | Filesystem (reference) | 3 | file-metadata | added by hand | Returns size and last-modified time |
| `stat` | Filesystem (j0hanz) | 3 | file-metadata | added by hand | Returns size and timestamps |
| `list_directory_with_sizes` | Filesystem (reference) | 2 | list-with-sizes | added by hand | Shows size, but not the date |
| `list` | Filesystem (j0hanz) | 2 | list-with-sizes | added by hand | Shows size (with includeSizes), not the date |
| `git_blame` | Git (cyanheads) | 0 |  | bm25 #9 | Per-line Git history; not for a zip on disk |
| `volume_inspect` | Docker (L337-org) | 0 |  | bm25 #1 | Docker volume details |
| `pg_table_bloat` | Postgres (YawLabs) | 0 |  | bm25 #2 | Database table sizes |
| `close_page` | Chrome DevTools (Google) | 0 |  | bm25 #3 | Closes a browser tab |
| `list_console_messages` | Chrome DevTools (Google) | 0 |  | bm25 #4 | Browser console |
| `list_network_requests` | Chrome DevTools (Google) | 0 |  | bm25 #5 | Browser network log |
| `replace_text` | Filesystem (j0hanz) | 0 |  | bm25 #6 | Edits files |
| `append_file` | Filesystem (reference) | 0 |  | bm25 #7 | Writes to a file |
| `scout_sbom` | Docker (L337-org) | 0 |  | bm25 #8 | Image package list |
| `pg_seq_scan_tables` | Postgres (YawLabs) | 0 |  | bm25 #10 | Database scan stats |

## 16. What have I changed since my last commit?

**Narrative.** The user is in a local Git repository and wants to see their uncommitted work: which files changed and what the changes are, staged or not. A status tool shows the changed files; a diff against the last commit shows the changes. Tools that show past commits, make commits or stage files do not answer it.

BM25's top 10 contained 0 of the 6 relevant tools (grade 2 or 3) we found.

| Tool | Server | Grade | Group | Source | Why |
|---|---|---|---|---|---|
| `git_status` | Git (reference) | 3 | working-tree-status | added by hand | Lists changed files |
| `git_status` | Git (cyanheads) | 3 | working-tree-status | added by hand | Lists staged, unstaged and untracked files |
| `git_diff` | Git (cyanheads) | 3 | uncommitted-diff | added by hand | Diffs the working tree, staged or not |
| `git_diff` | Git (reference) | 2 | uncommitted-diff | added by hand | Works only if the agent passes HEAD as target |
| `git_diff_unstaged` | Git (reference) | 2 | uncommitted-diff | added by hand | Shows unstaged changes only |
| `git_diff_staged` | Git (reference) | 2 | uncommitted-diff | added by hand | Shows staged changes only |
| `get_commit` | GitHub (official) | 1 |  | bm25 #4 | Shows a pushed commit, not uncommitted work |
| `git_log` | Git (cyanheads) | 1 |  | bm25 #6 | Past commits, not uncommitted work |
| `git_show` | Git (cyanheads) | 1 |  | bm25 #7 | Shows the last commit, not changes since |
| `git_add` | Git (cyanheads) | 0 |  | bm25 #5 | Stages files |
| `git_commit` | Git (cyanheads) | 0 |  | bm25 #8 | Makes a commit |
| `git_commit` | Git (reference) | 0 |  | bm25 #10 | Makes a commit |
| `list_console_messages` | Chrome DevTools (Google) | 0 |  | bm25 #1 | Browser console |
| `list_network_requests` | Chrome DevTools (Google) | 0 |  | bm25 #2 | Browser network log |
| `pg_seq_scan_tables` | Postgres (YawLabs) | 0 |  | bm25 #3 | Database scan stats |
| `node_update` | Docker (L337-org) | 0 |  | bm25 #9 | Docker Swarm nodes |

## 21. Open my local site at localhost:3000 and tell me if the browser console shows any errors

**Narrative.** The user is building a web app and wants an agent to load it in a real browser and report errors in the browser console. Steps: open the URL, then read the console messages. A tool that fully does either step is relevant. Fetching the page without a browser cannot see console errors.

BM25's top 10 contained 4 of the 6 relevant tools (grade 2 or 3) we found.

| Tool | Server | Grade | Group | Source | Why |
|---|---|---|---|---|---|
| `browser_navigate` | Playwright (Microsoft) | 3 | open-page | added by hand | Opens the URL |
| `navigate_page` | Chrome DevTools (Google) | 3 | open-page | added by hand | Opens the URL |
| `new_page` | Chrome DevTools (Google) | 3 | open-page | bm25 #6 | Opens the URL in a new tab |
| `browser_console_messages` | Playwright (Microsoft) | 3 | console-messages | bm25 #1 | Returns console messages |
| `list_console_messages` | Chrome DevTools (Google) | 3 | console-messages | bm25 #4 | Lists console messages |
| `get_console_message` | Chrome DevTools (Google) | 2 | console-messages | bm25 #3 | One message by ID; needs the list first |
| `list_pages` | Chrome DevTools (Google) | 1 |  | bm25 #2 | Lists open tabs |
| `set_logpoints` | Chrome DevTools (Google) | 1 |  | bm25 #10 | Adds console logging; does not read errors |
| `fetch` | Fetch (reference) | 1 |  | bm25 #7 | Loads the page without a browser; no console |
| `close_page` | Chrome DevTools (Google) | 0 |  | bm25 #5 | Closes a tab |
| `fetch_robots` | Fetch (YawLabs) | 0 |  | bm25 #8 | Reads robots.txt |
| `stat` | Filesystem (j0hanz) | 0 |  | bm25 #9 | File metadata |

## 22. Get the README of the psf/requests project on GitHub

**Narrative.** The user wants to read the README of a public GitHub project (psf/requests). A GitHub tool that reads a file from a repository does it directly. A web fetch tool also works by loading the project's page, but the agent must build the URL. Tools for pull requests, releases, tags or the user's profile are not relevant.

BM25's top 10 contained 1 of the 4 relevant tools (grade 2 or 3) we found.

| Tool | Server | Grade | Group | Source | Why |
|---|---|---|---|---|---|
| `get_file_contents` | GitHub (official) | 3 | read-repo-file | bm25 #9 | Reads README.md from the repository |
| `fetch` | Fetch (reference) | 2 | fetch-web-page | added by hand | Works if the agent builds the GitHub URL |
| `fetch_html_to_markdown` | Fetch (YawLabs) | 2 | fetch-web-page | added by hand | Works if the agent builds the GitHub URL |
| `fetch_reader` | Fetch (YawLabs) | 2 | fetch-web-page | added by hand | Works if the agent builds the GitHub URL |
| `search_repositories` | GitHub (official) | 1 |  | bm25 #1 | Finds the repository, not the README text |
| `get_latest_release` | GitHub (official) | 0 |  | bm25 #8 | Release notes |
| `list_pull_requests` | GitHub (official) | 0 |  | bm25 #2 | Pull requests |
| `search_pull_requests` | GitHub (official) | 0 |  | bm25 #3 | Pull requests |
| `request_copilot_review` | GitHub (official) | 0 |  | bm25 #4 | Requests a code review |
| `get_me` | GitHub (official) | 0 |  | bm25 #5 | The user's own profile |
| `get_tag` | GitHub (official) | 0 |  | bm25 #6 | Git tags |
| `get_commit` | GitHub (official) | 0 |  | bm25 #7 | One commit |
| `get_release_by_tag` | GitHub (official) | 0 |  | bm25 #10 | Release notes |

## 23. Spin up a throwaway Postgres 16 database in a container on port 5432

**Narrative.** The user wants a temporary Postgres 16 server running in a container on port 5432, for local testing. A tool that runs a new container from an image with a port mapping does it in one call. The Postgres tools look relevant because the query says "Postgres", but they need a database that is already running, so they cannot help.

BM25's top 10 contained 0 of the 2 relevant tools (grade 2 or 3) we found.

| Tool | Server | Grade | Group | Source | Why |
|---|---|---|---|---|---|
| `container_run` | Docker (L337-org) | 3 | run-new-container | added by hand | Runs a new container with a port mapping |
| `container_create` | Docker (L337-org) | 2 | create-container | added by hand | Works, but needs a separate start |
| `service_create` | Docker (L337-org) | 1 |  | bm25 #10 | Needs a Docker Swarm cluster |
| `image_pull` | Docker (L337-org) | 1 |  | added by hand | Downloads the image; does not start it |
| `start_container` | Docker (ofershap) | 1 |  | added by hand | Starts an existing container; cannot create one |
| `compose_port` | Docker (L337-org) | 1 |  | bm25 #1 | Shows a published port; starts nothing |
| `pg_query` | Postgres (YawLabs) | 0 |  | bm25 #2 | Needs a running database |
| `pg_readonly` | Postgres (YawLabs) | 0 |  | bm25 #4 | Needs a running database |
| `pg_kill` | Postgres (YawLabs) | 0 |  | bm25 #3 | Cancels queries |
| `pg_top_queries` | Postgres (YawLabs) | 0 |  | bm25 #6 | Query stats |
| `pg_list_roles` | Postgres (YawLabs) | 0 |  | bm25 #9 | Database roles |
| `list_schemas` | Postgres (antonorlov) | 0 |  | bm25 #7 | Needs a running database |
| `fetch_sitemap` | Fetch (YawLabs) | 0 |  | bm25 #5 | Reads a sitemap |
| `container_diff` | Docker (L337-org) | 0 |  | bm25 #8 | Container file changes |

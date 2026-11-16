# Sample queries and relevance judgments

Queries 1 to 12 from `docs/sample_queries.txt`, judged against the real tool collection (`data/tools.jsonl`, 384 tools from 13 MCP servers). Machine-readable copy: `data/sample_judgments_q1-12.jsonl`.

**Relevance scale**

- **3**: does the request, or one required step of a multi-step request, by itself.
- **2**: does it partly, only with extra steps, or looks up something a step needs (like the user's login).
- **1**: related, but cannot do the request.
- **0**: not relevant.

Each tool gets the highest grade that fits.

**Equivalent tools** that do the same job share a group name (for example `file-metadata`), even when they come from different vendors.

**Which tools were judged:** for each query, the top 10 results of a plain keyword search (BM25 over tool name and description), plus tools the judge added during judging because the search missed them.

## 1. List all tables in my local Postgres database

**Narrative.** The user is connected to a local Postgres database and wants the names of its tables, to get oriented before writing queries. A relevant tool returns the table names. A general SQL tool also works, but the agent must write a catalog query first. Tools that list schemas or roles, or show performance stats, do not answer the question.

BM25's top 10 contained 4 of the 5 relevant tools (grade 2 or 3) we found.

| Tool | Server | Grade | Group | Source | Why |
|---|---|---|---|---|---|
| `list_tables` | Postgres (antonorlov) | 3 | list-tables | bm25 #2 | Lists all tables in a schema |
| `pg_list_tables` | Postgres (YawLabs) | 3 | list-tables | bm25 #8 | Lists tables in a schema |
| `pg_query` | Postgres (YawLabs) | 2 | run-sql | bm25 #3 | Works, but needs a hand-written catalog query |
| `pg_readonly` | Postgres (YawLabs) | 2 | run-sql | bm25 #4 | Same as pg_query, read-only |
| `query` | Postgres (antonorlov) | 2 | run-sql | added during judging | Works, but needs a hand-written catalog query |
| `list_schemas` | Postgres (antonorlov) | 1 |  | bm25 #1 | Lists schemas, not tables |
| `pg_list_schemas` | Postgres (YawLabs) | 1 |  | added during judging | Lists schemas, not tables |
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
| `git_log` | Git (reference) | 3 | commit-history | added during judging | Commit log with start and end time filters |
| `git_log` | Git (cyanheads) | 3 | commit-history | added during judging | Commit history with since/until filters |
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

## 3. Scan this repo’s history for leaked API keys or passwords

**Narrative.** The user wants to check every past commit in their repository for secrets committed by mistake, such as API keys or passwords, even ones deleted later. No tool in this starter collection scans for secrets directly. (GitHub's server has secret-scanning tools, but they are off by default, so they were not collected.) The closest tools show the content of past commits, so the agent must search that output for key-like patterns itself. Searching only the current files misses secrets that were removed in later commits.

BM25's top 10 contained 0 of the 5 relevant tools (grade 2 or 3) we found.

| Tool | Server | Grade | Group | Source | Why |
|---|---|---|---|---|---|
| `git_log` | Git (cyanheads) | 2 | commit-contents | added during judging | Can show every commit's changes; agent must spot the keys |
| `git_show` | Git (cyanheads) | 2 | commit-contents | added during judging | Shows one commit's changes; must repeat for each commit |
| `git_show` | Git (reference) | 2 | commit-contents | added during judging | Shows one commit's changes; must repeat for each commit |
| `git_diff` | Git (cyanheads) | 2 | commit-contents | added during judging | Diffs one commit range at a time; agent must spot the keys |
| `git_diff` | Git (reference) | 2 | commit-contents | added during judging | Diffs one commit range at a time; agent must spot the keys |
| `git_log` | Git (reference) | 1 |  | added during judging | Lists commits without their content |
| `search_code` | GitHub (official) | 1 |  | added during judging | Searches current code, not history |
| `search_text` | Filesystem (j0hanz) | 1 |  | added during judging | Searches current files, not history |
| `image_inspect` | Docker (L337-org) | 0 |  | bm25 #1 | Docker image details |
| `buildx_history_list` | Docker (L337-org) | 0 |  | bm25 #2 | Docker build history |
| `pg_seq_scan_tables` | Postgres (YawLabs) | 0 |  | bm25 #3 | Database scan stats |
| `http_options` | Fetch (YawLabs) | 0 |  | bm25 #4 | HTTP request |
| `image_history` | Docker (L337-org) | 0 |  | bm25 #5 | Docker image layers |
| `browser_navigate_back` | Playwright (Microsoft) | 0 |  | bm25 #6 | Browser back button |
| `registry_image_config` | Docker (L337-org) | 0 |  | bm25 #7 | Docker image settings |
| `buildx_history_inspect` | Docker (L337-org) | 0 |  | bm25 #8 | Docker build record |
| `hub_tags` | Docker (L337-org) | 0 |  | bm25 #9 | Docker Hub tags |
| `system_logout` | Docker (L337-org) | 0 |  | bm25 #10 | Clears a Docker login |

## 4. Look up the Terraform getting-started docs

**Narrative.** The user wants to read HashiCorp's getting-started guide for Terraform. No URL is given, and this starter collection has no docs-lookup or web search tool, so no tool does this directly. Fetch tools and browsers can load the guide once the agent knows or finds its address. Docker's own documentation tool and tools unrelated to the web do not help.

BM25's top 10 contained 0 of the 5 relevant tools (grade 2 or 3) we found.

| Tool | Server | Grade | Group | Source | Why |
|---|---|---|---|---|---|
| `fetch` | Fetch (reference) | 2 | fetch-web-page | added during judging | Loads the guide if the agent knows its URL |
| `fetch_reader` | Fetch (YawLabs) | 2 | fetch-web-page | added during judging | Loads the guide if the agent knows its URL |
| `fetch_html_to_markdown` | Fetch (YawLabs) | 2 | fetch-web-page | added during judging | Loads the guide if the agent knows its URL |
| `browser_navigate` | Playwright (Microsoft) | 2 | open-page | added during judging | Can open the guide or a search engine, then read it |
| `navigate_page` | Chrome DevTools (Google) | 2 | open-page | added during judging | Can open the guide or a search engine, then read it |
| `docs_lookup` | Docker (L337-org) | 1 |  | bm25 #1 | Looks up Docker docs, not Terraform |
| `search_repositories` | GitHub (official) | 1 |  | added during judging | Finds Terraform's GitHub repo, not the guide |
| `http_head` | Fetch (YawLabs) | 0 |  | bm25 #2 | Checks a URL exists; returns no content |
| `compose_up` | Docker (L337-org) | 0 |  | bm25 #3 | Starts Docker Compose services |
| `assign_copilot_to_issue` | GitHub (official) | 0 |  | bm25 #4 | Assigns Copilot to an issue |
| `compose_port` | Docker (L337-org) | 0 |  | bm25 #5 | Docker Compose ports |
| `container_run` | Docker (L337-org) | 0 |  | bm25 #6 | Runs a container |
| `container_restart` | Docker (L337-org) | 0 |  | bm25 #7 | Restarts a container |
| `git_init` | Git (cyanheads) | 0 |  | bm25 #8 | Starts a new Git repository |
| `list_commits` | GitHub (official) | 0 |  | bm25 #9 | Lists commits |
| `pg_seq_scan_tables` | Postgres (YawLabs) | 0 |  | bm25 #10 | Database scan stats |

## 5. Fetch the pricing page at this URL and give me the prices as a table

**Narrative.** The user gives the URL of a pricing page and wants the prices pulled out and shown as a table. A tool that downloads the page and returns its readable content does the work; the agent then builds the table. A browser can do it in two steps: open the page, then read it. Tools that return only the page's title, links or crawler rules cannot get the prices.

BM25's top 10 contained 5 of the 10 relevant tools (grade 2 or 3) we found.

| Tool | Server | Grade | Group | Source | Why |
|---|---|---|---|---|---|
| `fetch` | Fetch (reference) | 3 | fetch-web-page | bm25 #3 | Returns the page as markdown |
| `fetch_html_to_markdown` | Fetch (YawLabs) | 3 | fetch-web-page | added during judging | Returns the page as markdown |
| `fetch_html_to_text` | Fetch (YawLabs) | 3 | fetch-web-page | bm25 #6 | Returns the page as plain text |
| `fetch_reader` | Fetch (YawLabs) | 3 | fetch-web-page | bm25 #10 | Returns the page's main content |
| `http_get` | Fetch (YawLabs) | 2 | fetch-web-page | added during judging | Returns raw HTML; agent must pick out the prices |
| `navigate_page` | Chrome DevTools (Google) | 2 | open-page | bm25 #1 | Opens the page; reading it is a second step |
| `new_page` | Chrome DevTools (Google) | 2 | open-page | bm25 #2 | Opens the page; reading it is a second step |
| `browser_navigate` | Playwright (Microsoft) | 2 | open-page | added during judging | Opens the page; reading it is a second step |
| `browser_snapshot` | Playwright (Microsoft) | 2 | page-snapshot | added during judging | Reads the open page's text |
| `take_snapshot` | Chrome DevTools (Google) | 2 | page-snapshot | added during judging | Reads the open page's text |
| `fetch_meta` | Fetch (YawLabs) | 1 |  | bm25 #9 | Gets the title and description, not prices |
| `fetch_robots` | Fetch (YawLabs) | 0 |  | bm25 #5 | Reads robots.txt |
| `fetch_sitemap` | Fetch (YawLabs) | 0 |  | bm25 #7 | Reads a sitemap |
| `git_remote` | Git (reference) | 0 |  | bm25 #4 | Git remote URLs |
| `pg_table_privileges` | Postgres (YawLabs) | 0 |  | bm25 #8 | Database permissions |

## 6. Run my test suite in an isolated container and show any failures

**Narrative.** The user wants their tests to run in a fresh, throwaway container so their machine is not affected, and wants to see which tests failed. Steps: start a new container with the test command, then read its output. Running a command in a container that is already running, or reading logs, covers part of the job. Listing containers, installing plugins or diffing files does not help.

BM25's top 10 contained 4 of the 7 relevant tools (grade 2 or 3) we found.

| Tool | Server | Grade | Group | Source | Why |
|---|---|---|---|---|---|
| `container_run` | Docker (L337-org) | 3 | run-new-container | bm25 #7 | Runs a new container and can wait for the result |
| `compose_run` | Docker (L337-org) | 2 | run-new-container | bm25 #8 | Works only with a Compose file; output fetched separately |
| `container_exec` | Docker (L337-org) | 2 | run-in-running-container | bm25 #4 | Runs a command, but needs a running container |
| `exec_command` | Docker (ofershap) | 2 | run-in-running-container | added during judging | Runs a command, but needs a running container |
| `container_logs` | Docker (L337-org) | 2 | container-output | added during judging | Shows the test output after a detached run |
| `container_logs` | Docker (ofershap) | 2 | container-output | added during judging | Shows the test output after a detached run |
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
| `search_files` | Filesystem (reference) | 3 | find-by-name | added during judging | Finds files by name pattern |
| `find_files` | Filesystem (j0hanz) | 3 | find-by-name | bm25 #6 | Finds files by name pattern |
| `create_directory` | Filesystem (reference) | 3 | make-folder | added during judging | Creates the new folder |
| `create` | Filesystem (j0hanz) | 3 | make-folder | bm25 #8 | Creates folders (and files) |
| `move_file` | Filesystem (reference) | 3 | move-file | bm25 #1 | Moves a file |
| `move` | Filesystem (j0hanz) | 3 | move-file | bm25 #7 | Moves files; creates missing folders too |
| `list_directory` | Filesystem (reference) | 2 | browse-folder | added during judging | Can find the files by browsing, with extra steps |
| `list` | Filesystem (j0hanz) | 2 | browse-folder | bm25 #2 | Can find the files by browsing, with extra steps |
| `search_text` | Filesystem (j0hanz) | 1 |  | bm25 #10 | Searches inside files, not names |
| `stat` | Filesystem (j0hanz) | 1 |  | bm25 #5 | Checks a path exists; cannot find or move |
| `delete` | Filesystem (j0hanz) | 0 |  | bm25 #3 | Deletes files |
| `git_worktree` | Git (cyanheads) | 0 |  | bm25 #4 | Git working trees |
| `git_checkout` | Git (cyanheads) | 0 |  | bm25 #9 | Switches Git branches |

## 8. Create a new branch, commit my changes, and open a pull request

**Narrative.** The user has local changes and wants them on a new branch, committed, and proposed as a pull request on GitHub. Steps: create and switch to a new branch, stage and commit the changes, push the branch, then open the pull request. A tool that fully does one of these steps is relevant. The reference Git server cannot push, so it covers only the local steps. Tools for reviewing, commenting on or updating existing pull requests do not help.

BM25's top 10 contained 6 of the 12 relevant tools (grade 2 or 3) we found.

| Tool | Server | Grade | Group | Source | Why |
|---|---|---|---|---|---|
| `git_create_branch` | Git (reference) | 3 | create-branch | bm25 #2 | Creates the new branch |
| `git_checkout` | Git (cyanheads) | 3 | create-branch | bm25 #9 | Creates and switches to the new branch |
| `git_branch` | Git (cyanheads) | 3 | create-branch | bm25 #8 | Creates the new branch |
| `git_checkout` | Git (reference) | 3 | switch-branch | added during judging | Switches to the new branch |
| `git_add` | Git (reference) | 3 | stage-changes | added during judging | Stages the changes |
| `git_add` | Git (cyanheads) | 3 | stage-changes | added during judging | Stages the changes |
| `git_commit` | Git (reference) | 3 | commit | added during judging | Commits the staged changes |
| `git_commit` | Git (cyanheads) | 3 | commit | bm25 #10 | Commits, and can stage files too |
| `git_push` | Git (cyanheads) | 3 | push-branch | added during judging | Pushes the branch to GitHub |
| `create_pull_request` | GitHub (official) | 3 | open-pr | bm25 #3 | Opens the pull request |
| `create_branch` | GitHub (official) | 2 | create-branch | bm25 #7 | Creates the branch on GitHub only, not locally |
| `push_files` | GitHub (official) | 2 | push-branch | added during judging | Commits files on GitHub directly; agent must send their content |
| `update_pull_request_branch` | GitHub (official) | 1 |  | bm25 #1 | Updates an existing pull request |
| `git_pull` | Git (cyanheads) | 0 |  | bm25 #5 | Pulls in others' changes |
| `add_reply_to_pull_request_comment` | GitHub (official) | 0 |  | bm25 #4 | Replies to a comment |
| `pull_request_review_write` | GitHub (official) | 0 |  | bm25 #6 | Reviews a pull request |

## 9. List the open issues on this repo that I’m tagged in

**Narrative.** The user wants the open issues in their GitHub repository where they are @-mentioned or assigned. The GitHub server's issue search passes GitHub's search filters through, so one call with is:open and mentions: (or assignee:) can do it. Listing open issues and filtering them by hand also works, with extra steps. Looking up the user's login helps fill in the filter. Browser and Docker tools do not help.

BM25's top 10 contained 2 of the 3 relevant tools (grade 2 or 3) we found.

| Tool | Server | Grade | Group | Source | Why |
|---|---|---|---|---|---|
| `search_issues` | GitHub (official) | 3 | find-issues | bm25 #3 | Accepts GitHub search filters like mentions: (per the server's code) |
| `list_issues` | GitHub (official) | 2 | find-issues | bm25 #1 | Lists open issues; agent must filter by mention |
| `get_me` | GitHub (official) | 2 | who-am-i | added during judging | Finds the user's login to filter on |
| `issue_read` | GitHub (official) | 1 |  | added during judging | Reads one issue at a time |
| `search_pull_requests` | GitHub (official) | 1 |  | bm25 #6 | Searches pull requests, not issues |
| `new_page` | Chrome DevTools (Google) | 1 |  | bm25 #7 | Could open GitHub's issue search; needs a login |
| `list_issue_types` | GitHub (official) | 0 |  | bm25 #5 | Issue types |
| `list_issue_fields` | GitHub (official) | 0 |  | bm25 #9 | Custom issue fields |
| `list_pages` | Chrome DevTools (Google) | 0 |  | bm25 #2 | Lists browser tabs |
| `close_page` | Chrome DevTools (Google) | 0 |  | bm25 #4 | Closes a tab |
| `performance_start_trace` | Chrome DevTools (Google) | 0 |  | bm25 #8 | Performance trace |
| `image_list` | Docker (L337-org) | 0 |  | bm25 #10 | Lists Docker images |

## 10. Open this repo’s issues page in a browser and take a screenshot

**Narrative.** The user wants a picture of their GitHub repository's issues page as it looks in a browser. Steps: open the page in a browser, then save a screenshot. A tool that fully does either step is relevant. Text snapshots of the page are not pictures, and listing issues through the GitHub API skips the browser.

BM25's top 10 contained 3 of the 5 relevant tools (grade 2 or 3) we found.

| Tool | Server | Grade | Group | Source | Why |
|---|---|---|---|---|---|
| `browser_navigate` | Playwright (Microsoft) | 3 | open-page | added during judging | Opens the issues page |
| `navigate_page` | Chrome DevTools (Google) | 3 | open-page | added during judging | Opens the issues page |
| `new_page` | Chrome DevTools (Google) | 3 | open-page | bm25 #8 | Opens the issues page in a new tab |
| `browser_take_screenshot` | Playwright (Microsoft) | 3 | screenshot | bm25 #1 | Takes the screenshot |
| `take_screenshot` | Chrome DevTools (Google) | 3 | screenshot | bm25 #2 | Takes the screenshot |
| `browser_snapshot` | Playwright (Microsoft) | 1 |  | bm25 #4 | Text snapshot, not a picture |
| `take_snapshot` | Chrome DevTools (Google) | 1 |  | bm25 #3 | Text snapshot, not a picture |
| `list_issues` | GitHub (official) | 1 |  | bm25 #5 | Lists the issues, but no browser or picture |
| `list_pages` | Chrome DevTools (Google) | 1 |  | bm25 #7 | Lists open tabs |
| `take_heapsnapshot` | Chrome DevTools (Google) | 0 |  | bm25 #10 | Memory snapshot |
| `close_page` | Chrome DevTools (Google) | 0 |  | bm25 #6 | Closes a tab |
| `performance_start_trace` | Chrome DevTools (Google) | 0 |  | bm25 #9 | Performance trace |

## 11. Fill out the signup form on this page with test data and submit it

**Narrative.** The user has a signup page open and wants an agent to fill every field with made-up test data and submit the form. Steps: fill in the fields, then submit. A tool that fills many fields at once, or clicks the submit button, fully does a step. Typing into one field at a time works with extra calls, and the agent first needs to read the page to find the fields.

BM25's top 10 contained 4 of the 13 relevant tools (grade 2 or 3) we found.

| Tool | Server | Grade | Group | Source | Why |
|---|---|---|---|---|---|
| `fill_form` | Chrome DevTools (Google) | 3 | fill-form | bm25 #1 | Fills many fields at once |
| `browser_fill_form` | Playwright (Microsoft) | 3 | fill-form | bm25 #2 | Fills many fields at once |
| `browser_click` | Playwright (Microsoft) | 3 | click | added during judging | Clicks the submit button |
| `click` | Chrome DevTools (Google) | 3 | click | added during judging | Clicks the submit button |
| `fill` | Chrome DevTools (Google) | 2 | fill-field | bm25 #6 | Fills one field per call |
| `browser_type` | Playwright (Microsoft) | 2 | fill-field | added during judging | Types into one field per call |
| `type_text` | Chrome DevTools (Google) | 2 | fill-field | added during judging | Types into the focused field |
| `browser_press_key` | Playwright (Microsoft) | 2 | press-key | added during judging | Can submit by pressing Enter |
| `press_key` | Chrome DevTools (Google) | 2 | press-key | bm25 #7 | Can submit by pressing Enter |
| `browser_snapshot` | Playwright (Microsoft) | 2 | page-snapshot | added during judging | Finds the form fields first |
| `take_snapshot` | Chrome DevTools (Google) | 2 | page-snapshot | added during judging | Finds the form fields first |
| `browser_navigate` | Playwright (Microsoft) | 2 | open-page | added during judging | Needed only if the page is not open yet |
| `navigate_page` | Chrome DevTools (Google) | 2 | open-page | added during judging | Needed only if the page is not open yet |
| `browser_drop` | Playwright (Microsoft) | 0 |  | bm25 #4 | Drops files onto the page |
| `container_exec` | Docker (L337-org) | 0 |  | bm25 #3 | Runs a command in a container |
| `pull_request_review_write` | GitHub (official) | 0 |  | bm25 #5 | Submits a code review |
| `set_logpoints` | Chrome DevTools (Google) | 0 |  | bm25 #8 | Console logging |
| `fetch_links` | Fetch (YawLabs) | 0 |  | bm25 #9 | Lists a page's links |
| `image_import` | Docker (L337-org) | 0 |  | bm25 #10 | Imports a Docker image |

## 12. Add the “bug” label to issue 42 and assign it to me

**Narrative.** The user is triaging issue 42 in their GitHub repository and wants it labeled "bug" and assigned to themselves. A tool that updates an issue's labels and assignees does it in one call. Looking up the user's own login helps fill in "me". Commenting, reading, or assigning someone else does not do the job.

BM25's top 10 contained 1 of the 2 relevant tools (grade 2 or 3) we found.

| Tool | Server | Grade | Group | Source | Why |
|---|---|---|---|---|---|
| `issue_write` | GitHub (official) | 3 | update-issue | bm25 #7 | Updates labels and assignees in one call |
| `get_me` | GitHub (official) | 2 | who-am-i | added during judging | Finds the user's login to assign |
| `assign_copilot_to_issue` | GitHub (official) | 1 |  | bm25 #1 | Assigns Copilot, not the user |
| `issue_read` | GitHub (official) | 1 |  | bm25 #6 | Reads the issue; cannot change it |
| `get_label` | GitHub (official) | 1 |  | bm25 #10 | Checks the label exists; cannot apply it |
| `ui_get` | GitHub (official) | 1 |  | bm25 #8 | Lists labels and assignees; cannot apply them |
| `add_issue_comment` | GitHub (official) | 0 |  | bm25 #2 | Adds a comment, not a label |
| `update_issue_comment` | GitHub (official) | 0 |  | bm25 #9 | Edits a comment |
| `sub_issue_write` | GitHub (official) | 0 |  | bm25 #3 | Links sub-issues |
| `list_issue_types` | GitHub (official) | 0 |  | bm25 #5 | Issue types are not labels |
| `network_connect` | Docker (L337-org) | 0 |  | bm25 #4 | Docker networking |

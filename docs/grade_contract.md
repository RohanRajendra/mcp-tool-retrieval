# Sample Data and Grade Contract

**Our task.** AI agents can connect to many MCP (Model Context Protocol) servers at once, and each server offers tools such as "read a file" or "open a pull request". Different vendors offer near-identical tools with different names and descriptions, and putting every tool into the agent's prompt is costly and makes the right tool harder to pick. Our task: given a developer's request in plain English, rank tools pooled from many real MCP servers, where equivalent tools from different vendors are equally relevant.

## 1. Sample queries and relevance judgments

### How these were made

- **Tools.** 384 tools from 13 MCP servers in 7 categories: filesystem, Git, GitHub, Postgres, containers, browser, and web fetch. We collected them on November 13, 2026 (US Eastern time) by asking each running server for its tool list. Each server ran in a throwaway container, and every server version is pinned.
- **Queries.** We wrote 12 sample queries before reading any tool descriptions. Ten are shown below.
- **Which tools were judged.** For each query: the top 10 tools from BM25, a standard keyword-matching ranker, run over tool names and descriptions, plus tools the judge added after scanning the names of all 384 tools for ones the search missed.
- **Judge.** An LLM (Claude Opus 5.5) drafted the grades using the scale below. A human check is part of milestone B.
- **Early observation.** For these 10 queries, BM25's top 10 contained 36 of the 69 relevant tools (grade 2 or 3) that we know of.
- **Full data**, including every tool judged not relevant: https://github.com/RohanRajendra/mcp-tool-retrieval/blob/dev/data/sample_judgments_q1-12.jsonl

### Relevance scale

- **3**: does the request, or one required step of a multi-step request, by itself.
- **2**: does it partly, only with extra steps, or looks up something a step needs (such as the user's login).
- **1**: related, but cannot do the request.
- **0**: not relevant.

Each tool gets the highest grade that fits. Server labels ending in **-ref** are the official reference servers; the other labels name the vendor or product.

### Examples

### 1. List all tables in my local Postgres database

**Narrative.** The user wants the names of the tables in their local Postgres database. A tool that lists tables is fully relevant. A tool that runs any SQL query also works, but the agent must write the query first. Tools that list schemas or roles, or show performance stats, do not answer it.

- **3:** `list_tables` (PG-antonorlov); `pg_list_tables` (PG-YawLabs).
- **2:** `pg_query`, `pg_readonly` (PG-YawLabs); `query` (PG-antonorlov). Each needs a hand-written SQL query.
- **1:** `list_schemas` (PG-antonorlov); `pg_list_schemas` (PG-YawLabs). They list schemas, not tables.
- **0, for example:** `pg_kill` (PG-YawLabs) cancels running queries, and `pg_top_queries` (PG-YawLabs) shows query performance stats. BM25 ranked them 5th and 6th.

### 2. Show me the commits made on this repo yesterday

**Narrative.** The user wants a list of yesterday's commits in the repository they are working on, a local copy that is also on GitHub. Relevant tools list commit history and can filter it by date. Tools that show one commit, compare versions, or change history are not what was asked for.

- **3:** `git_log` (Git-ref); `git_log` (Git-cyanheads); `list_commits` (GitHub).
- **2:** `search_commits` (GitHub). Searches by date, but only the default branch.
- **1:** `git_show`, `git_diff` (Git-cyanheads); `git_diff` (Git-ref). They show one commit or a difference between versions, not a list of commits.
- **0, for example:** `container_diff` (Docker-L337) lists file changes in a Docker container, and `image_list` (Docker-L337) lists Docker images. BM25 ranked them 1st and 2nd.

### 3. Fetch the pricing page at this URL and give me the prices as a table

**Narrative.** The user gives a page address and wants the prices on that page. A tool that downloads the page and returns its readable text is fully relevant; the agent then builds the table. A browser can do it in two steps. Tools that return only the page's title, links, or crawler rules cannot get the prices.

- **3:** `fetch` (Fetch-ref); `fetch_html_to_markdown`, `fetch_html_to_text`, `fetch_reader` (Fetch-YawLabs).
- **2:** `http_get` (Fetch-YawLabs); `navigate_page`, `new_page`, `take_snapshot` (ChromeDevTools); `browser_navigate`, `browser_snapshot` (Playwright). Raw HTML, or two steps: open the page, then read it.
- **1:** `fetch_meta` (Fetch-YawLabs). Gets only the page's title and description.
- **0, for example:** `git_remote` (Git-ref) lists a Git repository's remote URLs, and `fetch_robots` (Fetch-YawLabs) reads a site's robots.txt. BM25 ranked them 4th and 5th.

### 4. Run my test suite in an isolated container and show any failures

**Narrative.** The user wants their tests run in a fresh, throwaway container and wants to see which tests failed. A tool that starts a new container with the test command and returns its output is fully relevant. Running the tests in a container that is already running, or only reading a container's output, covers part of the job. Tools that only list containers or install plugins do not help.

- **3:** `container_run` (Docker-L337).
- **2:** `compose_run`, `container_exec`, `container_logs`, `compose_logs` (Docker-L337); `exec_command`, `container_logs` (Docker-ofershap). Each covers part of the job, or needs a running container or a Compose file.
- **1:** `container_start` (Docker-L337). Starts an existing container; cannot create one.
- **0, for example:** `container_list` (Docker-L337) lists containers, and `plugin_install` (Docker-L337) installs a Docker plugin. BM25 ranked them 1st and 2nd.

### 5. Find the spending report files and move them to a new folder called expenditure

**Narrative.** The user wants three things done: find the files by name, create the folder, and move the files into it. A tool that fully does any one of these steps is fully relevant. Browsing folders to find the files also works, with extra effort. Tools that delete files or work with Git do not help.

- **3:** `search_files`, `create_directory`, `move_file` (FS-ref); `find_files`, `create`, `move` (FS-j0hanz).
- **2:** `list_directory` (FS-ref); `list` (FS-j0hanz). Can find the files by browsing, with extra work.
- **1:** `search_text`, `stat` (FS-j0hanz). Searches inside files, or only checks that a path exists.
- **0, for example:** `delete` (FS-j0hanz) deletes files, and `git_worktree` (Git-cyanheads) manages Git working trees. BM25 ranked them 3rd and 4th.

### 6. Create a new branch, commit my changes, and open a pull request

**Narrative.** The user wants their local changes put on a new branch, committed, pushed to GitHub, and proposed as a pull request. A tool that fully does any one of these steps is fully relevant. Tools that review, comment on, or update an existing pull request do not help.

- **3:** `git_create_branch`, `git_checkout`, `git_add`, `git_commit` (Git-ref); `git_checkout`, `git_branch`, `git_add`, `git_commit`, `git_push` (Git-cyanheads); `create_pull_request` (GitHub). Git-ref cannot push, so it covers only the local steps.
- **2:** `create_branch`, `push_files` (GitHub). GitHub-only shortcuts that need extra steps.
- **1:** `update_pull_request_branch` (GitHub). Updates an existing pull request.
- **0, for example:** `add_reply_to_pull_request_comment` (GitHub) replies to a pull request comment, and `git_pull` (Git-cyanheads) pulls in others' changes. BM25 ranked them 4th and 5th.

### 7. List the open issues on this repo that I’m tagged in

**Narrative.** The user wants the open GitHub issues in their repository where they are @-mentioned or assigned. A search that can filter by state and by mention or assignee does it in one call. Listing all open issues and checking them by hand also works, with extra steps. Tools that manage browser tabs or Docker do not help.

- **3:** `search_issues` (GitHub). Accepts GitHub search filters such as `is:open` and `mentions:` (checked in the server's code).
- **2:** `list_issues`, `get_me` (GitHub). List open issues and filter by hand, or look up the user's login.
- **1:** `issue_read`, `search_pull_requests` (GitHub); `new_page` (ChromeDevTools). Reads one issue at a time, searches pull requests, or opens a browser that needs a login.
- **0, for example:** `list_pages` (ChromeDevTools) lists browser tabs, and `close_page` (ChromeDevTools) closes a browser tab. BM25 ranked them 2nd and 4th.

### 8. Open this repo’s issues page in a browser and take a screenshot

**Narrative.** The user wants a picture of their repository's issues page as it looks in a browser. Opening the page and taking the screenshot are each fully relevant steps. A text snapshot of a page is not a picture, and listing issues through the GitHub API skips the browser.

- **3:** `browser_navigate`, `browser_take_screenshot` (Playwright); `navigate_page`, `new_page`, `take_screenshot` (ChromeDevTools).
- **2:** none.
- **1:** `browser_snapshot` (Playwright); `take_snapshot`, `list_pages` (ChromeDevTools); `list_issues` (GitHub). A text snapshot, a list of tabs, or no browser.
- **0, for example:** `close_page` (ChromeDevTools) closes a browser tab, and `performance_start_trace` (ChromeDevTools) records page performance. BM25 ranked them 6th and 9th.

### 9. Fill out the signup form on this page with test data and submit it

**Narrative.** The user wants every field of the signup form on a given page filled with made-up data, then the form submitted. Filling many fields at once and clicking the submit button are each fully relevant steps. Typing one field at a time, or first opening the page and reading its fields, helps but takes extra calls. Tools that run commands in containers or drop files onto the page do not help.

- **3:** `fill_form`, `click` (ChromeDevTools); `browser_fill_form`, `browser_click` (Playwright).
- **2:** `fill`, `type_text`, `press_key`, `take_snapshot`, `navigate_page` (ChromeDevTools); `browser_type`, `browser_press_key`, `browser_snapshot`, `browser_navigate` (Playwright). One field per call, Enter to submit, or a helper step (open the page or read its fields).
- **1:** none.
- **0, for example:** `container_exec` (Docker-L337) runs a command in a container, and `browser_drop` (Playwright) drops files onto a page. BM25 ranked them 3rd and 4th.

### 10. Add the “bug” label to issue 42 and assign it to me

**Narrative.** The user wants one GitHub issue labeled "bug" and assigned to themselves. A tool that updates an issue's labels and assignees is fully relevant. Looking up the user's own login helps. Commenting on the issue or assigning someone else does not do the job.

- **3:** `issue_write` (GitHub).
- **2:** `get_me` (GitHub). Looks up the user's login, but changes nothing.
- **1:** `assign_copilot_to_issue`, `issue_read`, `get_label`, `ui_get` (GitHub). Reads the issue or its labels, or assigns Copilot instead of the user.
- **0, for example:** `add_issue_comment` (GitHub) adds a comment, not a label, and `sub_issue_write` (GitHub) links sub-issues. BM25 ranked them 2nd and 3rd.
## 2. Grade contract

Each milestone is work we will do, not a score we promise to reach. Each grade includes everything required for the grades below it.

### B

1. **Collection.** Add one docs or web-search server (for example, Context7) and GitHub's secret-scanning tools to the current 384 tools, then freeze the collection before judging starts. Every server version is pinned and its collection date recorded.
2. **Queries.** 40 queries: the 12 sample queries plus 28 new ones written from real developer tasks, without copying wording from tool descriptions. Each has a narrative that says what the user wants and what makes a tool relevant or not.
3. **Candidates.** For each query, the top 10 tools from BM25 and the top 10 from one off-the-shelf dense retriever (a model that matches by meaning rather than exact words, named in the report), plus tools the judge adds after scanning the full tool list. Both retrievers index each tool's name, description, and parameter schema (the names and descriptions of its inputs).
4. **Judgments.** An LLM grades every candidate on the 0 to 3 scale. The report names the model and includes the prompt.
5. **Human check.** We hand-grade 50 query-tool pairs without seeing the LLM's grades, about 12 drawn at random from each of the LLM's four grades. We report weighted Cohen's kappa, a standard measure of how much two judges agree beyond chance (with linear weights, a 3-vs-2 disagreement counts less than a 3-vs-0).
6. **Baseline.** Run BM25 on all 40 queries and score it with nDCG@10 and Recall@10, averaged over queries. nDCG@10 adds up the grades of the first 10 tools, counting lower ranks less, and divides by the best possible total for that query (1 = perfect order). Recall@10 is the share of a query's relevant tools (grade 2 or 3) that appear in the first 10. Before any new system is scored, the LLM grades the unjudged tools in its top 10, and all systems are scored on the same final judgments.

### B+

1. **Hybrid retrieval.** Merge the BM25 and dense rankings with reciprocal rank fusion: each list gives a tool 1/(60 + its rank) points, and the points are added.
2. **Comparison.** Score BM25, dense-only, and hybrid on the same 40 queries with nDCG@10 and Recall@10, and use a paired randomization test (a standard check of whether a difference could be due to chance) for each pair of systems.
3. **Second-judge check.** An LLM from another company re-grades at least 100 query-tool pairs, 25 drawn at random from each grade. We report weighted kappa between the two LLMs.

### A-

1. **Equivalence groups.** Label tools that do the same job as one group, across and within servers, using a written rule that also covers tools that overlap only partly.
2. **Redundancy measure.** Score all three retrieval methods with α-nDCG@10, a version of nDCG that gives less credit for repeating a job already shown. A tool graded 2 or 3 counts toward each of its groups; with α = 0.5, a group's second tool earns half credit and its third a quarter. Also report how many top-10 results repeat a group already shown.

### A

1. **Duplicate-aware reranker.** Rerank the hybrid top 30, moving a tool down when it is very similar to a tool already placed above it. Similarity comes from the tools' names, descriptions, and schemas, never from our labeled groups. Its settings are chosen by 5-fold cross-validation (tuned on four fifths of the queries and scored on the rest, five times over), so it is never tuned on the queries it is scored on.
2. **Evaluation.** Compare the reranker with the hybrid system on α-nDCG@10 (does it cover more distinct jobs?) and nDCG@10 (does it lose relevance?), with the same paired randomization test.
3. **Error analysis.** For at least 10 queries where the reranker changes the top 10, explain why it helped or hurt.

## 3. Barriers

1. **Equivalence is often partial.** For example, `move` from FS-j0hanz can also copy files, so it overlaps two reference tools, `move_file` and `copy_file`. Plan: a written rule for partial overlap (milestone A-).
2. **What the collection holds depends on our choices.** The official reference servers are not listed in the official MCP Registry, our planned source of servers, so we added them by hand. GitHub's server hides some tools by default, such as its secret-scanning tools. There is no docs or web-search server yet, so a request like "look up the Terraform getting-started docs" has no fully relevant tool. Plan: record every server's settings, and add the missing tools before judging (milestone B).
3. **Server sizes are very uneven.** One Docker server has 154 of the 384 tools (40%); the reference fetch server has 1. A few large servers could dominate the results. Plan: report scores by category as well as overall.
4. **Tool descriptions can mislead.** GitHub's `search_issues` says it takes natural language, but its code also passes GitHub search filters such as `mentions:` through. Plan: when a grade depends on behavior the description does not state, check the server's code or run the tool, and note it.

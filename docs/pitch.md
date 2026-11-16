## Retrieval Task

Multi-agent systems often connect to many MCP servers at once, and those servers have a high overlap. Several vendors ship their own filesystem, Git, database, and browser automation servers, with near-identical tools that are named and described differently. Since an agent can’t load every tool into context, it must first retrieve a short list of top candidates that match the query.

The task: given a natural-language request, rank tools pooled from many real MCP servers. Queries may have several correct answers, since equivalent tools from different vendors are equally relevant. Prior work (https://arxiv.org/abs/2503.01763Links) shows strong IR models perform poorly on tool retrieval and uses tools from earlier datasets rather than real MCP servers, where cross-vendor redundancy and inconsistent descriptions are the core difficulty.

### Queries and Results to Annotate

- Collection: ~300 to 500 tools from 6 to 8 developer-toolcategories (filesystem, Git, databases, browser automation,web fetching, containers, code execution, GitHub), 3 to 5servers each, sourced from the official MCP Registry. Eachtool’s name, description, and input schema recorded, withserver versions pinned.
- Queries: ~40 to 50 realistic developer tasks, fromsingle-step (“list all tables in my local Postgres database”)to multi-step. Written before reading tool descriptions toavoid vocabulary overlap.
- Candidates: pooled from the top results of severalretrievers, including an off-the-shelf baseline.
- Relevance scale: 3 = directly accomplishes the request; 2 =partially or with extra steps; 1 = related but insufficient;0 = not relevant.
- Equivalence groups: functionally equivalent tools acrossservers labelled together.
- Consistency check: a sample re-judged later, with agreementreported (weighted Cohen’s kappa).

### System Component

- Hybrid retrieval: BM25 plus dense embeddings over toolname, description, and parameter schema, merged withreciprocal rank fusion. 
- Duplicate-aware reranking: detects equivalent tools acrossservers and reorders results to cover distinct capabilitiesrather than repeat one function. 
- Evaluation: nDCG@10 and Recall@k for retrieval; α-nDCG overthe equivalence groups for the reranker, since standard nDCGdoesn’t penalise redundancy.
- Stretch goals: normalising tool descriptions beforeindexing, and decomposing multi-step queries.

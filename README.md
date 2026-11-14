# LangChain Practice

A collection of hands-on notebooks for learning LangChain and LangGraph. Examples cover models, prompts, tools, memory, multimodal messages, agents, state, context, and MCP integrations.

## Requirements

- Python 3.12 (supported range: `>=3.12,<3.14`)
- [uv](https://docs.astral.sh/uv/)

## Setup

From the project root, install the locked dependencies:

```powershell
uv sync
```

Create a `.env` file in the project root for the API keys needed by the notebooks you plan to run. For example, the wedding-planning example uses Groq, Tavily, and SerpApi:

```dotenv
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
SERPAPI_API_KEY=your_serpapi_api_key
```

Keep real keys private. `.env` is git-ignored; do not commit credentials.

## Run the notebooks

Start JupyterLab from the project root:

```powershell
uv run jupyter lab
```

Open a notebook under `notebooks/module1/` or `notebooks/module2/`, select the project Python environment as its kernel, and run cells from top to bottom. Notebooks that call external model or search APIs require the corresponding API keys in `.env`; provider usage may be subject to rate limits or charges.

## Project layout

```text
notebooks/
  module1/    Model, prompting, tools, memory, and multimodal examples
  module2/    Context, state, MCP, multi-agent, and wedding-planning examples
src/
  langchain_practice/
```

The wedding-planning flow is available as both [a notebook](notebooks/module2/wedding_planning.ipynb) and a Python script ([wedding_planning.py](notebooks/module2/wedding_planning.py)). To run the script from the project root:

```powershell
uv run python notebooks/module2/wedding_planning.py
```

The script makes live model and search calls, so configure its API keys before running it.

# new venv
# --------------------
uv init --bare --python 3.12
uv sync --python 3.12
uv pip install torch


# install requirements
# --------------------
# create a .env file in root directory
cp .env.example .env
# add the following lines to the .env file
# LANGSMITH_API_KEY=your_langsmith_api_key
# LANGSMITH_TRACING=true
# LANGSMITH_PROJECT="interrupt-workshop"
# OPENAI_API_KEY=your_openai_api_key

# or, set env vars in terminal
export LANGSMITH_API_KEY=your_langsmith_api_key
export LANGSMITH_TRACING=true
export OPENAI_API_KEY=your_openai_api_key

# package install
uv sync --extra dev  # install the package with development dependencies
souce .venv/Scripts/activate  # activate the virtual environment


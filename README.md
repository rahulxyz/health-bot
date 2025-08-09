# Health-Bot

Health-Bot is an intelligent agent designed to assist users with health-related queries and tasks. It leverages modern AI frameworks and integrates with external APIs to provide accurate, context-aware responses and recommendations.

## Features

- Natural language understanding for health questions
- Integration with medical knowledge bases
- Contextual memory and self-reflection for improved interactions
- Multi-agent collaboration for complex tasks
- Extensible toolset for custom workflows

## Python Version

This project requires **Python 3.11.13**.

## Folder Structure

- `config.env` – Environment configuration (excluded from version control)
- `__pycache__` – Python bytecode cache (excluded from version control)
- `*.png` – Image assets (excluded from version control)
- Source code and modules for agent logic, memory, tools, and planning

## Getting Started

1. **Clone the repository** and navigate to the `health-bot` folder.
2. **Set up the environment**:
   - Create a virtual environment:  
     ```sh
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - Install dependencies:  
     ```sh
     pip install -r requirements.txt
     ```
   - Configure environment variables in `config.env`.
     ```
     OPENAI_API_KEY=<YOUR_KEY>
     TAVILY_API_KEY=<YOUR_KEY>
     ```

3. **Run the bot**:
   ```sh
   python main.py
   ```

## Usage

Interact with Health-Bot via the command line or integrate it into your application as a module. Customize its behavior by modifying the agent logic and tools.

## License

This project is licensed under the MIT License.

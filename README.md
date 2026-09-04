# InsightAI — Generative AI Data Intelligence Platform

Transform natural-language questions into structured data analysis, SQL queries, visualizations, and actionable business insights.

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

## About the Project

InsightAI is an AI-powered data intelligence platform that leverages Large Language Models (LLMs) to make data exploration more intuitive and accessible. Users can interact with data using natural language and generate structured analyses, SQL queries, visualizations, and business insights.

The platform combines Retrieval-Augmented Generation (RAG), Text-to-SQL, Generative Business Intelligence, and multi-agent validation to support more reliable data-driven decision-making.

### Core Capabilities

**RAG-Based Text-to-SQL** — Uses retrieval and contextual examples to improve natural-language-to-SQL generation.

**Generative Business Intelligence** — Converts data queries into meaningful business insights and analytical outputs.

**Visual Analytics** — Supports data exploration and visualization generation through the Visual Analyzer and BI Wizard.

**Dynamic Few-Shot Prompting** — Incorporates relevant examples to improve LLM response quality for analytical tasks.

**Multi-Agent Validation** — Uses specialized LLM agents to validate generated outputs and support iterative self-correction.

## Architecture

```text
User Query
    │
    ▼
LLM Understanding Layer
    │
    ▼
RAG + Dynamic Few-Shot Retrieval
    │
    ▼
Text-to-SQL Generation
    │
    ▼
Query / Output Validation
    │
    ├───────────────┐
    ▼               ▼
Data Agent    Visual Analyzer
    │               │
    └───────┬───────┘
            ▼
        BI Wizard
            │
            ▼
 Multi-Agent Validation
            │
            ▼
Insights & Visualizations
```

## Tech Stack

- Python
- Streamlit
- OpenAI API / LLMs
- SQLite
- Pandas
- Plotly
- Retrieval-Augmented Generation (RAG)
- Text-to-SQL
- Generative AI
- Multi-Agent Systems

## Getting Started

### Prerequisites

- Python 3.x
- An OpenAI-compatible API key

### Installation

1. Clone the repository:

```sh
git clone https://github.com/Aditya-Kusale/InsightAI.git
```

2. Navigate to the project directory:

```sh
cd InsightAI
```

3. Install dependencies:

```sh
pip install -r requirements.txt
```

4. Provide your API key through Streamlit secrets or the application's sidebar.

5. Run the application:

```sh
streamlit run insight_ai.py
```

## Usage

### Data Agent

1. Enter a natural-language question about the available data.
2. Submit the query.
3. The Data Agent generates an analytical result or dataset relevant to the question.
4. The output can be passed to the Visual Analyzer or BI Wizard for further exploration.

### Visual Analyzer

1. Upload a CSV file when a dataset is not already available from the Data Agent.
2. Explore data quality and structure.
3. Perform data cleaning and discovery.
4. Build visualizations and dashboards.

### BI Wizard

1. Enter a prompt describing the visualization you want to create.
2. Generate the visualization.
3. Review the generated chart together with its textual explanation.

## Roadmap

- [ ] Support additional LLM providers
- [ ] Support additional SQL databases
- [ ] Authentication and authorization
- [ ] Dynamic database connections
- [ ] Persistent dashboard directory
- [ ] Advanced RAG strategies
- [ ] Fine-tuning and evaluation experiments

See the [open issues](https://github.com/Aditya-Kusale/InsightAI/issues) for proposed improvements and known issues.

## Contributing

Contributions, suggestions, and improvements are welcome.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is distributed under the MIT License. See the `LICENSE` file for details.

## Contact

**Aditya Kusale**

- LinkedIn: https://www.linkedin.com/in/aditya-kusale/
- GitHub: https://github.com/Aditya-Kusale

---

### Attribution

The original copyright and license notices contained in the project are preserved in the `LICENSE` file.

[contributors-shield]: https://img.shields.io/github/contributors/Aditya-Kusale/InsightAI.svg?style=for-the-badge
[contributors-url]: https://github.com/Aditya-Kusale/InsightAI/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Aditya-Kusale/InsightAI.svg?style=for-the-badge
[forks-url]: https://github.com/Aditya-Kusale/InsightAI/network/members
[stars-shield]: https://img.shields.io/github/stars/Aditya-Kusale/InsightAI.svg?style=for-the-badge
[stars-url]: https://github.com/Aditya-Kusale/InsightAI/stargazers
[issues-shield]: https://img.shields.io/github/issues/Aditya-Kusale/InsightAI.svg?style=for-the-badge
[issues-url]: https://github.com/Aditya-Kusale/InsightAI/issues
[license-shield]: https://img.shields.io/github/license/Aditya-Kusale/InsightAI.svg?style=for-the-badge
[license-url]: https://github.com/Aditya-Kusale/InsightAI/blob/main/LICENSE
[linkedin-shield]: https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin
[linkedin-url]: https://www.linkedin.com/in/aditya-kusale/

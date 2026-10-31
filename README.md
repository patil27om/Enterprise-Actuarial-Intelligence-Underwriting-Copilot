# 🛡️ Enterprise Actuarial Intelligence & Underwriting Copilot

> An agentic, compliance-audited health insurance underwriting platform powered by **FastAPI**, **LangGraph**, **ChromaDB**, and **GPT-6 Luna**.



### 📖 Overview & Core Philosophy

In traditional insurance workflows, pricing premiums and explaining them to customers is heavily fragmented. Actuaries lean on rigid, generalized risk tables, while customer support agents spend 15 to 20 minutes parsing complex underwriting manuals to justify surcharges to frustrated clients.

This project bridges that gap by building an **Enterprise Underwriting Copilot**. Rather than treating premium calculation as an opaque, black-box AI guess or relying on static CSV files, this platform calculates deterministic statutory premiums under **Title 45 CFR § 147.102 (Affordable Care Act)**, enriches applicant risk profiles via **live public REST APIs**, retrieves regulatory policy clauses from a local zero-cost vector database, and generates audit-ready natural language explanations with automated counterfactual rate-reduction modeling.



### 🌟 Key Features

- **Deterministic Actuarial Math vs. Black-Box Pricing:** Premium rates and risk surcharges (ACA 3:1 age-curves, 45% tobacco loadings, excess BMI metabolic adjustments, dependent tiering) are executed via deterministic code rather than probabilistic LLM hallucinations.
- **Live Public API Ingestion:** Resolves US postal ZIP codes to rating areas dynamically via public municipal geocoding (`Zippopotam.us`) and benchmarks rates against live **CMS Qualified Health Plan (QHP)** open datasets.
- **Event-Driven LangGraph Orchestrator:** Models underwriting as an auditable state graph with typed state contracts and dynamic conditional routing for high-risk profiles.
- **Decoupled Model Context Protocol (MCP) Design:** Modularizes geocoding, market benchmark retrieval, and statutory math into standalone tool interfaces.
- **Zero Infrastructure Cost ($0):** Persists embeddings locally using `sentence-transformers/all-MiniLM-L6-v2` on CPU and local ChromaDB, preserving API tokens exclusively for cost-efficient inference on `gpt-6-luna`.
- **Automated Counterfactual Modeling:** If an applicant incurs risk surcharges, the engine dynamically calculates exact monetary reduction pathways (e.g., 90-day tobacco cessation credit waivers, metabolic wellness targets).



### 🏗️ System Architecture

+---------------------------------------------------------------------------------------------------------+
|                                      Insurance Agent Dashboard                                          |
|                                       (Streamlit / Port 8501)                                           |
+----------------------------------------------------+----------------------------------------------------+
                                                     |
                                        POST /api/v1/quote (JSON)
                                                     |
                                                     v
+---------------------------------------------------------------------------------------------------------+
|                                    FastAPI Gateway (Port 8000)                                          |
|                                                                                                         |
|  [1. Live Public Enrichment Layer (MCP Tools)]                                                          |
|      * Postal Geocoder (Zippopotam.us): Resolves ZIP -> City, State, Geographic Rating Region           |
|      * CMS Open Benchmark Gateway: Fetches State Second-Lowest Cost Silver Plan (SLCSP) Baselines       |
|                                                     |                                                   |
|                      +------------------------------+-------------------------------+                   |
|                      |                                                              |                   |
|                      v                                                              v                   |
|  [2. Actuarial Pricing Engine]                            [3. Local Regulatory Vector Store]            |
|      * ACA 3:1 Monotonic Age Curve                            * Grounding: Title 45 CFR § 147.102       |
|      * 45% Statutory Tobacco Load                             * Embeddings: all-MiniLM-L6-v2 ($0 CPU)   |
|      * Metabolic BMI & Vitals Load                            * ChromaDB Persistent Local Storage       |
|                      |                                                              |                   |
|                      +------------------------------+-------------------------------+                   |
|                                                     |                                                   |
|                                                     v                                                   |
|  [4. LangGraph Multi-Node State Machine]                                                                |
|      * Workflow: [Enrich] -> [Price] -> <Conditional: Has Surcharges?> -> [Counterfactual]             |
|                                                \                                 /                      |
|                                                 +-----> [Retrieve] -> [Synthesize]                      |
|      * LLM: gpt-6-luna (Low reasoning effort, structured audit synthesis)                               |
+---------------------------------------------------------------------------------------------------------+



### 📂 Repository Structure

insurance-actuarial-agent/
├── docker-compose.yml               # Multi-container orchestration (API + UI)
├── Dockerfile                       # Multi-stage container build (CPU-optimized PyTorch)
├── entrypoint.sh                    # Container startup script (auto-seeds ChromaDB)
├── pytest.ini                       # Test runner configuration
├── requirements.txt                 # Application dependencies
│
├── data/
│   └── underwriting_policies/       # Statutory regulatory manuals
│       ├── aca_tobacco_rating.md    # Title 45 CFR § 147.102 surcharge rules
│       ├── cms_age_curves.md        # Standard 3:1 age rating curves
│       ├── metabolic_risk_tiers.md  # Clinical BMI & hypertension schedules
│       └── family_dependents.md     # Child dependent allowances
│
├── artifacts/
│   └── chroma_db/                   # Local persistent ChromaDB vector store
│
├── scripts/
│   ├── seed_vectorstore.py          # Vector store ingestion runner
│   ├── test_graph_run.py            # CLI test runner for LangGraph
│   └── test_mcp_tools.py            # Direct MCP tool validation script
│
├── app/
│   ├── main.py                      # FastAPI app entry point & CORS configuration
│   ├── config.py                    # Environment settings parser
│   ├── ui.py                        # Streamlit Agent Copilot UI
│   │
│   ├── api/                         # REST API Layer
│   │   ├── routes.py                # Endpoints (/quote, /health)
│   │   └── schemas.py               # Pydantic input/output schemas
│   │
│   ├── mcp_servers/                 # Model Context Protocol (MCP) Tools
│   │   ├── geo_mcp.py               # Live postal resolver
│   │   ├── cms_benchmarks_mcp.py    # CMS benchmark provider
│   │   └── actuarial_calc_mcp.py    # Deterministic ACA calculator
│   │
│   ├── graph/                       # LangGraph Orchestration
│   │   ├── state.py                 # UnderwritingState TypedDict
│   │   ├── nodes.py                 # Graph execution nodes
│   │   └── workflow.py              # Conditional edges & graph compiler
│   │
│   └── core/                        # Core Utilities
│       ├── vectorstore.py           # ChromaDB client & embedding factory
│       └── llm.py                   # GPT-6 Luna client configuration
│
└── tests/                           # Automated Test Suite (11 passing tests)
    ├── test_actuarial_math.py       # Math & statutory curve unit tests
    ├── test_mcp_services.py         # Live geocoding & CMS integration tests
    ├── test_graph_state.py          # LangGraph state & routing tests
    └── test_api_endpoints.py        # FastAPI contract & validation tests



### 🚀 Getting Started

#### 1. Clone & Set Up Local Environment

git clone https://github.com/YOUR_USERNAME/insurance-actuarial-agent.git
cd insurance-actuarial-agent



### 🧪 Automated Testing

The repository includes a complete test suite covering deterministic calculations, MCP integrations, LangGraph routing, and FastAPI schema validation:

pytest -v

All 11 test cases pass in ~1.2s:

tests/test_actuarial_math.py::test_aca_age_factor_boundaries PASSED         [  9%]
tests/test_actuarial_math.py::test_tobacco_surcharge_application PASSED     [ 18%]
tests/test_actuarial_math.py::test_metabolic_bmi_surcharge PASSED           [ 27%]
tests/test_actuarial_math.py::test_dependent_charge_cap PASSED              [ 36%]
tests/test_api_endpoints.py::test_health_check_endpoint PASSED              [ 45%]
tests/test_api_endpoints.py::test_quote_endpoint_validation_error PASSED    [ 54%]
tests/test_graph_state.py::test_conditional_router_identifies_risk PASSED   [ 63%]
tests/test_graph_state.py::test_counterfactual_engine_math PASSED           [ 72%]
tests/test_mcp_services.py::test_resolve_valid_zipcode PASSED               [ 81%]
tests/test_mcp_services.py::test_resolve_invalid_zipcode_fallback PASSED     [ 90%]
tests/test_mcp_services.py::test_cms_benchmark_lookup PASSED                [100%]



### 📡 Sample API Request & Response

#### Request (POST /api/v1/quote)

curl -X POST "http://localhost:8000/api/v1/quote" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 45,
    "gender": "male",
    "bmi": 29.5,
    "bloodpressure": 125,
    "diabetic": "No",
    "children": 2,
    "smoker": "Yes",
    "zipcode": "33101"
  }'

#### Response Payload

{
  "location": {
    "zipcode": "33101",
    "city": "Miami",
    "state": "Florida",
    "state_code": "FL",
    "region": "southeast",
    "status": "resolved"
  },
  "benchmark_rate_monthly": 480.0,
  "pricing": {
    "final_annual_premium": 19982.83,
    "final_monthly_premium": 1665.24,
    "breakdown": {
      "base_annual_premium": 12188.16,
      "age_factor": 2.116,
      "tobacco_surcharge": 5484.67,
      "bmi_surcharge": 810.0,
      "hypertension_surcharge": 0.0,
      "dependents_surcharge": 1500.0,
      "chargeable_children": 2
    }
  },
  "counterfactual_scenarios": {
    "tobacco_cessation": {
      "action": "Enroll in an approved 90-day Tobacco Cessation Program (Title 45 CFR § 147.102)",
      "annual_savings_usd": 5484.67,
      "monthly_savings_usd": 457.06,
      "revised_annual_premium": 14498.16
    },
    "bmi_normalization": {
      "action": "Maintain documented participation in certified wellness program reaching BMI < 25.0",
      "annual_savings_usd": 810.0,
      "monthly_savings_usd": 67.5,
      "revised_annual_premium": 19172.83
    }
  },
  "underwriting_synthesis": "## 1. Executive Underwriting Summary\n\nThe stated quote is **$1,665.24 per month ($19,982.83 annually)**. The calculation reconciles arithmetically..."
}



### ⚖️ License & Disclaimer

Distributed under the **MIT License**. The calculations and regulatory rules simulated in this project reflect statutory frameworks under Title 45 CFR and public CMS dataset benchmarks. It is designed for demonstration and architectural portfolio purposes and does not represent binding insurance underwriting advice.
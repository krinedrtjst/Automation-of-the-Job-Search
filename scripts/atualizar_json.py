import json

dados = {
  "personal": {
    "name": "Karine Duarte Justino",
    "email": "karineduartejustino@proton.me",
    "location": "São Paulo, Brazil",
    "github": "linktr.ee/krine.djt",
    "linkedin": "linkedin.com/in/karinedjustino"
  },
  "languages": [
    {"language": "Portuguese", "level": "Native"},
    {"language": "English", "level": "Full Professional"},
    {"language": "French", "level": "Limited Working"}
  ],
  "skills": {
    "programming": ["Python (Advanced)", "SQL", "PySpark", "NLTK", "PyTorch"],
    "data_ai": ["Prompt Engineering", "AI Red-Teaming", "RLHF", "NLP", "Transformers", "Generative AI", "Chatbots"],
    "bi_cloud": ["Cloud Pipelines", "CI/CD", "ML Governance", "Power BI"]
  },
  "education": [
    {
      "degree": "Bachelor's Degree, Data Science",
      "institution": "UNINTER Centro Universitário Internacional",
      "start_date": "2025-02",
      "end_date": "2027-12"
    },
    {
      "degree": "Postgraduate Specialization, Neuroscience and Applied Psychology",
      "institution": "Universidade Presbiteriana Mackenzie",
      "start_date": "2022-02",
      "end_date": "2023-02"
    },
    {
      "degree": "Bachelor's Degree, Psychology",
      "institution": "Universidade Federal de Mato Grosso",
      "start_date": "2014",
      "end_date": "2021"
    }
  ],
  "experience": [
    {
      "title": "AI Data Specialist & Trust & Safety Evaluator",
      "company": "Spotify (via TaskUs)",
      "start_date": "2026-10",
      "end_date": "Present",
      "bullets": [
        "Engineered complex, edge-case prompt injections to stress-test Generative AI safety guardrails, identifying model vulnerabilities related to culturally nuanced audio requests.",
        "Executed high-volume evaluation of multimedia content, enforcing strict Trust & Safety guidelines to filter policy-violating material."
      ]
    },
    {
      "title": "AI Data Specialist & Trust & Safety Evaluator",
      "company": "Riot Games (via TaskUs)",
      "start_date": "2025-09",
      "end_date": "Present",
      "bullets": [
        "Navigated complex, cross-lingual datasets in C2 English and Native Brazilian Portuguese, evaluating user search intent and linguistic nuances to optimize algorithm accuracy."
      ]
    },
    {
      "title": "Data Analyst for AI Models",
      "company": "RWS Group",
      "start_date": "2024-04",
      "end_date": "2026-09",
      "bullets": [
        "Developed and deployed NLP models using Hugging Face and PyTorch, consistently maintaining production-level accuracy metrics of 99.2%.",
        "Led feature engineering and constructed robust automated ETL pipelines, managing volumes exceeding 15 TB of unstructured multimodal data.",
        "Implemented Fairness algorithms in PyTorch to mitigate bias in LLM training datasets, achieving a 40% reduction."
      ]
    },
    {
      "title": "Prompt Engineering - AI Tutor",
      "company": "Stealth AI Lab",
      "start_date": "2024-09",
      "end_date": "2025-06",
      "bullets": [
        "Iteratively refined complex prompts for LLMs and applied structured RLHF rubrics to validate factual accuracy, coherence, and safety.",
        "Led the curation, cleaning, and management of diverse, gold-standard datasets for fine-tuning generative models."
      ]
    },
    {
      "title": "Epidemiological Data Analyst",
      "company": "Secretaria Municipal de Saúde de Nova Olímpia",
      "start_date": "2020-02",
      "end_date": "2024-08",
      "bullets": [
        "Applied cross-disciplinary clinical expertise and data science to analyze large-scale demographic datasets, informing strategic public health policies.",
        "Managed the end-to-end ETL data lifecycle within SINANWEB, integrating complex datasets to ensure 100% integrity of epidemiological records."
      ]
    }
  ],
  "projects": [
    {
      "name": "Predictive Market Forecasting System",
      "technologies": ["ARIMAX", "XGBoost", "Python"],
      "description": "Built a predictive market forecasting system on 13+ years of data, reducing prediction error by 72.7% to protect portfolios from volatility."
    },
    {
      "name": "Epidemiological Crisis Dashboard",
      "technologies": ["ETL", "VBA", "Excel"],
      "description": "Developed dynamic dashboards for daily public reporting during COVID-19 and automated resource allocation reports to reduce time-to-insight."
    }
  ],
  "certifications": [
    "Microsoft Power BI Desktop for Business Intelligence",
    "Python for Data Science and Machine Learning Bootcamp",
    "Generative AI",
    "Inteligência Artificial Aplicada a Dados"
  ]
}

with open('privado/perfil_mestre.json', 'w', encoding='utf-8') as f:
    json.dump(dados, f, ensure_ascii=False, indent=2)
print("✅ Base de dados JSON atualizada com sucesso!")

# Contributing

Thank you for your interest in contributing to the AI Career Automation Command Center! Pull Requests (PRs), bug reports, and feature ideas are always welcome.

## 🛡️ Privacy First (Critical Rule)

**Never commit or version real personal data.** 
This includes your actual resumes, `profile_truth.md`, generated output files, application trackers, API keys, or `.env` files. 

To protect your privacy, the directories `input/`, `data/`, `outputs/`, and `private/` are strictly ignored by `.gitignore`. 

If you are submitting a PR that requires sample data or fixtures, **only use the fictional personas** located in the `examples/` directory.

## 🧪 Running Tests

Before submitting a Pull Request, please ensure that all unit tests pass locally and that your changes do not break the strict Zero-Hallucination guardrails. 

You can run the test suite using the standard Python `unittest` module:

```bash
python -m unittest discover -s tests -v

```

## 🛠️ Contribution Workflow

1. **Fork** the repository.
2. **Create** a new feature branch (`git checkout -b feature/your-feature-name`).
3. **Commit** your changes clearly (`git commit -m 'Add some feature'`).
4. **Push** to the branch (`git push origin feature/your-feature-name`).
5. **Open** a Pull Request describing your changes, the problem they solve, and confirming tests pass.

## 📝 Code Style & Guidelines

* **Type Hints:** Use standard Python type hinting (via the `typing` module) for all new functions to maintain code robustness.
* **Formatting:** Ensure your code editor does not insert invisible non-breaking spaces (NBSPs). These cause hidden syntax errors in Python.
* **LLM Prompts:** If you are modifying the AI prompts, ensure they continue to enforce the **Zero-Hallucination Policy**. The agents must never be allowed to invent metrics, tools, or experiences that are not present in the master profile.
* **Language:** Keep all code logic, variables, and documentation in English to maintain a standardized open-source codebase. Specific localized prompts (e.g., Brazilian Portuguese resume generation) should be kept within their designated prompt modules.

```

```
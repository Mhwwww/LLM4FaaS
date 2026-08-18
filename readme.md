# LLM4FaaS: No-Code Application Development using LLMs and FaaS

LLM4FaaS is a No-Code application development framework that combines Large Language Models (LLMs) with Function-as-a-Service (FaaS) platforms, enabling non-technical users to build and run customized applications using only natural language.

By leveraging FaaS, LLM4FaaS abstracts infrastructure and deployment complexity while constraining LLM generation to core business logic, avoids boilerplate generation and improves reliability.


## Introduction

LLM4FaaS uses [tinyFaaS](https://github.com/OpenFogStack/tinyFaas) as the default FaaS backend and [GPT-4o](https://platform.openai.com/docs/models/gpt-4o) as the default code-generation model, though both components can be replaced with other platforms or models.

The [automation pipeline](./eva_automation), including structured prompt preparation, code generation, FaaS function preparation and deployment.
The default prompt templates used for generation and evaluation are located in [experiments_default](./experiments_default) folder.

LLM4FaaS is compared with three baselines, including a [non-FaaS version of LLM4FaaS](./experiments_baseline_v2), human-written implementations, and [Open Iterpreter](https://github.com/OpenInterpreter/open-interpreter).
The evaluation considers [consistency](./experiments_repeat), [programming language](./experiments_js), [latency](./eva_automation), and [static code quatlity with pylint and radon](./eva_code_quality).

LLM4FaaS also incorporates [runtime-error-based few-shot learning](./syntactic_error_loop) to improve system accuracy by refining generated code based on execution feedback.


## Research
We introduced the LLM4FaaS concept and use it as a base platform to explore the factors influencing LLM suitability for no-code development in the following publications.

To use LLM4FaaS or our follow-up studies, please cite them as:

### Text
Wang, M., Pfandzelter, T., Schirmer, T., & Bermbach, D. (2025). LLM4FaaS: No-Code Application Development using LLMs and FaaS. arXiv preprint arXiv:2502.14450.

Wang, M., Kapp, A., Schirmer, T., Pfandzelter, T., & Bermbach, D. (2026). Exploring Influence Factors on LLM Suitability for No‐Code Development of End User Applications. Software: Practice and Experience, 56(1), 96-118.


### BibTex

```bibtex
@article{wang2025llm4faas,
  title={LLM4FaaS: No-Code Application Development using LLMs and FaaS},
  author={Wang, Minghe and Pfandzelter, Tobias and Schirmer, Trever and Bermbach, David},
  journal={arXiv preprint arXiv:2502.14450},
  year={2025}
}
```

```bibtex
@article{wang2026exploring,
  title={Exploring Influence Factors on LLM Suitability for No-Code Development of End User Applications},
  author={Wang, Minghe and Kapp, Alexandra and Schirmer, Trever and Pfandzelter, Tobias and Bermbach, David},
  journal={Software: Practice and Experience},
  volume={56},
  number={1},
  pages={96--118},
  year={2026},
  publisher={Wiley Online Library}
}
```
For a full list of publications from our research group, please see [our website](https://www.tu.berlin/en/3s/research/publications).



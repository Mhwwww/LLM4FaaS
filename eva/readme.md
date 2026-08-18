# Raw Data from Questionnaire

1. All replies are stored in [Data Excel File](llm4faas/eva/data.xlsx).
2. Prompt sample for 4 functions are [keyword](llm4faas/eva/keyword-prompt_template.md), [remote-control](llm4faas/eva/remote-control-prompt_template.md).


# Extract Data from Excel and Store to Markdown file
1. run [extract.py](llm4faas/eva/extract.py) for remote-control data and energy data.
2. run [extract-keyword.py](llm4faas/eva/extract-keyword-prompt.py) for keyword data and auto-adapt data.

# Change LLM models and store responses to Python file

## OpenAI API
1. change the OpenAI API key in [line 9](scripts/openai_simple_generator.py)
2. change model, temperature, max_tokens in [model_setting](scripts/model_setting.py).
3. change the prompt directory and output file directory in [line 15 and 16](scripts/openai_simple_generator.py)

## Gemini API
1. run [start_gemini.sh](scripts/start_gemini.sh) to start the Gemini API.

## Ollama
1. change the model in line 6 of [model_setting](scripts/ollama_simple_generate.py).
2. change the function prompt directory in line 13 of [ollama generator](scripts/ollama_simple_generate.py).

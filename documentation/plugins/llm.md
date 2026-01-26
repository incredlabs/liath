# LLM Plugin (llm)

Access language models for text generation.

## Installation

```bash
pip install liath[llm]
```

Set your OpenAI API key:

```bash
export OPENAI_API_KEY=your-api-key
```

## Functions

### plugins.llm.llm_complete(prompt)

Generate a completion for a prompt.

**Parameters:**

- `prompt` (string): The input prompt

**Returns:** JSON with generated text

**Example:**
```lua
local result = plugins.llm.llm_complete("What is 2 + 2?")
-- Returns: {"status": "success", "response": "2 + 2 equals 4."}
```

### plugins.llm.llm_chat(messages)

Send a chat conversation.

**Parameters:**

- `messages` (string): JSON array of message objects with `role` and `content`

**Returns:** JSON with assistant response

**Example:**
```lua
local json = require("cjson")

local messages = {
    {role = "system", content = "You are a helpful assistant."},
    {role = "user", content = "Hello!"}
}

local result = plugins.llm.llm_chat(json.encode(messages))
-- Returns: {"status": "success", "response": "Hello! How can I help you today?"}
```

## Usage Examples

### Simple Question Answering

```lua
local question = "What is the capital of France?"
local result = plugins.llm.llm_complete(question)
local json = require("cjson")
local data = json.decode(result)
return data.response
```

### RAG with Context

```lua
local json = require("cjson")

-- Search for relevant documents
local query = "What is machine learning?"
local query_emb = json.decode(plugins.embed.embed(query)).embedding
local search_results = json.decode(plugins.vdb.vdb_search("kb", query_emb, 3))

-- Build context from results
local context = ""
for _, result in ipairs(search_results.results or {}) do
    local doc = db:get("doc:" .. result.id)
    if doc then
        context = context .. doc .. "\n"
    end
end

-- Generate answer with context
local prompt = string.format([[
Based on the following context, answer the question.

Context:
%s

Question: %s

Answer:]], context, query)

local answer = json.decode(plugins.llm.llm_complete(prompt))
return answer.response
```

### Multi-turn Conversation

```lua
local json = require("cjson")

local conversation = {
    {role = "system", content = "You are a knowledgeable AI assistant."},
    {role = "user", content = "What is Python?"},
    {role = "assistant", content = "Python is a high-level programming language known for its readability."},
    {role = "user", content = "What are its main uses?"}
}

local result = plugins.llm.llm_chat(json.encode(conversation))
local data = json.decode(result)
return data.response
```

### Code Generation

```lua
local json = require("cjson")

local prompt = [[
Write a Python function that calculates the factorial of a number.
Include docstring and type hints.
]]

local result = plugins.llm.llm_complete(prompt)
local data = json.decode(result)
return data.response
```

### Summarization

```lua
local json = require("cjson")

local text = db:get("article:1")
local prompt = string.format([[
Summarize the following text in 2-3 sentences:

%s

Summary:]], text)

local result = plugins.llm.llm_complete(prompt)
local data = json.decode(result)
return data.response
```

## Configuration

### Using OpenAI

Set the API key environment variable:

```bash
export OPENAI_API_KEY=sk-...
```

### Using Local Llama

The plugin supports local Llama models via llama-cpp-python. Configure the model path as needed.

## Best Practices

1. **Clear prompts**: Be specific about what you want
2. **Use system messages**: Set context with system role in chat
3. **Handle errors**: Check response status
4. **Rate limiting**: Be aware of API rate limits
5. **Cost awareness**: Monitor token usage for OpenAI

## Error Handling

```lua
local json = require("cjson")

local result = plugins.llm.llm_complete("prompt")
local data = json.decode(result)

if data.status == "success" then
    return data.response
else
    return "LLM error: " .. (data.message or "Unknown error")
end
```

## Prompt Templates

### Question Answering Template

```lua
local function qa_prompt(context, question)
    return string.format([[
Answer the question based on the context below.
If the answer is not in the context, say "I don't know."

Context:
%s

Question: %s

Answer:]], context, question)
end
```

### Classification Template

```lua
local function classify_prompt(text, categories)
    local cats = table.concat(categories, ", ")
    return string.format([[
Classify the following text into one of these categories: %s

Text: %s

Category:]], cats, text)
end
```

### Extraction Template

```lua
local function extract_prompt(text, fields)
    local field_list = table.concat(fields, ", ")
    return string.format([[
Extract the following information from the text: %s

Text: %s

Return as JSON with the specified fields.]], field_list, text)
end
```

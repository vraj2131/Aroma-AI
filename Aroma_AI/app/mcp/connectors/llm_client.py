from groq import Groq
import os
import json

client = Groq(api_key="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")

def llm_call(system_prompt, user_prompt, role, model, max_tokens, schema, temp=0):
    """Generic LLM call with enforced JSON schema and safe error handling."""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"You are a {role}. {user_prompt}. "
                               f"Ensure JSON strictly matches this schema: {schema}. "
                               f"No extra keys, no deviations."
                }
            ],
            model=model,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            temperature=temp
        )
        raw_output = chat_completion.choices[0].message.content

        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON from model", "raw_output": raw_output}

    except Exception as e:
        return {"error": str(e)}

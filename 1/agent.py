import asyncio
import json
from openai import AsyncOpenAI
import aiomysql

# Local Ollama config
client = AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")  # fake key for local

# Tool function
async def get_documents_by_president(president: str, month: str):
    pool = await aiomysql.create_pool(
        host='localhost', port=3306,
        user='root', password='123456',
        db='reg_data', autocommit=True
    )

    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("""
                SELECT title, publication_date, type
                FROM documents
                WHERE president = %s AND MONTH(publication_date) = %s
                ORDER BY publication_date DESC
                LIMIT 5
            """, (president, month))
            result = await cur.fetchall()
    pool.close()
    await pool.wait_closed()
    print(result)
    return result

# Tool schema (JSON-style)
tool_schema = [{
    "name": "get_documents_by_president",
    "description": "Get recent federal documents by a specific president and month",
    "parameters": {
        "type": "object",
        "properties": {
            "president": {"type": "string", "description": "Full name of the US president"},
            "month": {"type": "string", "description": "Month number, like '01' for January"},
        },
        "required": ["president", "month"]
    }
}]

# Agent loop
async def chat_with_agent(user_input: str):
    # First LLM call: determine if tool is needed
    response = await client.chat.completions.create(
        model="llama3",  # or qwen:1b
        messages=[{"role": "user", "content": user_input}],
        tools=tool_schema,
        tool_choice="auto"
    )

    message = response.choices[0].message

    if message.tool_calls:
        print("Tool was used. Fetching data from MySQL...")
        tool_call = message.tool_calls[0]
        func_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        if func_name == "get_documents_by_president":
            data = await get_documents_by_president(**args)
            print(" Data fetched from DB:", data)
            # Second LLM call: ask to summarize result
            followup = await client.chat.completions.create(
                model="llama3",
                messages=[
                    {"role": "user", "content": user_input},
                    message,
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": json.dumps(data)
                    }
                ]
            )
            print("Final Answer:", followup.choices[0].message.content)
            return followup.choices[0].message.content
        else:
            print("Unknown tool requested.")
    else:
        print("🤖 No tool used. Answer from model only.")
        print("Final Answer:(model-only):", message.content)
        return message.content

# Run
if __name__ == "__main__":
    query = input("Enter your question for the agent: ")
    asyncio.run(chat_with_agent(query))

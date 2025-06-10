import aiohttp
import aiomysql
import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load .env credentials
load_dotenv()

# DB config
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "db": os.getenv("DB_NAME"),
    "port": 3306,
}

# Fetch Federal Register data (e.g., executive documents for last 7 days)
async def fetch_documents(session, date_str):
    url = f"https://www.federalregister.gov/api/v1/documents.json?conditions[publication_date][is]={date_str}&per_page=100"
    async with session.get(url) as response:
        if response.status != 200:
            print(f"Failed to fetch data for {date_str}")
            return []
        data = await response.json()
        return data.get("results", [])


# Insert data into MySQL
async def insert_documents(pool, documents):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            for doc in documents:
                
                try:
                    await cur.execute("""
                        INSERT INTO documents (title, document_number, publication_date, type, president, full_text_url)
                        VALUES (%s, %s, %s, %s, %s, %s) AS new
                        ON DUPLICATE KEY UPDATE
                        title = new.title,
                        publication_date = new.publication_date,
                        type = new.type,
                        president = new.president,
                        full_text_url = new.full_text_url
                    """, (
                        doc.get("title"),
                        doc.get("document_number"),
                        doc.get("publication_date"),
                        doc.get("type"),
                        doc.get("president", "Unknown"),
                        doc.get("html_url")
                    ))
                except Exception as e:
                    print(f" Error inserting doc {doc.get('document_number')}: {e}")
            await conn.commit()


async def main():
    # Setup DB pool and HTTP session
    pool = await aiomysql.create_pool(**DB_CONFIG)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(7):  # Past 7 days
            date_str = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            tasks.append(fetch_documents(session, date_str))

        all_results = await asyncio.gather(*tasks)
        documents = [doc for day_docs in all_results for doc in day_docs]

        print(f"Fetched {len(documents)} documents")

        await insert_documents(pool, documents)

    pool.close()
    await pool.wait_closed()
    print(" Pipeline completed.")

if __name__ == "__main__":
    asyncio.run(main())

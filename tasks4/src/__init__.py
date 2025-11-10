# tasks4/src/__init__.py

import os
from openai import OpenAI
import sys # Added to gracefully exit on API key error

def summarize_task(client: OpenAI, task_description: str) -> str:
    """Sends a task description to the LLM for summarization."""
    # Print the start of the task being summarized
    print(f"\n--- Summarizing: {task_description[:50].strip()}... ---")
    
    # Define the precise instructions for the AI model
    system_prompt = (
        "You are a professional task summarization agent. "
        "Your only job is to take a long, paragraph-length description "
        "of a task and summarize it into a short, concise phrase (5-10 words). "
        "Respond only with the summary, no other text, and no punctuation on the end."
    )
    
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo", # Recommended fast and cost-effective model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task_description}
            ]
        )
        # Extract the content and clean up whitespace
        summary = completion.choices[0].message.content.strip()
        return summary
        
    except Exception as e:
        # Catch common errors like authentication failure
        if "AuthenticationError" in str(e):
            print("ERROR: Authentication failed. Please check your OPENAI_API_KEY.")
            # Exit the program since we can't proceed without the key
            sys.exit(1)
        return f"ERROR: Could not get summary due to an API error: {e}"

def main():
    """Main application loop to summarize multiple tasks."""
    
    # 1. Check for API Key before proceeding
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your terminal (e.g., $env:OPENAI_API_KEY='your_key') before running 'uv run tasks4'.")
        # Since we can't proceed, we exit here
        return

    # Initialize the OpenAI client (automatically uses the environment variable)
    client = OpenAI() 

    # 2. Add at least 2 sample paragraph-length descriptions (Project Requirement)
    task_descriptions = [
        """
        The project requires a full migration of the existing database from MySQL 
        to PostgreSQL, which involves creating new schema scripts, testing data integrity 
        with a mock load, and setting up daily replication checks. This is the top priority 
        and must be completed by the end of next week to avoid service downtime.
        """,
        """
        I need to research three different possible Personal Knowledge Management Systems (PKMS) 
        that offer strong API integrations with Python, specifically focusing on how easily 
        they support creating linked notes and managing task status updates programmatically. 
        The final output should be a comparison matrix in the SUMMARY.md file.
        """
    ]

    # 3. Loop through and summarize all descriptions (Project Requirement)
    for i, description in enumerate(task_descriptions, 1):
        summary = summarize_task(client, description)
        print(f"Task {i} Summary: **{summary}**")
        
    print("\n--- Tasks 4 Experiment Complete ---")

# This ensures the main function runs when you execute 'uv run tasks4'
if __name__ == "__main__":
    main()

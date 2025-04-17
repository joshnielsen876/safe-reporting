import sqlite3
import os
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from azure.identity import ClientSecretCredential
from openai import AzureOpenAI

# Database path (adjust for your Databricks workspace)
DB_PATH = "/Workspace/Users/ag95@cdc.gov/Llama index test/Safe reporting guidelines/articles.db"

# 🔑 Function to Acquire Azure Credentials
def AcquireCredentials():
    credential = ClientSecretCredential(
        tenant_id="9ce70869-60db-44fd-abe8-d2767077fc8f",
        client_id = "0e38bfdf-13a1-4986-850d-c909912f9a26",
        client_secret=dbutils.secrets.get(scope="dbs-scope-NCIPC-OD-AIPILOT" , key="EDAV-NCIPC-OD-AIPILOT-SP")
    )
    access_token  = credential.get_token("https://cognitiveservices.azure.com/.default").token
    client = AzureOpenAI(
        api_key=access_token,
        azure_endpoint="https://edav-dev-openai-eastus2-shared.openai.azure.com/",
        api_version="2024-08-01-preview",
        azure_deployment="gpt-4o-mini-nofilter")#,
        # model='gpt-4o')
    
    
    os.environ["AZURE_OPENAI_API_KEY"] = access_token
    os.environ["AZURE_OPENAI_ENDPOINT"] = "https://edav-dev-openai-eastus2-shared.openai.azure.com/"
    return client

# 🎯 Define Pydantic Model for Structured Output
class Summary(BaseModel):
    title: str = Field(description="title of the article")
    harmful: bool = Field(description="indicator if the title is harmful")
    sensational: bool = Field(description="indicator if the title is sensational")
    neutral: bool = Field(description="indicator if the title is neutral")
    protective: bool = Field(description="indicator if the title is protective")
    reasoning: str = Field(description="reasoning for indicator decisions")

# 📌 Function to Run LLM Headline Classification
def GetJson(headline):
    llm = AcquireCredentials()
    struct_llm = llm.with_structured_output(Summary)
    output_parser = JsonOutputParser(pydantic_object=Summary, partial=True)

    # Prompt template
    prompt = PromptTemplate(
        template="""
    You are an expert at the CDC. You will be provided with the title of a news article related to the suicide of a high profile individual.
    You must determine if the title is or is not protective, factual, sensational or harmful. Only one label is selected per headline. and you must provide your reasoning. Here are guidelines for labeling: 
    
    Protective 
    Headlines labeled as "Protective" actively support suicide prevention efforts with intentional framing to encourage protective actions and attitudes. These headlines:
    - Language: Use respectful and supportive language, explicitly highlighting suicide prevention resources or emphasizing solutions.
    - Framing: Clearly position suicide as preventable, promoting awareness of effective interventions, resources, or community efforts.
    - Focus: Emphasize positive actions, available support systems, or community initiatives aimed at preventing suicide and supporting mental health.
    
    Neutral
    Headlines labeled as "Neutral" neutrally present accurate, respectful, and non-sensational information. These headlines: 
    - Language: Use neutral, non-stigmatizing terms (e.g., "suicide rates have risen"), avoiding judgmental or overly dramatic phrases.
    - Framing: Present suicide as a complex, preventable public health issue without exaggeration.
    - Focus: Provide clear, factual information, accurately summarizing research or data without explicitly emphasizing prevention strategies.
    
    Sensational
    Headlines labeled as "Sensational" rely on provocative or emotionally charged language and imagery to attract attention, which can amplify harm. These headlines:
    - Language: Use shocking, dramatic, or emotionally manipulative phrases like "alarming suicide surge" or "society on the brink."
    - Tone: Focus disproportionately on the dramatic rise or fall of suicide statistics without providing meaningful context or constructive insights.
    - Impact: Exaggerate trends or statistics, creating unnecessary fear or despair about the phenomenon.
   
    Harmful
    Headlines labeled as "Harmful" include language, framing, or details that perpetuate stigma, misinformation, or potential harm. These headlines:
    - Language: Use stigmatizing, inflationary, or judgmental language, such as "rising concerns", "suicide epidemic," or overly simplistic explanations like "caused by economic struggles."
    - Framing: Oversimplify suicide as a single-cause phenomenon or frame it as inevitable, ignoring opportunities for prevention.
    - Negativity: Draw attention to problems instead of solutions, perpetuating a sense of hopelessness, or that the problem of suicide is too hard to solve.

    Below are some examples to illustrate how this should be done.

    Example 1: (Headline: Higher suicide rates tied to lack of basics: internet, insurance, income, CDC says; harmful: True; sensational: False;  factual: False; protective: False;\
    reasoning: Frames factors like internet, insurance, and income primarily as barriers rather than highlighting them as potential solutions.)
    Example 2: (Headline: Study finds social and economic factors crucial in preventing suicide, CDC reports; harmful: False; sensational: False; neutral: False; protective: True\
    reasoning: Emphasizes the preventative power of the identified factors, showcasing the potential for effective interventions.)
    Example 3: (Headline: CDC data reveal three social drivers that influence suicide risk; harmful: False; sensational: False; neutral: True; protective: False; \
    reasoning: Presents accurate and factual information neutrally without explicit focus on prevention strategies, but effectively summarizes the research findings.) 
    Determine if the title is Protective, Neutral, Sensational, or Harmful. Only one label is selected per headline, and you must provide reasoning.
    
    {format_instructions}
    This is the headline to score:\n{context}
    """,
        description="Headline Analysis",
        input_variables=["context"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()},
    )

    chain = prompt | struct_llm
    jsonResults = chain.invoke({"context": headline})
    return jsonResults

# 🔄 Update Database with Headline Scores
def update_headline_scores():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get headlines that haven't been classified yet
    cursor.execute("SELECT url, headline FROM articles WHERE protective IS NULL")
    articles = cursor.fetchall()

    for url, headline in articles:
        if not headline:
            continue  # Skip if no headline is available

        print(f"Processing: {headline}")  # Debugging output

        try:
            scores = GetJson(headline)

            cursor.execute("""
                UPDATE articles 
                SET protective = ?, neutral = ?, sensational = ?, harmful = ?, reasoning = ?
                WHERE url = ?
            """, (scores.protective, scores.neutral, scores.sensational, scores.harmful, scores.reasoning, url))

            conn.commit()
            print(f"✅ Updated: {url}")

        except Exception as e:
            print(f"❌ Error processing {url}: {e}")

    conn.close()
    print("✅ Headline classification complete!")

if __name__ == "__main__":
    update_headline_scores()

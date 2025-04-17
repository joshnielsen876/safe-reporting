import sqlite3
from pydantic import BaseModel, Field
from openai_utils import get_chat_model, get_structured_output_parser, create_prompt_template

# Database path (adjust for your Databricks workspace)
DB_PATH = "articles.db"

# 🎯 Define Pydantic Model for Structured Output
class Summary(BaseModel):
    title: str = Field(description="title of the article")
    harmful: bool = Field(description="indicator if the title is harmful")
    sensational: bool = Field(description="indicator if the title is sensational")
    neutral: bool = Field(description="indicator if the title is neutral")
    protective: bool = Field(description="indicator if the title is protective")
    reasoning: str = Field(description="reasoning for indicator decisions")

def analyze_headline(headline):
    """Analyze a headline using OpenAI"""
    llm = get_chat_model()
    struct_llm = llm.with_structured_output(Summary)
    output_parser = get_structured_output_parser(Summary)

    prompt_template = """
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

    Determine if the title is Protective, Neutral, Sensational, or Harmful. Only one label is selected per headline, and you must provide reasoning.
    
    {format_instructions}
    This is the headline to score:\n{context}
    """

    prompt = create_prompt_template(
        template=prompt_template,
        input_variables=["context"],
        format_instructions=output_parser.get_format_instructions()
    )

    chain = prompt | struct_llm
    return chain.invoke({"context": headline})

# 🔄 Update Database with Headline Scores
def update_headline_scores():
    """Update database with headline analysis scores"""
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
            scores = analyze_headline(headline)

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

import sqlite3
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

# Database path (adjust for your Databricks workspace)
DB_PATH = "articles.db"



# 🎯 Define Pydantic Model for TEMPOS Structured Output
class Summary(BaseModel):
    is_unrelated: bool = Field(description="True if the text is not a valid news article (e.g., error messages, login required).")
    suicide_framing: int = Field(description="Score for how the report frames the suicide")
    factual_information: int = Field(description="Score for inclusion of factual and non-speculative information")
    non_stigmatizing_language: int = Field(description="Score for use of appropriate, non-stigmatizing language")
    method_and_scene: int = Field(description="Score for how the report describes the suicide method and scene")
    suicide_note: int = Field(description="Score for how the report describes the suicide note")
    factors_and_reasons: int = Field(description="Score for how the report describes risk factors and reasons for suicide")
    sensational: int = Field(description="Score for use of sensational language")
    glamorized: int = Field(description="Score for whether the report glamorizes suicide")
    resources: int = Field(description="Score for inclusion of suicide prevention and mental health resources")
    reasoning: str = Field(description="Verbose reasoning for scores, citing snippets from the article")

# 📌 Function to Run LLM TEMPOS Analysis
def GetJson(article_text):
    llm = AcquireCredentials()
    struct_llm = llm.with_structured_output(Summary)
    output_parser = JsonOutputParser(pydantic_object=Summary, partial=True)

    # Prompt template
    prompt = PromptTemplate(
        template="""
    You are an expert at the CDC. You will be provided with the text of a news article that is reporting on the suicide of a high profile \
    figure. First, determine if the article is valid or unrelated (e.g., error messages, login required, blank pages).\
    If it is unrelated, set "is_unrelated" to True and ignore the other fields. Otherwise, provide the full analysis. \
        Your task is to score the article on the following safe reporting guidelines, choosing from 0, 1, or 2. Use a score of 0 when \
    there is harmful messaging and no adherence to the instructions. Use a score of 1 when there is mixed messaging and partial adherence.\
    Use a score of 2 when the messaging is helpful and full adherence to the guidelines/instructions. Instructions for reporters are as follows.

    1. Framing the suicide. A helpful article which would score a 2 frames suicide as a preventable mental health outcome; reports that \
    coping skills, support, and treatment work for most people (recovery is possible). A harmful article which would score a 0 \
    explicitly presents or strongly implies that suicide is a common, acceptable, or inevitable response to hardship; frames suicide as \
    "a way out" or a way of taking control of one's circumstances. A mixed articles which scores 1 doesn't portray suicide as an escape or \
    inevitable response to hardship, but fails to include that suicide is preventable and that resources are available to those who are \
    struggling. For clarity, 

    2. Factual information. A helpful article which would score a 2 includes information that is clearly factual in nature, not speculative. \
    May include quotes or objective information from informed sources (e.g. people or organizations with mental health or suicide prevention\
    expertise, and/or people with lived experience). A harmful article which scores 0 includes information that is clearly speculative \
    (e.g. non-factual) about the causes of/reasons for suicide. Sources of information (e.g. family/friends/professionals) are not factually\
    informed or are inaccurate/inappropriate. A mixed article which scores 1 does not include speculation but also fails to provide factual\
    information about suicide/mental health.
    
    3. Non-stigmatizing language. A helpful article which would score a 2 includes language that is not stigmatizing that is more neutral \
    and treates suicide similarly to other causes of death (e.g. "died by suicide"). A harmful article which scores 0 uses inappropriate or \
    stigmatizing language that implies criminality (e.g. "committed"), judgement, or positive connotations (e.g. "successful attempt"). \
    A mixed article that scores 1 uses a mix of appropriate and inappropriate language.

    4. Method and scene. A helpful article which would score a 2 reports the death as a suicide but keeps information general and does not \
    mention method.  A harmful article which scores 0 describes or depicts, in a detailed manner, the method and/or location of the suicde; \
    'sets the scene' by including information about what was found at the scene of death, how the person was found, or the type of object used.\
    A mixed article which scores 1 briefly mentions suicide method (e.g. asphyxiation, overdose) but does not include explicit details about \
    the method used or the scene of death. 

    5. Suicide notes. A helpful article, which scores 2, does not mention a note or its contents, or simply states that no note was found. \
    A harmful article, which scores 0, shares specific content directly from a suicide note. A mixed article which scores 1 reports that a \
    note was found but does not include any content therefrom. 

    6. Factors and reasons. A helpful article which would score a 2 acknowledges the complexity of suicide and describes risk factors \
    (e.g. mental illness, economic hardship, family issues) that give suicide context. A harmful article which scores 0 oversimplifies or \
    speculates on the reason for suicidel simplifies the issue of suicide by directly or indirectly attributing the death to a single reason \
    or saying that it happened "without warning". A mixed article (scores 1) does not speculate about reasons for death but does not include \
    information about risk factors. Again, the simple absence of a discussion about factors and reasons scores 1, not 0. 

    7. Sensational language. A helpful article that scores 2 reports on the death using non-sensational facts and language that focuses on \
    the person's life rather than death (similar to reporting on non-suicide deaths); when referring to suicide rates, references best available\
    data and uses words like 'increase' or 'rise'. A harmful article that scores 0 includes shocking or provocative language/details about \
    suicide designed to elicit and emotional response; uses sensational langauge (e.g. 'epidemic', 'skyrocketing', 'spike') when describing \
    suicide rates. A mixed article that scores 1 includes some sensative language that focuses on the person's life rather than death, but also \
    includes a few instances of sensational language or details about the death. NOTE: Harmful sensational language refers to language about \
    suicide specifically. As people mourn the loss of loved ones, some sensational language may be used to describe their feelings of loss, \
    which is not the same as harmful sensational language about suicide. 

    8. Glamorization. A helpful article which scores a 2 does NOT portray suicide in a positive or glamorous manner; a helpful article focuses \
    on the life they lived, rather than their death, acknowledges positive aspects of their life, as well as their struggles. In a harmful \
    article that scores 0, suicide is frequently glamorized; includes several tributes or portrays suicide in a positive manner (e.g. ties \
    suicide to heroism, romance, or honor). A mixed article that scores 1 includes some content that glamorizes or portrays suicide in a \
    positive light; portrays their life in an idealized way or glamorized way without acknowledging struggles. NOTE: glamorizing suicide is \
    different from glamorizing the life of the deceased, especially when the deceased is a celebrity. It is normal to celebrate the life of the\
    person and celebration of life should not be considered as glamorizing suicide. An example of harmful glamorization would be content like\
    "It’s telling that the deceased killed himself in this picturesque, story tale village" which romanticizes the suicide, or "His shocking \
    death by suicide led to an outpouring of grief and support from celebrities around the world", which falsely implies that suicide is how \
    you get people to show love and support. 

    9. Resources. A helpful article that scores 2 includes a suicide hotline or crisis number as well as additional resources for \
    mental health care and suicide prevention, for example, local mental health resources, suicide prevention organizations, or websites. A \
    harmful article that scores 0 does not include any information about suicide prevention or crisis resources. A mixed article that scores \
    1 includes a hotline or crisis number, but does not include any additional information about suicide prevention or crisis resources.

    When reasoning through the decision, actively remind yourself of the criteria given above. You will also need to include the ultimate \
    reason for your decision. If one of the scores is 0, you MUST provide at least ONE EXACT PHRASE from the article that you used to make\
    your decision.
    
    For each criteria, the options are 0, 1, or 2. This is the article to evaluate:\n{context}

    Remember to make your decision based on the above safe reporting guidelines. {format_instructions}

            
    """,
        description="TEMPOS Analysis",
        input_variables=["context"],
        partial_variables={"format_instructions": output_parser.get_format_instructions()},
    )

    chain = prompt | struct_llm
    jsonResults = chain.invoke({"context": article_text})
    return jsonResults

# 🔄 Update Database with TEMPOS Scores
def update_tempos_scores():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get articles that haven't been analyzed yet
    cursor.execute("SELECT url, article_text FROM articles WHERE suicide_framing IS NULL")
    articles = cursor.fetchall()

    for url, article_text in articles:
        if not article_text:
            continue  # Skip if no article text is available

        print(f"Processing TEMPOS analysis for: {url}")  # Debugging output

        try:
            scores = GetJson(article_text)

            # 🛑 Skip updating the database if the article is unrelated
            if scores.is_unrelated:
                print(f"⚠️ Skipping {url} (Unrelated Content)")
                continue  

            # ✅ Update database with TEMPOS scores
            cursor.execute("""
                UPDATE articles 
                SET suicide_framing = ?, factual_information = ?, non_stigmatizing_language = ?, 
                    method_and_scene = ?, suicide_note = ?, factors_and_reasons = ?, sensational = ?, 
                    glamorized = ?, resources = ?, reasoning = ?
                WHERE url = ?
            """, (scores.suicide_framing, scores.factual_information, scores.non_stigmatizing_language,
                  scores.method_and_scene, scores.suicide_note, scores.factors_and_reasons, scores.sensational, 
                  scores.glamorized, scores.resources, scores.reasoning, url))

            conn.commit()
            print(f"✅ TEMPOS scores updated for: {url}")

        except Exception as e:
            print(f"❌ Error processing TEMPOS for {url}: {e}")

    conn.close()
    print("✅ TEMPOS analysis complete!")

if __name__ == "__main__":
    update_tempos_scores()

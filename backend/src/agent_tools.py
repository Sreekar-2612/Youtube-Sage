from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def build_agent(llm, retriever):

    @tool
    def search_transcript(query: str) -> str:
        """Search the current YouTube video's transcript for relevant passages."""
        docs = retriever.invoke(query)
        if not docs:
            return "No relevant passage found in the transcript."
        return "\n\n".join(d.page_content for d in docs)

    @tool
    def word_count(text: str) -> str:
        """Count the number of words in a given piece of text."""
        return str(len(text.split()))

    tools = [search_transcript, word_count]

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",
             "You are YT-Sage, an assistant that answers questions about a YouTube "
             "video. Use the search_transcript tool to find relevant information "
             "before answering. Only use word_count if explicitly asked for a "
             "word/length count."),
            MessagesPlaceholder("chat_history"),
            ("human", "{question}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True)
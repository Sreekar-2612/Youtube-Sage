from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def build_agent(llm, retriever):

    @tool
    def search_transcript(query: str) -> str:
        """Search the current YouTube video's transcript for passages relevant to a specific topic or question."""
        docs = retriever.invoke(query)
        if not docs:
            return "No relevant passage found in the transcript."
        return "\n\n".join(d.page_content for d in docs)

    @tool
    def generate_video_chapters(topic: str = "") -> str:
        """Scan video transcript and construct structured video chapter bookmarks with timestamps [MM:SS]."""
        search_query = topic.strip() if topic.strip() else "introduction overview conclusion summary"
        docs = retriever.invoke(search_query)
        if not docs:
            return "Unable to extract chapter bookmarks from transcript."
        lines = []
        for d in docs:
            ts = d.metadata.get("timestamp", "00:00")
            snippet = d.page_content.split("] ", 1)[-1][:70].strip()
            lines.append(f"- [{ts}] {snippet}...")
        return "\n".join(lines)

    @tool
    def generate_study_quiz(topic: str = "general") -> str:
        """Generate a 3-question multiple choice study quiz with answer keys and timestamp references based on video content."""
        docs = retriever.invoke(topic if topic else "key concept definitions explanation")
        if not docs:
            return "Insufficient transcript context to create study quiz."
        context_preview = "\n\n".join(d.page_content[:200] for d in docs[:3])
        return (
            f"Based on the following video context, format 3 multiple-choice questions:\n\n{context_preview}"
        )

    @tool
    def extract_code_or_tools(topic: str = "all") -> str:
        """Extract code snippets, libraries, CLI commands, and software tools mentioned in the video."""
        docs = retriever.invoke(f"{topic} code function library install api package command syntax")
        if not docs:
            return "No programming tools or code found in transcript."
        return "\n\n".join(d.page_content for d in docs)

    tools = [search_transcript, generate_video_chapters, generate_study_quiz, extract_code_or_tools]

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",
             "You are YT-Sage, an elite video intelligence co-pilot. You have access to specialized tools "
             "to analyze YouTube transcripts:\n"
             "- search_transcript: Search for specific facts or answers.\n"
             "- generate_video_chapters: Create structured chapter timestamps.\n"
             "- generate_study_quiz: Build a multiple-choice quiz with answer keys.\n"
             "- extract_code_or_tools: Extract code, libraries, and tools.\n\n"
             "Always cite exact timestamps in format [MM:SS] (e.g. [03:15]) when answering."),
            MessagesPlaceholder("chat_history"),
            ("human", "{question}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True)


from langchain.tools import tool
from typing import Dict,Any
from tavily import TavilyClient
from dotenv import load_dotenv
import os
from datetime import date
import serpapi
from langchain.tools import tool
from pprint import pprint
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain.messages import HumanMessage
from langchain.agents import create_agent

load_dotenv(override=True)
@tool
def search_flights_api(
    departure_airport: str,
    arrival_airport: str,
    outbound_date: str,
):
    """Search one-way economy flights for a date selected in the destination's wedding season."""
    api_key = os.getenv("SERPAPI_API_KEY")

    parsed_date = date.fromisoformat(outbound_date)
    if parsed_date.isoformat() != outbound_date:
        raise ValueError("outbound_date must use YYYY-MM-DD format")
    if parsed_date <= date.today():
        raise ValueError("outbound_date must be a future date; choose the next occurrence of the destination's wedding season")
    client = serpapi.Client(api_key=api_key)

    results = client.search({
        "engine": "google_flights",
        "departure_id": departure_airport,
        "arrival_id": arrival_airport,
        "outbound_date": outbound_date,
        "type": 2,
        "currency": "INR",
    })

    return results.get("best_flights", [])


tavily_Search = TavilyClient()

@tool
def web_search(query:str) -> Dict[str,Any]:
    """Searching in web for information"""
    response = tavily_Search.search(query, max_results=3)
    return {
        "results": [
            {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", "")[:400],
            }
            for result in response.get("results", [])
        ]
    }


# <h2>Creating SubAgents</h2>

model=ChatGroq(model="openai/gpt-oss-20b", max_tokens=1024)
# model =ChatGoogleGenerativeAI(model="gemini-3.6-flash")

travel_agent = create_agent(
    model=model,
    tools=[search_flights_api],
    system_prompt=f"""Find one-way economy flights for the wedding. Today is {date.today().isoformat()}. Choose one future date in a pleasant wedding season and search once. For India or Delhi use DEL; for Paris use CDG. Call search_flights with airport codes and outbound_date in YYYY-MM-DD format. Return up to 3 options, prioritizing low price and short duration, and state the season/date. If SERPAPI_API_KEY is missing or invalid, explain that; do not retry.
    """

)

playlist_agent=create_agent(
    model=model,
    tools=[web_search],
    system_prompt="""Create a concise 10-song wedding playlist matching the requested language and style. Group songs into ceremony categories. Use at most one web search and summarize briefly."""
)

venue_agent=create_agent(
    model=model,
    tools=[web_search],
    system_prompt="""Find up to 3 wedding venues matching the destination and guest count. Search once. Briefly report name, capacity, price if available, and source URLs. Do not ask questions."""

)



# <h2>Main coordinator</h2>

@tool
def search_flights(origin: str, destination: str) -> str:
    """Search flights from a user-provided city or country to the wedding destination."""
    response = travel_agent.invoke({"messages": [HumanMessage(content=f"Find flights from {origin} to {destination}")]})
    return response['messages'][-1].content

@tool
def search_venues(destination: str, guest_count: str) -> str:
    """Venue agent chooses the best venue for the given location and capacity."""
    query = f"Find wedding venues in {destination} for {guest_count} guests"
    response = venue_agent.invoke({"messages": [HumanMessage(content=query)]})
    return response['messages'][-1].content

@tool
def suggest_playlist(genre: str) -> str:
    """Playlist agent curates the perfect playlist for the given genre."""
    query = f"Find {genre} tracks for wedding playlist"
    response = playlist_agent.invoke({"messages": [HumanMessage(content=query)]})
    return response['messages'][-1].content


coordinator = create_agent(
    model=model,
    tools=[search_flights, search_venues, suggest_playlist],
    system_prompt="""
    You are a wedding coordinator. Extract the origin, destination, guest count, and playlist genre from the user's request.
    Call the flight tool with the origin exactly as the user described it (city or country) and the destination. The travel specialist will choose the airports.
    Call the venue tool with the destination and guest count, and call the playlist tool with the requested genre.
    Once you have received their answers, coordinate the perfect wedding for me.
    """
)


response =coordinator.invoke(
    {
        "messages": [HumanMessage(content="I'm from India and I'd like a wedding in Paris for 100 guests create Telugu playlist genre should be timeless classic")],
    }
     #tag traces to make them easy to find in Langsmith. Increase number of steps the agent can take to 40.
)

pprint(response)

print(response['messages'][-1].content)

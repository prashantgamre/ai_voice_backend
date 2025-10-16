from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions , function_tool
from livekit.plugins import noise_cancellation
from livekit.plugins import google
from Ai_techer_Prompt import AI_Teacher_Instructions
import os

load_dotenv(".env.local")

api_key=os.getenv("Google_API_KEY")

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=AI_Teacher_Instructions)



async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(model="gemini-2.0-flash-exp")  #gemini-2.0-flash-exp
        )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` instead for best results
            noise_cancellation=noise_cancellation.BVC(),
        )
    )

    await session.generate_reply(
        instructions="Greet the user and tell i am AI Teacher and ask user about which subject user want to learn."
    )

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))

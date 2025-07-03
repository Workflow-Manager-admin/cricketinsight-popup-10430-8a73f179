import os
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from marshmallow import Schema, fields
import openai
import random

blp = Blueprint(
    "Cricket Analysis API",
    "cricket_api",
    url_prefix="/api",
    description="Cricket scenario, question, analysis, and mock data routes",
)

# === Schemas for OpenAPI and validation ===

class MatchDetailsSchema(Schema):
    """Schema for user input to generate a cricket scenario and related tasks."""
    team_batting = fields.Str(required=True, description="Batting team name")
    team_bowling = fields.Str(required=True, description="Bowling team name")
    runs = fields.Int(required=True, description="Current runs scored")
    wickets = fields.Int(required=True, description="Wickets fallen")
    overs = fields.Float(required=True, description="Overs completed (e.g., 10.2)")
    target = fields.Int(required=False, description="Target runs (optional, for 2nd innings)")
    additional_notes = fields.Str(required=False, description="Any extra context (optional)")

class ScenarioSchema(Schema):
    scenario = fields.Str(required=True, description="A concise textual scenario based on provided match details")

class QuestionSchema(Schema):
    question = fields.Str(required=True, description="Yes/no prediction question about the scenario")

class PredictionInputSchema(Schema):
    scenario = fields.Str(required=True, description="Scenario text")
    question = fields.Str(required=True, description="Yes/no question")
    user_answer = fields.Bool(required=True, description="User's answer: true=Yes, false=No")

class AnalysisSchema(Schema):
    summary = fields.Str(required=True, description="AI-generated analysis/justification for the user's prediction")

class MockPlayerDataSchema(Schema):
    player_name = fields.Str(required=True)
    runs = fields.Int()
    strike_rate = fields.Float()
    wickets = fields.Int()
    economy = fields.Float()

class MockPlayersOutSchema(Schema):
    players = fields.List(fields.Nested(MockPlayerDataSchema), required=True)

# === Scenario generation endpoint ===

@blp.route("/generate_scenario")
class GenerateScenario(MethodView):
    """
    Generate a concise cricket scenario from live match details.
    """
    @blp.arguments(MatchDetailsSchema)
    @blp.response(200, ScenarioSchema)
    def post(self, match_details):
        # Dummy scenario: In production, could use OpenAI or templating
        scenario = (
            f"After {match_details['overs']} overs, {match_details['team_batting']} "
            f"have scored {match_details['runs']} runs for {match_details['wickets']} wickets"
        )
        if match_details.get("target"):
            scenario += f", chasing a target of {match_details['target']}."
        else:
            scenario += "."
        if match_details.get("additional_notes"):
            scenario += f" Note: {match_details['additional_notes']}"
        return {"scenario": scenario}

# === Question generation endpoint ===

@blp.route("/generate_question")
class GenerateQuestion(MethodView):
    """
    Generate a simple yes/no prediction question from a scenario (for user interaction).
    """
    class GenQuestionIn(Schema):
        scenario = fields.Str(required=True)

    @blp.arguments(GenQuestionIn)
    @blp.response(200, QuestionSchema)
    def post(self, scenario_in):
        # Simple logic - or use OpenAI in production
        scenario = scenario_in["scenario"]
        # Randomly pick a template
        templates = [
            "Will the batting team reach {rand_runs} runs?",
            "Can the batting team win from here?",
            "Will the next wicket fall in the upcoming over?",
            "Will a fifty be scored in the next 5 overs?",
            "Will {team_batting} win this match?",
        ]
        # Extract team name if possible
        team_batting = None
        import re
        m = re.search(r"([A-Za-z ]+) have scored", scenario)
        if m:
            team_batting = m.group(1).strip()
        template = random.choice(templates)
        if "{team_batting}" in template and team_batting:
            question = template.format(team_batting=team_batting)
        elif "{rand_runs}" in template:
            import re
            runs = re.search(r"scored (\d+) runs", scenario)
            next_ = str(int(runs.group(1)) + random.choice([10, 20, 30])) if runs else "100"
            question = template.format(rand_runs=next_)
        else:
            question = template
        return {"question": question}

# === Analysis endpoint (OpenAI-powered) ===

@blp.route("/analyze_prediction")
class AnalyzePrediction(MethodView):
    """
    Analyze the user's yes/no prediction and provide reasoning via OpenAI.
    """
    @blp.arguments(PredictionInputSchema)
    @blp.response(200, AnalysisSchema)
    def post(self, payload):
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            abort(500, message="OpenAI API key not set in environment. Please set OPENAI_API_KEY.")

        scenario = payload['scenario']
        question = payload['question']
        user_answer = 'Yes' if payload['user_answer'] else 'No'

        prompt = (
            "Given the cricket scenario:\n"
            f"{scenario}\n"
            f"Question: {question}\n"
            f"User's answer: {user_answer}\n"
            "Provide a one-paragraph expert analysis justifying the user's answer, using logical cricket reasoning."
        )

        try:
            openai.api_key = openai_api_key
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert cricket analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=128
            )
            analysis = response.choices[0].message["content"].strip()
        except Exception as e:
            abort(502, message=f"OpenAI error: {str(e)}")
            return
        return {"summary": analysis}

# === Mock player data endpoint ===

@blp.route("/mock_player_data")
class MockPlayerData(MethodView):
    """
    Provide mock player performance data for visualization (bar/line charts etc).
    """
    @blp.response(200, MockPlayersOutSchema)
    def get(self):
        # Random mock player stats for demo
        players = [
            {
                "player_name": "Virat Kohli",
                "runs": random.randint(20, 90),
                "strike_rate": round(random.uniform(90, 150), 1),
                "wickets": random.randint(0, 1),
                "economy": 0 if random.random() > 0.5 else round(random.uniform(6, 8), 2),
            },
            {
                "player_name": "Jos Buttler",
                "runs": random.randint(15, 80),
                "strike_rate": round(random.uniform(120, 166), 1),
                "wickets": random.randint(0, 1),
                "economy": 0 if random.random() > 0.5 else round(random.uniform(6, 8), 2),
            },
            {
                "player_name": "Rashid Khan",
                "runs": random.randint(0, 30),
                "strike_rate": round(random.uniform(80, 120), 1),
                "wickets": random.randint(1, 4),
                "economy": round(random.uniform(4, 8), 2),
            },
            {
                "player_name": "Pat Cummins",
                "runs": random.randint(0, 20),
                "strike_rate": round(random.uniform(70, 120), 1),
                "wickets": random.randint(1, 3),
                "economy": round(random.uniform(5, 9), 2),
            },
            {
                "player_name": "Rohit Sharma",
                "runs": random.randint(15, 110),
                "strike_rate": round(random.uniform(121, 175), 1),
                "wickets": 0,
                "economy": 0,
            },
        ]
        return {"players": players}

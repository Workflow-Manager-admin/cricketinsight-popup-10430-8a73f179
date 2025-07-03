# cricketinsight-popup-10430-8a73f179

## Flask Backend: Quick Start

This Flask backend exposes REST APIs for scenario generation, yes/no question formulation, prediction analysis (via OpenAI), and mock player data serving (for visualizations).

### Requirements
- Python 3.9+
- `pip install -r requirements.txt`
- Set your OpenAI API key:  
  `export OPENAI_API_KEY=your_api_key_here`

### Running the Development Server
```bash
cd flask_backend
export OPENAI_API_KEY=your_api_key_here
python run.py
```

The API will be available at: `http://localhost:5000`
Interactive Swagger docs: `http://localhost:5000/docs/`

### Main Endpoints

- **POST /api/generate_scenario**  
  Input: `{ team_batting, team_bowling, runs, wickets, overs, [target], [additional_notes] }`  
  Output: `{ scenario }`

- **POST /api/generate_question**  
  Input: `{ scenario }`  
  Output: `{ question }`

- **POST /api/analyze_prediction**  
  Input: `{ scenario, question, user_answer }`  
  Output: `{ summary }`  
  _Requires_ `OPENAI_API_KEY`

- **GET /api/mock_player_data**  
  Output: `{ players: [ ... ] }` _(mock player performance data)_

No persistent storage is used; all data is ephemeral and generated per request.

Task completed: Flask backend REST API for cricket scenario generation, question, OpenAI analysis, and mock data is implemented.
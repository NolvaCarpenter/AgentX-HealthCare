.PHONY: run gradio expo help server

help:
	@echo "Available commands:"
	@echo "  make run      - Run the CLI application"
	@echo "  make gradio   - Run the Gradio web interface"
	@echo "  make expo     - Run the Expo frontend"
	@echo "  make png      - Generate the conversation graph"
	@echo "  make server   - Run the FastAPI server"

run:
	@echo "Starting CLI application..."
	cd baymax_team_collab && poetry run python main.py

gradio:
	@echo "Starting Gradio web interface..."
	cd baymax_team_collab && poetry run python main_gradio.py

expo:
	@echo "Starting Expo frontend..."
	cd expo-client && npm start 

png:
	@echo "Generating conversation graph..."
	cd baymax_team_collab && poetry run python visualize_graph.py

server:
	@echo "Starting FastAPI server..."
	cd baymax_team_collab && PYTHONPATH=.. poetry run uvicorn server.service:app --reload --host 127.0.0.1 --port 1500





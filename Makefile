.PHONY: run gradio expo help

help:
	@echo "Available commands:"
	@echo "  make run      - Run the CLI application"
	@echo "  make gradio   - Run the Gradio web interface"
	@echo "  make expo     - Run the Expo frontend"

run:
	@echo "Starting CLI application..."
	cd baymax_team_collab && poetry run python main.py

gradio:
	@echo "Starting Gradio web interface..."
	cd baymax_team_collab && poetry run python main_gradio.py

expo:
	@echo "Starting Expo frontend..."
	cd expo-client && npm start 





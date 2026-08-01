.PHONY: install install-dev test ui docker-up docker-down

install:
	python3 -m pip install -r requirements.txt

install-dev:
	python3 -m pip install -r requirements-dev.txt

test:
	python3 -m pytest -q

ui:
	streamlit run streamlit_app.py

docker-up:
	docker compose up --build

docker-down:
	docker compose down

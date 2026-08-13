.PHONY: backend frontend install-backend install-frontend test seed-db docker-up docker-down

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && pytest -v

seed-db:
	cd backend && python -m scripts.seed_dummy_data

docker-up:
	docker compose up --build

docker-down:
	docker compose down

.PHONY: test eval seed docker
test:
	cd backend && pytest
	cd frontend && npm run lint && npm run typecheck && npm run build
eval:
	cd backend && python run_evaluation.py
seed:
	curl -X POST http://localhost:8000/api/demo/reset
docker:
	docker compose up --build


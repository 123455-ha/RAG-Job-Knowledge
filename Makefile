install:
	python -m pip install -r backend/requirements.txt
test:
	cd backend && pytest -q
run-backend:
	uvicorn backend.app.main:app --reload --port 8000
demo-data:
	python scripts/init_demo_data.py

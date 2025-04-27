start cmd /k "cd enveye-backend && uvicorn enveye_backend:app --host 0.0.0.0 --port 8000 --reload"
start cmd /k "cd enveye-frontend && npm install && npm run build && npm run preview -- --port 5173"

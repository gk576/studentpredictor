# EduPredict frontend

React 19 client for the local Student Performance Predictor.

## Run locally

The Django API must be running on `http://127.0.0.1:8000` first.

```powershell
npm install
npm start
```

Open http://localhost:3000 and log in with `demo` / `demo12345`.

The API base URL is defined in `src/api.js`. If you change the Django port, update
that constant too.

See the project root [README.md](../README.md) and
[assessment report](../docs/ASSESSMENT_REPORT.md) for full documentation.

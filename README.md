# Financial Research Assistant

An AI-powered application that helps users quickly understand a company's latest financial standing and potential risks. The application uses a sophisticated agent-based architecture to gather, analyze, and present financial data in a clear and concise format.

## Features

- Company financial analysis
- Real-time data fetching
- Risk assessment
- Structured report generation
- Modern, responsive UI

## Tech Stack

### Backend
- FastAPI
- OpenAI GPT-4
- News API
- Yahoo Finance API
- Python 3.9+

### Frontend
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Heroicons

## Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn
- OpenAI API key
- News API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd financial-research-agent/backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file:
```bash
OPENAI_API_KEY=your_openai_api_key
NEWS_API_KEY=your_news_api_key
```

5. Start the backend server:
```bash
uvicorn app.main:app --reload
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd financial-research-agent/frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Start the development server:
```bash
npm run dev
# or
yarn dev
```

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Enter a company name in the search box
3. Click "Analyze" to generate a comprehensive report
4. View the company overview, financial metrics, and risk assessment

## API Endpoints

- `POST /api/v1/analyze`
  - Request body: `{ "company_name": "string" }`
  - Returns a comprehensive company analysis

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License # -Vibe-Coding-Financial-Research-Agent
# Vibe-Coding-Financial-Research-Agent

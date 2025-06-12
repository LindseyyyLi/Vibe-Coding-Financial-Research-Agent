# Financial Research Agent

An intelligent AI-powered financial research assistant that helps users analyze companies, understand their financial standing, and assess potential risks. The application combines advanced language models with financial data APIs to provide comprehensive, real-time analysis and insights.

## 🤔 Background & Motivation

This project is driven by my fascination with large language models (LLMs) and their transformative impact on real-world tasks. I built this app using Cursor, exploring their “vibe coding” feature—which absolutely amazed me with how quickly ideas go from concept to working code. I wanted to see just how powerful LLMs can be for building user-friendly, domain-specific research agents, and this project is the result.


## 🌟 Key Features

- **Company Analysis**: Deep dive into company financials, metrics, and performance
- **Real-time Data**: Live financial data fetching from Yahoo Finance
- **News Integration**: Latest news and updates about analyzed companies
- **AI-Powered Insights**: Advanced analysis using OpenAI's GPT models
- **Interactive Reports**: Well-structured, easy-to-understand financial reports
- **Modern UI**: Responsive and user-friendly interface built with Next.js

## 🛠 Technology Stack

### Backend (FastAPI + Python)
- FastAPI 0.104.1 - Modern, fast web framework
- OpenAI 1.3.0 - AI language model integration
- Yahoo Finance API - Real-time financial data
- News API - Current news and updates
- Pandas 2.1.2 & NumPy 1.26.1 - Data processing
- Python 3.9+ with asyncio support

### Frontend (Next.js + React)
- Next.js 14.0.3 - React framework
- React 18.2.0 - UI library
- TypeScript - Type-safe development
- Tailwind CSS 3.3.5 - Styling
- Heroicons 2.0.18 - UI icons
- Axios - API communication

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- Node.js 18 or higher
- npm or yarn package manager
- OpenAI API key
- News API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory:
```env
OPENAI_API_KEY=your_openai_api_key
NEWS_API_KEY=your_news_api_key
```

5. Start the backend server:
```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
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

The application will be available at `http://localhost:3000`

## 📚 Project Structure

```
financial-research-agent/
├── backend/
│   ├── app/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
└── README.md
```

## 🔄 API Endpoints

The backend provides the following REST API endpoints:

- `POST /api/v1/analyze`
  - Analyzes a company based on provided information
  - Request body: `{ "company_name": "string" }`
  - Returns comprehensive analysis results

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
# or
yarn test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for their powerful language models
- Yahoo Finance for financial data
- News API for current events integration
- The open-source community for various tools and libraries used in this project

## Example Usage

![example](https://github.com/user-attachments/assets/7c2d41cb-ded0-4d46-be48-9f1337c4eca7)



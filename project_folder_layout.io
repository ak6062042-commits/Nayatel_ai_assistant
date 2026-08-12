nayatel-ai-assistant/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routes/
│   │   │   └── chat.py
│   │   ├── rag/
│   │   │   ├── ingest.py
│   │   │   ├── retriever.py
│   │   │   ├── pipeline.py
│   │   │   ├── history.py
│   │   │   └── prompt.py
│   │   ├── llm/
│   │   │   └── client.py
│   │   └── models/
│   │       └── schemas.py
│   │
│   ├── data/
│   │   ├── raw/
│   │   └── processed/
│   │
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│
├── docs/
│
├── README.md
└── .gitignore
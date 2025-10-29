# FinTrack - AI Powered Expense Tracker 

**FinTrack** is an intelligent personal finance management application that helps you track expenses, manage income, and gain AI-powered insights into your spending habits. Built with Python and Streamlit, it features secure multi-user authentication, automated transaction categorization from bank statements (CSV/XLSX), and interactive visualizations. The integrated FinBot provide personalized budget recommendations without any cloud dependencies, ensuring complete privacy. With real time balance tracking, comprehensive CRUD operations, and beautiful Plotly dashboards, FinTrack makes managing your finances simple and insightful.

Perfect for students, professionals, and anyone looking to take control of their financial health with a modern, privacy focused solution.

## Features

- **User Authentication**: Secure login and registration system with SHA256 password hashing
- **Expense Tracking**: Add, edit, view, and delete expenses with categories
- **Income Management**: Track multiple income sources with full CRUD operations
- **AI-Powered Insights**: Get financial advice and budget analysis.
- **Interactive Dashboards**: Beautiful visualizations with Plotly charts
- **Month-by-Month Analysis**: Track spending patterns across different months
- **Multi-User Support**: Each user has their own isolated database
- **Real-Time Balance Tracking**: Automatic balance updates with every transaction

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Ollama (for AI features)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/VVenkatesh215/fintrack-ai-powered-expense-tracker.git
cd fintrack-ai-powered-expense-tracker
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install and setup Ollama**

**Windows:**
- Download from [ollama.com/download](https://ollama.com/download)
- Run the installer
- Open PowerShell and pull the model:
```powershell
ollama pull llama3.2:1b
```

**Linux/Mac:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2:1b
```

4. **Run the application**
```bash
streamlit run Home.py
```

The app will open in your browser at `http://localhost:8501`

## Project Structure

```
FinTrack/
├── Home.py                      # Main entry point with login/register
├── auth.py                      # Authentication manager
├── requirements.txt             # Python dependencies
├── pages/
│   ├── 1_Transaction_Log.py    # Add expenses and income
│   ├── 2_View_Expenses.py      # View, edit, and delete transactions
│   └── 3_Report.py             # Analytics and AI insights
├── utils/
│   ├── expenseTracker.py       # Database operations (CRUD)
│   ├── finbot.py               # AI-powered financial insights
│   └── chatbot_ui.py           # Reusable chatbot component
└── *.db                         # SQLite databases (auto-generated)
```

## Usage

### 1. Register/Login
- Create a new account or login with existing credentials
- Each user gets their own secure database

### 2. Add Transactions
- Navigate to **Transaction Log** in the sidebar
- Add expenses with categories (Food, Transport, Entertainment, etc.)
- Add income with sources (Salary, Business, Investment, etc.)
- Forms stay open for multiple entries

### 3. View & Edit
- Go to **View Expenses** to see all transactions
- Edit any transaction by clicking the edit icon
- Delete unwanted entries
- All changes update your balance in real time

### 4. Analyze & Get Insights
- Visit the **Report** page for visual analytics
- View spending by category with pie charts
- Track monthly trends with area charts
- Compare income vs expenses with bar charts
- Use **FinBot** (available on all pages) to ask questions like:
  - "How much did I spend in October?"
  - "What's my biggest expense category?"
  - "Give me budgeting advice"

## AI Features

FinTrack uses **Ollama** with the **llama3.2:1b** model for local AI processing:
- **100% Private**: All AI processing happens locally on your machine
- **No API Costs**: Free to use, no cloud API charges
- **Offline Capable**: Works without internet connection
- **Month-by-Month Analysis**: Accurately analyzes your spending patterns
- **Personalized Advice**: Tailored financial insights based on your data

## Validation & Security

- Amount validation
- Category/source selection required
- Title validation
- Password hashing (SHA256)
- User specific databases for data isolation
- Session state management for security

## Technologies Used

- **Frontend**: Streamlit 1.41.1
- **Database**: SQLite3
- **AI**: Ollama (llama3.2:1b)
- **Visualization**: Plotly 5.24.1
- **Data Processing**: Pandas 2.2.3
- **Security**: Hashlib (SHA256)

## Dependencies

```
streamlit==1.41.1
pandas==2.2.3
plotly==5.24.1
ollama==0.4.4
```


## Future Enhancements

- [ ] Budget goal setting
- [ ] Recurring transactions
- [ ] Export to CSV/PDF
- [ ] Mobile responsive design
- [ ] Multiple currency support
- [ ] Bill reminders
- [ ] Category customization

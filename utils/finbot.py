import traceback

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


def get_budget_insights(user_query, transactions_text):
    """
    Get budget or expense insights using Ollama local model.
    Falls back to local summary if Ollama is unavailable.
    
    The transactions_text is already loaded from the user's .db file via Account.format_transactions_for_ai()
    so we don't need to load it again here.
    """
    from datetime import datetime
    
    # Format transaction data in a cleaner way
    tx = transactions_text if isinstance(transactions_text, dict) else {}
    incomes = tx.get("income", []) if isinstance(tx, dict) else []
    expenses = tx.get("expenses", []) if isinstance(tx, dict) else []
    
    if not incomes and not expenses:
        return "No financial data available. Please add some income or expenses to get started."
    
    # Parse dates and organize by month
    monthly_data = {}
    
    for exp in expenses:
        try:
            date_str = exp.get('date', '')
            date_obj = datetime.strptime(str(date_str), '%Y-%m-%d')
            month_key = date_obj.strftime('%B %Y')  # e.g., "July 2025"
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'expenses': [], 
                    'income': [], 
                    'total_expense': 0, 
                    'total_income': 0, 
                    'categories': {}
                }
            
            amount = float(exp.get('amount', 0))
            category = exp.get('category', 'Miscellaneous')
            monthly_data[month_key]['expenses'].append(exp)
            monthly_data[month_key]['total_expense'] += amount
            monthly_data[month_key]['categories'][category] = monthly_data[month_key]['categories'].get(category, 0) + amount
        except Exception as e:
            print(f"Error parsing expense: {e}")
            pass
    
    for inc in incomes:
        try:
            date_str = inc.get('date', '')
            date_obj = datetime.strptime(str(date_str), '%Y-%m-%d')
            month_key = date_obj.strftime('%B %Y')
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'expenses': [], 
                    'income': [], 
                    'total_expense': 0, 
                    'total_income': 0, 
                    'categories': {}
                }
            
            amount = float(inc.get('amount', 0))
            monthly_data[month_key]['income'].append(inc)
            monthly_data[month_key]['total_income'] += amount
        except Exception as e:
            print(f"Error parsing income: {e}")
            pass
    
    # Build month-by-month summary
    total_income = sum(float(i.get("amount", 0)) for i in incomes)
    total_expense = sum(float(e.get("amount", 0)) for e in expenses)
    
    summary = f"Overall Total: Income ₹{total_income:.2f}, Expenses ₹{total_expense:.2f}\n\n"
    summary += "Month-by-Month Breakdown:\n"
    
    for month, data in sorted(monthly_data.items(), reverse=True):
        summary += f"\n{month}:\n"
        summary += f"  Income: ₹{data['total_income']:.2f}\n"
        summary += f"  Expenses: ₹{data['total_expense']:.2f}\n"
        
        if data['categories']:
            summary += "  Spending by category:\n"
            for cat, amt in sorted(data['categories'].items(), key=lambda x: x[1], reverse=True):
                summary += f"    - {cat}: ₹{amt:.2f}\n"
    
    # Calculate overall spending percentage
    spending_ratio = (total_expense / total_income * 100) if total_income > 0 else 0
    summary += f"\nOverall spending: {spending_ratio:.1f}% of income\n"
    
    prompt = f"""Question: {user_query}

My Financial Summary:
{summary}

Answer the question directly based on my data above. Give practical advice in 2-3 clear sentences. Be specific about my spending patterns."""

    last_exc = None
    
    if OLLAMA_AVAILABLE:
        try:
            # Using llama3.2:1b - small, fast model (1.3GB)
            response = ollama.chat(
                model='llama3.2:1b',
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are FinBot, a financial assistant. Answer questions directly using the user\'s financial data. Be specific, helpful, and concise (2-3 sentences). Never add disclaimers or unnecessary warnings.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.7,
                    'num_predict': 100  # Limit response length
                }
            )
            
            # Extract only the message content, not the full response object
            if isinstance(response, dict):
                if 'message' in response and isinstance(response['message'], dict):
                    return response['message'].get('content', str(response))
                elif 'message' in response and hasattr(response['message'], 'content'):
                    return response['message'].content
            
            # If response has message attribute directly
            if hasattr(response, 'message'):
                if hasattr(response.message, 'content'):
                    return response.message.content
                elif isinstance(response.message, dict):
                    return response.message.get('content', str(response))
            
            return str(response)
            
        except Exception as e:
            print(f"Ollama call failed: {e}")
            last_exc = e

    # Local fallback summary
    try:
        # Use the same monthly_data we already calculated
        if not monthly_data:
            return "No financial data available. Please add some income or expenses to get started."
        
        parts = []
        parts.append(f"Financial Summary: Total income ₹{total_income:.2f}, total expenses ₹{total_expense:.2f}.")
        
        # Show month-by-month breakdown
        for month, data in sorted(monthly_data.items(), reverse=True)[:3]:  # Last 3 months
            parts.append(f"\n{month}: Income ₹{data['total_income']:.2f}, Expenses ₹{data['total_expense']:.2f}")
            if data['categories']:
                top_cat = max(data['categories'].items(), key=lambda x: x[1])
                parts.append(f" (Top spending: {top_cat[0]} ₹{top_cat[1]:.2f})")
        
        if total_income > 0:
            ratio = (total_expense / total_income) * 100
            parts.append(f"\n\nOverall you're spending {ratio:.1f}% of your income.")
            if ratio > 80:
                parts.append(" Recommendation: reduce discretionary spending and build an emergency fund.")
            elif ratio < 50:
                parts.append(" Nice work — your expenses are under control.")
            else:
                parts.append(" Consider reviewing recurring costs.")
        
        parts.append("\n\nNote: Ollama AI is unavailable. This is a basic summary from your data.")
        return " ".join(parts)

    except Exception:
        tb = traceback.format_exception_only(type(last_exc), last_exc) if last_exc else []
        return "FinBot is currently unavailable. Please try again later.\n" + ("".join(tb) if tb else "")

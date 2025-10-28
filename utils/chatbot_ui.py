import streamlit as st
from utils.finbot import get_budget_insights

def render_finbot_sidebar(account, user_email):
    """
    Render the FinBot chatbot in the sidebar.
    Can be called from any page.
    
    Args:
        account: Account object with access to transactions
        user_email: User's email for personalization
    """
    with st.sidebar:
        st.markdown(
            """
            <style>
            .chatbot-container {
                display: flex;
                align-items: center;
                gap: 10px;
                cursor: pointer;
                margin-bottom: 20px;
            }

            .chatbot-icon {
                background-color: #ff4b87;
                color: white;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 8px;
                font-size: 20px;
                font-weight: bold;
                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.3);
            }

            .chatbot-name {
                background-color: white;
                color: #333;
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);
            }
            </style>
            <div class="chatbot-container" onclick="document.getElementById('chat_expander').click();">
                <div class="chatbot-icon">🤖</div>
                <div class="chatbot-name">FinBot - AI Assistant</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Expander for AI Chat
        with st.expander("💬 Chat with FinBot", expanded=False):
            st.write(f"👋 Hi {user_email.split('@')[0]}! How can I help you today?")

            user_query = st.text_input("Enter your question:", key="finbot_query")

            if st.button("Send ▶", key="finbot_send"):
                if user_query.strip():
                    with st.spinner("FinBot is thinking..."):
                        transactions_text = account.format_transactions_for_ai()
                        budget_tip = get_budget_insights(user_query, transactions_text)
                        st.write(budget_tip)
                else: 
                    st.warning("Please enter a valid question.")

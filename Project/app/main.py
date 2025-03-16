import streamlit as st
import requests
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text
from streamlit.components.v1 import html


def email_quality_score(email):
    score = min(100, len(email.split()) * 2)  
    return score


def create_streamlit_app(llm, portfolio, clean_text):
    st.set_page_config(layout="wide", page_title="Cold Mail Generator", page_icon="📧")

    st.markdown(
        '''
        <div style='display: flex; align-items: center;'>
            <div style='font-size: 36px;'>📧</div>
            <div style='font-size: 32px; margin-left: 10px; font-weight: bold;'>Cold Mail Generator</div>
            <div style='margin-left: 20px;'>🌟</div> <!-- Adding a small logo/icon beside the title -->
        </div>
        ''',
        unsafe_allow_html=True
    )

    url_input = st.text_input("Enter a URL:", value="https://jobs.nike.com/job/R-33460")
    submit_button = st.button("Submit")

    st.sidebar.title("Customization Options")
    template_choice = st.sidebar.selectbox("Choose Email Template:", ["Formal", "Casual", "Technical", "Sales-Pitch"])

    if submit_button:
        try:
            loader = WebBaseLoader([url_input])
            documents = loader.load()

            if not documents:  # Check if documents list is empty
                st.error("No content found using WebBaseLoader. Trying alternative method...")
                response = requests.get(url_input)

                if response.status_code == 200:
                    data = clean_text(response.text)
                    st.success("Successfully loaded content using requests.")
                else:
                    st.error("Failed to load content. Please try a different URL.")
                    return
            else:
                data = clean_text(documents.pop().page_content)

            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)

            for job in jobs:
                skills = job.get('skills', [])
                links = portfolio.query_links(skills)
                email = llm.write_mail(job, links)
                score = email_quality_score(email)

                formatted_email = f'<div style="white-space: pre-line; word-wrap: break-word; line-height: 1.2; margin: 0; padding: 0;">{email}</div>'
                st.markdown(formatted_email, unsafe_allow_html=True)
                st.markdown(f'<h3 style="color: green;">Email Quality Score: {score}/100</h3>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    create_streamlit_app(chain, portfolio, clean_text)

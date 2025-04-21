import streamlit as st
import pandas as pd
import warnings
from scraper import get_films

warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")

st.set_page_config(page_title="Boxd Office", page_icon="🎬")

def main():
    st.title("Boxd Office")
    st.write("Visualize your Letterboxd film data!")
    
    with st.form("user_input"):
        username = st.text_input("Enter your Letterboxd username:")
        submit_button = st.form_submit_button("Start")
    
    if submit_button:
        if not username:
            st.error("Please enter a valid Letterboxd username")
            return
            
        with st.spinner("Scraping your films..."):
            try:
                films_data = get_films(username, max_threads=20)
                films_df = pd.DataFrame(films_data)
                st.success("Scraping complete!")
                
                st.subheader("Your Film Data")
                st.dataframe(films_df)
                
                csv = films_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name=f'{username}_letterboxd.csv',
                    mime='text/csv'
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
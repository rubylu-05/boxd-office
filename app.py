import streamlit as st
import pandas as pd
import warnings
from visualizations.genres.popular_genres import plot_popular_genres
from visualizations.genres.popular_themes import plot_popular_themes
from theme import ORANGE, GREEN, BLUE

warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")

st.set_page_config(page_title="Boxd Office", page_icon="🍿")

def main():
    st.markdown(f"<h1 style='font-size: 4em;'><span style='color: {ORANGE};'>Boxd</span> · <span style='color: {GREEN};'>Office</span></h1>", unsafe_allow_html=True)
    st.write("Visualize your Letterboxd film data!")

    with st.form("user_input"):
        username = st.text_input("Enter your Letterboxd username:")
        submit_button = st.form_submit_button("Start")

    if submit_button:
        if not username:
            st.error("Please enter a valid Letterboxd username")
            return

        with st.spinner("Loading your films..."):
            try:
                films_df = pd.read_csv('rubylu.csv')

                for col in ['genres', 'themes', 'cast']:
                    films_df[col] = films_df[col].apply(eval)

                st.success("Data loaded successfully!")

                st.markdown(f"<h3 style='color: {BLUE}; font-weight: bold;'>Your Film Data</h3>", unsafe_allow_html=True)
                st.dataframe(films_df)

                csv = films_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name=f'{username}_letterboxd.csv',
                    mime='text/csv'
                )

                st.markdown(f"<h2 style='color: {GREEN};'>Genres and Themes</h2>", unsafe_allow_html=True)
                st.plotly_chart(plot_popular_genres(films_df), use_container_width=True)
                st.plotly_chart(plot_popular_themes(films_df), use_container_width=True)

            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
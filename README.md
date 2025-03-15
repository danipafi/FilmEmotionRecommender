# Film Recommendation System via Reviews Sentiment Analysis

This project proposes a film recommendation engine that leverages **sentiment analysis** on Rotten Tomatoes reviews. Instead of recommending movies based solely on user behavior or film metadata, we create **emotional profiles** from critics’ reviews and suggest movies with similar emotional signatures.

**Presentation Slides**: [Click here](https://docs.google.com/presentation/d/1T9KxRNtyEIgQPMPZpFmPyfwri7n5BWvxFeQ0KHxlRPk/edit?usp=sharing)

## Overview

- **Motivation**:  
  Users are overwhelmed by too many content choices, leading to “choice paralysis.” Traditional recommendation systems often trap users in an “echo chamber” based on past behavior.  
- **Key Idea**:  
  Analyze the emotional tone (joy, sadness, anger, fear, etc.) in critics’ reviews to cluster and recommend films with similar emotional profiles.  
- **Data Source**:  
  A publicly available Rotten Tomatoes dataset (scraped in 2023), containing critic reviews and basic movie info.

## Main Steps

1. **Data Cleaning and EDA**
   Cleaned, normalized, and transformed the data, followed by Exploratory Data Analysis (EDA) to generate insights and visualizations.

2. **Sentiment Analysis**  
   Used a RoBERTa-based NLP model fine-tuned on the GoEmotions dataset (28 emotions) to score each review.

3. **Emotion Profile Creation**  
   Aggregated predicted emotions at the film level, producing an average emotional distribution per movie.

4. **Similarity Matrix**  
   Used cosine similarity on the films’ emotional vectors (with PCA for dimensionality reduction). Identified the top similar films for each title.

5. **Recommendation**  
   When a user selects a favorite movie, the system returns films with the closest emotional profile (optionally filtering by shared genres).

## How to Run (Streamlit)

1. **Clone This Repository**:
   ```bash
   git clone https://github.com/YourUsername/your-repo-name.git
   cd your-repo-name

2. **Install Dependencies (example with pip)**:
   ```bash
   pip install -r requirements.txt

Make sure your requirements.txt includes packages such as streamlit, pandas, numpy, scikit-learn, and transformers.

3. **Run the Streamlit App**:
   ```bash
   streamlit run app.py

This command opens a local browser window with the demo app.

## Future Improvements

- **Streaming APIs**: Connect to platforms like Netflix or Hulu for real-time content data.  
- **Continuous Scraping**: Keep updating the Rotten Tomatoes database beyond 2023.  
- **Additional Filters**: Exclude extremely low-rated films or refine by director, cast, etc.  
- **Enhanced Search**: Improve query handling for typos or partial matches.  
- **Standalone App**: Deploy using a more robust architecture (e.g., FastAPI for backend).

## References

- [Rotten Tomatoes Official Site](https://www.rottentomatoes.com/)
- [Hugging Face – RoBERTa-base-go_emotions](https://huggingface.co/SamLowe/roberta-base-go_emotions)
- [“Stream Fatigue” & Business Wire Surveys](https://www.businesswire.com)

## License

This project is released under the [MIT License](LICENSE).

## Contact

**Author**: Daniele Belmiro  
**Project**: Ironhack Data Analytics Bootcamp Final Project (2025)

Feel free to open [issues](https://github.com/danipafi/FilmEmotionRecommender/issues) or submit [pull requests](https://github.com/danipafi/FilmEmotionRecommender/pulls) for feedback and collaboration!

**Enjoy discovering new films through a more emotionally aligned recommendation system!**

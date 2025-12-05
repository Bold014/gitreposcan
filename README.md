# VC Sourcing Engine

An automated tool for Venture Capitalists and investors to discover high-velocity open source repositories on GitHub. This dashboard identifies trending technologies by analyzing star growth velocity rather than just total stars.

## Features

- **Velocity Tracking**: Calculates the number of new stars in the last 7 days to find "breakout" repos.
- **Automated Classification**: Categorizes repos into "Breakout" (>50 stars/week), "Growing" (>10 stars/week), and "Early".
- **Thesis-Driven Search**: Presets for popular investment themes like Generative AI, Autonomous Agents, Rust, DeFi, etc.
- **Visual Analytics**: Interactive charts showing growth distribution and velocity leaders.

## Live Demo

[Link to Streamlit App] *(You will generate this link after deploying)*

## How to Run Locally

1.  **Clone the repository**
    ```bash
    git clone https://github.com/YOUR_USERNAME/vc-sourcing-engine.git
    cd vc-sourcing-engine
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure GitHub Token**
    Create a file `.streamlit/secrets.toml` and add your GitHub Personal Access Token to avoid rate limits:
    ```toml
    GITHUB_TOKEN = "your_github_token_here"
    ```

4.  **Run the App**
    ```bash
    streamlit run app.py
    ```

## Deployment

This app is designed to be deployed on **Streamlit Cloud**:
1.  Push code to GitHub.
2.  Connect your repo on [share.streamlit.io](https://share.streamlit.io/).
3.  Add your `GITHUB_TOKEN` in the App Settings > Secrets.


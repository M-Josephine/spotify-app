# Pimp my track

Pimp My Track is a web application that generates personalized music recommendations based on a user's Spotify listening history and their chosen audio features.

**Architecture**

The application is built on a serverless architecture to ensure scalability and ease of deployment. 

The core components are:

**Frontend**: A Streamlit application built with Python provides the user interface and handles all the business logic. It uses the Spotipy library to interact with the Spotify API and the Reccobeats API for recommendation generation.

https://developer.spotify.com/documentation/web-api 
https://reccobeats.com/

**Authentication**: The app uses the OAuth 2.0 protocol to authenticate each user, ensuring they can access and interact with their own Spotify data in a secure, private, and personalized session.

**Containerization**: The entire application is packaged into a Docker image, guaranteeing a consistent and portable environment.

**Deployment**: The Docker container is deployed on Google Cloud Run, a managed platform that automatically handles infrastructure, scaling, and public access. The Cloud Run URL is then mapped to a custom domain name for easier access. This domain is hosted on OVHcloud as https://portfolio-mjo.com.


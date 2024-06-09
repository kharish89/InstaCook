# InstaCook

This document provides an overview of the data flow for our web application, InstaCook, which processes a recipe video URL input to generate and return the instructions and ingredient list to the user interface (UI).

## Table of Contents
- [Introduction](#introduction)
- [Data Flow Steps](#data-flow-steps)
- [Flowchart](#flowchart)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction

InstaCook takes a video URL input from the user, extracts the audio, transcribes it, processes the transcription with Groq to generate a JSON response, and sends this JSON to the Instacart API. The API returns an ingredient list that is displayed in the UI.

## Data Flow Steps

1. **UI**: The user provides a video URL through the application's UI.
2. **Audio Extraction**: The audio from the provided video URL is extracted.
3. **Whisper Speech to Text/Transcription**: The extracted audio is transcribed into text using Whisper.
4. **Groq Processing**: The transcribed text is processed using Groq to extract instructions and ingredients into a JSON format.
5. **Send to Instacart API**: The JSON object is sent to the Instacart API (pending approval).
6. **Return Ingredient List to UI**: The Instacart API processes the JSON and returns an ingredient list.
7. **UI**: The returned ingredient list is displayed back in the UI for the user.

## Flowchart

```mermaid
flowchart TD
    A[UI] -->|User Inputs Video URL| B[Audio Extraction]
    B --> C[Whisper Speech to Text/Transcription]
    C --> D[Groq converts instructions and ingredients into JSON format]
    D --> E[Send to Instacart API]
    E --> F[Return Instacart Recipe Page]
    F --> A[UI]
```

## Technologies Used

## Installation

1. Create a new conda environment using

```bash
conda create -n insta-cook python=3.11
```

2. Activate the conda environment

```bash
conda activate insta-cook
```

3. Install the requiered python modules using

```bash
pip install -r requirements.txt
```

4. Run the python script

```bash
python yt_instacart_recipie.py
```
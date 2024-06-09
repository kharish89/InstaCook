import yt_dlp
import gradio as gr
from groq import Groq
import os
import ffmpeg
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# accept a youtube url as input
url = gr.Textbox(label="Cooking recipe Youtube URL")

# Download hook for youtube-dlp to extract filename
def download_hook(d):
    if d['status'] == 'finished':
        filename = d['filename']
        global OUTPUT_FILE_NAME
        OUTPUT_FILE_NAME = filename

# download the audio
def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        "restrictfilenames": True,
        "outtmpl": "%(title)s",
        # "trim_file_name": True,
        "progress_hooks": [download_hook],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '16000',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # info = ydl.extract_info(url, download=False)
        ydl.download([url])
    
# convert the audio to wav with 16khz sample rate using ffmpeg
def convert_to_wav(filename):
    filename = OUTPUT_FILE_NAME + ".wav"
    output_filename = OUTPUT_FILE_NAME
    ffmpeg.input(filename).output(output_filename, format="wav", ac=1, ar='16k').run()
    return output_filename

# transcribe the audio
def transcribe(input_audio):
    """
    Transcribes using Whisper (https://github.com/openai/whisper)
    until groq enables this speech to text api for public
    """
    transcriber = pipeline(model="openai/whisper-base")
    transcript = transcriber(input_audio)["text"]
    return transcript

# get the transcribed text to groq client and get a instacart api response
def instacartRecipeAPI(text):
    """
    Generate the instacart recipe request using Llama or mixtral models.
    llama3-70b-8192
    mixtral-8x7b-32768
    """
    if text != "":
        response = groq_client.chat.completions.create(
            response_format={ "type": "json_object" },
            model='llama3-70b-8192',
            messages=[
                {"role": "system", "content": """
                       You are a shopping list creator who will take a full audio transcript of the recipe and extract shopping list for the recipe and the short instruction. You will only output valid 'JSON'.
                        Output only json in the below format
                        ----- output format json
                        ``{
                        "title": "Small Chocolate Cake (6 inches)",
                        "image_url": "https://d3s8tbcesxr4jm.cloudfront.net/recipe-images/v3/small-chocolate-cake-6-inches/0_medium.jpg",
                        "link_type": "recipe",
                        "instructions": [
                            "Preheat the oven to 350 degrees F and grease a 6-inch round cake pan.",
                            "In a large bowl, combine flour, sugar, cocoa, baking powder, baking soda, salt, and cinnamon.",
                            "Add egg, milk, oil, and vanilla to dry ingredients and mix well.",
                            "Gradually add boiling water, mixing continuously until the batter is smooth.",
                            "Pour the batter in the prepared cake pan and bake for 30-35 minutes, or until a toothpick comes out clean.",
                            "Let the cake cool in the pan for 10 minutes, then remove from the pan and let cool completely on a wire rack.",
                            "To prepare the frosting, melt the butter in a small saucepan.",
                            "Stir in the cocoa and remove the saucepan from heat.",
                            "Gradually add powdered sugar and milk, stirring until you reach your desired consistency. Stir in the vanilla.",
                            "Wait until the cake is cooled completely to frost it."
                        ],
                        "ingredients": [
                            {
                            "name": "whole milk",
                            "quantity": 0.5,
                            "unit": "cup"
                            },
                            {
                            "name": "eggs",
                            "quantity": 1,
                            "unit": "large"
                            },
                            {
                            "name": "ground cinnamon",
                            "quantity": 0.25,
                            "unit": "teaspoon"
                            },
                            {
                            "name": "salt",
                            "quantity": 0.25,
                            "unit": "cup"
                            },
                            {
                            "name": "baking powder",
                            "quantity": 1,
                            "unit": "teaspoon"
                            },
                            {
                            "name": "unsalted butter",
                            "quantity": 0.25,
                            "unit": "cup"
                            },
                            {
                            "name": "unsweetened cocoa powder",
                            "quantity": 0.25,
                            "unit": "cup"
                            },
                            {
                            "name": "powdered sugar",
                            "quantity": 1,
                            "unit": "cup"
                            },
                            {
                            "name": "evaporated milk",
                            "quantity": 1,
                            "unit": "tablespoon"
                            },
                            {
                            "name": "vanilla extract",
                            "quantity": 0.5,
                            "unit": "teaspoon"
                            },
                            {
                            "name": "boiling water",
                            "quantity": 0.5,
                            "unit": "cup"
                            },
                            {
                            "name": "vegetable oil",
                            "quantity": 0.25,
                            "unit": "cup"
                            },
                            {
                            "name": "all-purpose flour",
                            "quantity": 1,
                            "unit": "cup"
                            }
                        ],
                        "landing_page_configuration": {
                            "partner_linkback_url": "string",
                            "enable_pantry_items": true
                        }
                        }``"""
                        },
                      {"role": "user", "content": text}]
            )
            
        return response.choices[0].message.content

# Download the audio and convert it to wav
def process_instacart_recipe(url):
    
    # Download and extract audio from youtube video
    download_audio(url)
    
    # Convert the audio to wav with 16khz sample rate using ffmpeg
    converted_audio_filename = convert_to_wav(OUTPUT_FILE_NAME + ".wav")
    
    # Transcribe the audio using Whisper
    transcript = transcribe(converted_audio_filename)
    
    # Get the transcribed text to groq client and get a instacart recipe api request
    instacart_api_request = instacartRecipeAPI(transcript)
    
    return instacart_api_request
    
# create a gradio interface
demo = gr.Interface(inputs=url, outputs="text", fn=process_instacart_recipe, title="Instacart Recipe from Youtube Video")

# launch the demo
demo.launch()

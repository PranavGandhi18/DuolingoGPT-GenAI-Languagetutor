import streamlit as st
import requests
import numpy as np
from audio_recorder_streamlit import audio_recorder
import io
import openai
from . import config
from openai import OpenAI
client = OpenAI(api_key=config.API_KEY)



def speech_to_text(file_path):
    audio_file= open(file_path, "rb")
    transcription = client.audio.transcriptions.create(
      model="whisper-1",
      file=audio_file
    )
    print("transcript:")
    print(transcription.text)
    return transcription.text



def describe_image(image_url):
    response = client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {
          "role": "user",
          "content": [
            {"type": "text", "text": "describe this image like an IELTS exam"},
            {
              "type": "image_url",
              "image_url": {
                "url": image_url,
              },
            },
          ],
        }
      ],
      max_tokens=300,
    )
    print("Chat GPT:")
    print(response.choices[0].message.content)
    return response.choices[0].message.content



def compare_descriptions(model_desc, user_desc):
    st.write(f" Description: {model_desc}")
    st.write(f"Your Description: {user_desc}")
    completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
      {"role": "system", "content": "You are a language teacher. you have a predefined description of an image, and also a user written dscription. you just have to judge the language, grammer and vocabolary of the user provided description. keep in mind that the user is a beginner so be supportive and helpful."},
      {"role": "user", "content": f"Description: {model_desc},user Description: {user_desc}. based on these two respond what all the user can improve in their description of the image "}
      ]
    )

    print(completion.choices[0].message.content)
    st.subheader('Feedback')
    st.write(f"Analysis: {completion.choices[0].message.content.strip()}")


def app():
    # Embed the Lottie animation using an iframe
    st.markdown(
        """
        <iframe src="https://lottie.host/embed/fc8b428c-a3e9-4a2c-a2f6-c5cdad5fba55/b5RNl8YODi.json"
        style="width: 200px; height: 200px; border:none;" allowfullscreen></iframe>
        
        """,
        unsafe_allow_html=True
    )
    st.header('Image Comprehension')
    st.write('Learn to understand and describe images in your target language. This task focuses on improving your speaking skills and vocabulary.')
    

    if 'image_shown' not in st.session_state:
        st.session_state.image_shown = False
    if 'recording_started' not in st.session_state:
        st.session_state.recording_started = False

    # Start button to display the image
    if st.button('Start'):
        st.session_state.image_shown = True
        st.session_state.image_generated = False

    if st.session_state.image_shown:
        # Display the image
        print(st.session_state.image_generated)
        if st.session_state.image_generated == False:
            url = f"https://picsum.photos/1280/720"
            response = requests.get(url)
            image_url = response.url
            st.session_state.image_url=image_url
            st.session_state.image_generated = True
            print(st.session_state.image_generated)
        st.image(st.session_state.image_url, caption='Describe this image.')
        st.subheader('You have to describe and talk about what you see in the image. Take your time to look and analyse the image. Think about what you want to say and then start.\n You will have 30 seconds to speak about it. Focus on rich decription fluid speech.')

        #Capture audio from the user for 30 seconds
        audio_bytes = audio_recorder(energy_threshold=(-1.0, 1.0),pause_threshold=30.0)
       
        if audio_bytes:
            output_file = "output2.wav"
            with open(output_file, "wb") as f:
                f.write(audio_bytes)
                

            print(f"Audio saved to {output_file}")
            user_description = speech_to_text(output_file)

            model_description = describe_image(st.session_state.image_url)
            compare_descriptions(model_description, user_description)

  


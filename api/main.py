from fastapi import FastAPI,UploadFile,File,Form,Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
import azure.cognitiveservices.speech as speechsdk
import speech_recognition as sr
import moviepy.editor as mp
from pydantic import BaseModel
import tempfile
import gtts as gt
import uvicorn
import tempfile
import aiofiles
import pyttsx3
import pydub
import os


from dotenv import load_dotenv

load_dotenv()
AZURE_SPEECH_KEY = os.getenv('AZURE_SPEECH_KEY')
AZURE_SPEECH_REGION = os.getenv('AZURE_SPEECH_REGION')
WIT_AI_KEY = os.getenv('WIT_AI_KEY')
WIT_AI_KEY_SPANISH = os.getenv('WIT_AI_KEY_SPANISH')
HOUNDIFY_CLIENT_ID = os.getenv('HOUNDIFY_CLIENT_ID')
HOUNDIFY_CLIENT_KEY = os.getenv('HOUNDIFY_CLIENT_KEY')

app = FastAPI()
ffmpeg_path = "C:/Program Files/ffmpeg/bin/ffmpeg.exe"
os.environ["FFMPEG_PATH"]= ffmpeg_path
# Specify the allowed origins for CORS
origins = [
    "http://127.0.0.1:3000",  #  URL of your front-end
    "http://127.0.0.1:2000",  #  URL of your front-end
    "http://127.0.0.1:1000",  #  URL of your front-end
]

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/recognize_speech")
async def upload_audio(
    audio: UploadFile = File(...),
    language: str = Form(...)):

    # Create a temporary file to store the uploaded audio
    with tempfile.NamedTemporaryFile(delete=False) as temp_audio:
        temp_audio_path = temp_audio.name
        async with aiofiles.open(temp_audio_path, "wb") as temp_file:
            while chunk := await audio.read(1024):
                await temp_file.write(chunk)

        # Convert the temporary audio file to WAV
        wav_file_path = temp_audio_path + ".wav"
        convert_webm_to_wav(temp_audio_path, wav_file_path)

        # Recognize speech from the WAV file
        recognized_text = await perform_speech_recognition(wav_file_path,language)

        # Return the recognized text or perform additional actions
        return {"recognized_text": recognized_text}

def convert_webm_to_wav(input_file_path, output_file_path):
    # Load the webm file using pydub
    audio = pydub.AudioSegment.from_file(input_file_path, format='webm')

    # Set the sample width to 2 bytes (16-bit)
    audio = audio.set_sample_width(2)

    # Set the number of channels to mono
    audio = audio.set_channels(1)

    # Set the sample rate to 16kHz
    audio = audio.set_frame_rate(16000)

    # Export the audio as a WAV file
    audio.export(output_file_path, format='wav')

async def perform_speech_recognition(wav_file_path,language):
    r = sr.Recognizer()

    # Load the WAV file as audio data
    with sr.AudioFile(wav_file_path) as audio_file:
        audio = r.record(audio_file)

    recognized_text = ""

    if language == "english":
        recognized_text += '\n'
        try:
            recognized_text += "sphinx: "
            recognized_text += r.recognize_sphinx(audio)+ "   "
        except sr.UnknownValueError:
            recognized_text = "Sphinx could not understand audio"
        except sr.RequestError as e:
            recognized_text = "Sphinx error: {0}".format(e)
        recognized_text += '\n'
        try:
            recognized_text += "google: "
            recognized_text += r.recognize_google(audio) + "   "
        except sr.UnknownValueError:
            recognized_text = "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            recognized_text = "Could not request results from Google Speech Recognition service: {0}".format(e)
        recognized_text += '\n'
        try:
            recognized_text += "wit: "
            recognized_text += r.recognize_wit(audio, key=WIT_AI_KEY) + "  "
        except sr.UnknownValueError:
            recognized_text += "Wit.ai could not understand audio   "
        except sr.RequestError as e:
            recognized_text += "Could not request results from Wit.ai service: {0}   ".format(e)
        recognized_text += '\n'
        try:
            recognized_text += "houndify: "
            recognized_text += r.recognize_houndify(audio, client_id=HOUNDIFY_CLIENT_ID, client_key=HOUNDIFY_CLIENT_KEY)[0]+ "   "
        except sr.UnknownValueError:
            recognized_text += "Houndify could not understand audio   "
        except sr.RequestError as e:
            recognized_text += "Could not request results from Houndify service: {0}   ".format(e)
        recognized_text += '\n'
        try:
            recognized_text += "whisper: "
            recognized_text += r.recognize_whisper(audio, language='english') + "   "
        except sr.UnknownValueError:
            recognized_text += "Whisper could not understand audio   "
        except sr.RequestError as e:
            recognized_text += "Whisper error: {0}".format(e)
        recognized_text += '\n'
        try:
            recognized_text += "whisper small: "
            recognized_text += r.recognize_whisper(audio, language='english',model = "small") + "   "
        except sr.UnknownValueError:
            recognized_text += "Whisper could not understand audio"
        except sr.RequestError as e:
            recognized_text += "Whisper error: {0}".format(e)
        recognized_text += '\n'
        # Microsoft Azure Speech
        recognized_text += "Azure: "
        try:
                recognized_text += str(r.recognize_azure(audio, key=AZURE_SPEECH_KEY,language='es-ES',location=AZURE_SPEECH_REGION)[0])+ "   "
        except sr.UnknownValueError:
            recognized_text += "Microsoft Azure Speech could not understand audio"
        except sr.RequestError as e:
            recognized_text += ("Could not request results from Microsoft Azure Speech service; {0}".format(e))

        

    elif language == "spanish":
        recognized_text += '\n'
        try:
            recognized_text += "google: "
            recognized_text += r.recognize_google(audio, language="es-ES") + "   "
        except sr.UnknownValueError:
            recognized_text += "Google Speech Recognition could not understand audio"
        except sr.RequestError as e:
            recognized_text += "Could not request results from Google Speech Recognition service: {0}".format(e)
        recognized_text += '\n'
        try:
            recognized_text += "wit: "
            recognized_text += r.recognize_wit(audio, key=WIT_AI_KEY_SPANISH)  + "   "
        except sr.UnknownValueError:
            recognized_text += "Wit.ai could not understand audio"
        except sr.RequestError as e:
            recognized_text += "Could not request results from Wit.ai service: {0}".format(e)
        recognized_text += '\n'
        try:
            recognized_text += "Whisper: "
            recognized_text += r.recognize_whisper(audio, language='spanish') + "   "
        except sr.UnknownValueError:
            recognized_text += "Whisper could not understand audio"
        except sr.RequestError as e:
            recognized_text += "Whisper error: {0}".format(e)
        recognized_text += '\n'
        try:
            recognized_text += "Whisper small: "
            recognized_text += r.recognize_whisper(audio, language='spanish',model = "small") + "   "
        except sr.UnknownValueError:
            recognized_text += "Whisper could not understand audio"
        except sr.RequestError as e:
            recognized_text += "Whisper error: {0}".format(e)
        recognized_text += '\n'
    
        # Microsoft Azure Speech
        recognized_text += "Azure: "
        try:
                recognized_text += str(r.recognize_azure(audio, key=AZURE_SPEECH_KEY,language='es-ES',location=AZURE_SPEECH_REGION)[0]) + "   "
        except sr.UnknownValueError:
            recognized_text +=("Microsoft Azure Speech could not understand audio")
        except sr.RequestError as e:
            recognized_text += ("Could not request results from Microsoft Azure Speech service; {0}".format(e))
        
    

    return {"recognized_text": recognized_text}



class TextToSpeechRequest(BaseModel):
    text: str
    language: str
@app.post("/text-to-speech")
async def convert_text_to_speech(request: TextToSpeechRequest):
    
    audio_file = text_to_speech_function(request.text, request.language)
    response = Response(content=audio_file, media_type="audio/mpeg")
    response.headers["Content-Disposition"] = 'attachment; filename="audio_file.mp3"'
    return response


def text_to_speech_function(text, language):
    audio_clip_paths = []
    if(language == 'english'):
        language = 'en-US'
    elif(language == 'spanish'):
        language = 'es-ES'


    # Create a temporary file with .mp3 extension
    temp_file_path_gtts = tempfile.NamedTemporaryFile(suffix=".mp3", prefix="temp_audio_",delete=False).name
    temp_file_path_pytts = tempfile.NamedTemporaryFile(suffix=".mp3", prefix="temp_audio_",delete=False).name
    temp_file_path_Azure = tempfile.NamedTemporaryFile(suffix=".mp3", prefix="temp_audio_",delete=False).name
    temp_file_output = tempfile.NamedTemporaryFile(suffix=".mp3", prefix="temp_audio_",delete=False).name
    
    # os.close(temp_file_handle)
    
    t2s = gt.gTTS("gtts: "+text, lang=language)
    t2s.save(temp_file_path_gtts)
    audio_clip_paths.append(temp_file_path_gtts)
        # Read the contents of the temporary file
    if language == 'en-US':
        engine = pyttsx3.init()
        rate = engine.getProperty('rate')   # getting details of current speaking rate
        engine.setProperty('rate', 125)     # setting up new voice rate
        """VOLUME"""
        volume = engine.getProperty('volume')   #getting to know current volume level (min=0 and max=1)
        engine.setProperty('volume',1.0)    # setting up volume level  between 0 and 1
        """VOICE"""
        voices = engine.getProperty('voices')    
        engine.setProperty('voice', voices[1].id)  #changing index, changes voices. o for male
        #  Save the audio to a BytesIO object
        # engine.save_to_file(text,temp_file_path)  
        engine.save_to_file("pytts: "+text,temp_file_path_pytts)
        engine.runAndWait()
        audio_clip_paths.append(temp_file_path_pytts)

    speech_key, service_region = AZURE_SPEECH_KEY, AZURE_SPEECH_REGION
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)

    speech_config.speech_synthesis_language = language
    if language == 'en-US':
        voice = "Microsoft Server Speech Text to Speech Voice (en-US, JennyNeural)"
    else:
        voice = 'Microsoft Server Speech Text to Speech Voice (es-ES, EliasNeural)'
    
    speech_config.speech_synthesis_voice_name = voice
    file_config = speechsdk.audio.AudioOutputConfig(filename=temp_file_path_Azure,use_default_speaker= True)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)
    result = speech_synthesizer.speak_text_async("azure: "+text).get()

    audio_clip_paths.append(temp_file_path_Azure)
    output_path = temp_file_output
    concatenate_audio_moviepy(audio_clip_paths, output_path)
    with open(output_path, 'rb') as file:
        audio_data_complete = file.read()   


    return audio_data_complete
def concatenate_audio_moviepy(audio_clip_paths, output_path):
    """Concatenates several audio files into one audio file using MoviePy
    and save it to `output_path`. Note that extension (mp3, etc.) must be added to `output_path`"""
    clips = [mp.AudioFileClip(c) for c in audio_clip_paths]
    final_clip = mp.concatenate_audioclips(clips)
    final_clip.write_audiofile(output_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv
import wave
from google import genai
from google.genai import types
import serial
import numpy as np
from playsound import playsound
import os
import pyttsx3
tts = pyttsx3.init()
tts.setProperty('rate', 150)
tts.setProperty('volume', 1)
arduino = serial.Serial(port="COM10")

def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)

def gerar(caminho_do_arquivo):        
    print("Gerando resposta...")
    client = genai.Client(
    api_key="AIzaSyDtQrX-QXuTs0-60-Az3OpZk8GlgEX9AIU",
    )

    generate_content_config = types.GenerateContentConfig(
        system_instruction="Seu nome é hermes. Não precisa dizer caso não seja requisitado.\nResponda aos áudios, em português. O conteúdo deles.",
        response_mime_type="text/plain",
    )

    arquivo = client.files.upload(file=caminho_do_arquivo)
    resposta = client.models.generate_content(
        model="gemini-2.5-flash-preview-05-20",
        contents=[arquivo, "Responda ao conteúdo do áudio. Os áudios serão enviados em português."],
        config=generate_content_config
    )

    texto = resposta.text
    
    tts.say(texto)
    tts.runAndWait()
    print("ACABOU!")
buffer = []
def callback(indata, _, __, ___):
    buffer.append(indata.copy())

comando_real = ""
frequencia=44100
gravacao = sd.InputStream(samplerate=frequencia, channels=2, callback=callback)
gravou = False
while True:
    comando = arduino.readline().decode("utf-8").strip("\n").strip()
    if (comando != comando_real):
        comando_real = comando
        match comando:
            case "OUVIR":
                buffer = []
                gravacao = sd.InputStream(samplerate=frequencia, channels=2, callback=callback)
                gravacao.start()
                gravou = True
            case "PROCESSAR":
                if gravou:
                    print("PROCESSANDO")
                    gravacao.stop()
                    audio = np.concatenate(buffer, axis=0)
                    write("output.wav", frequencia, audio.astype(np.float32))
                    gerar("./output.wav")
                    gravou = False
import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

def on_publish(client, userdata, result):
    print("Mensaje enviado correctamente")

def on_message(client, userdata, message):
    global message_received
    time.sleep(1)
    message_received = str(message.payload.decode("utf-8"))
    st.markdown(f"<div class='mensaje'>{message_received}</div>", unsafe_allow_html=True)

broker = "157.230.214.127"
port = 1883
client1 = paho.Client("VOICE-CLIENT")
client1.on_message = on_message

st.markdown("""
    <style>
        .stApp {
            background-color: #e0f2f1;
            font-family: 'Segoe UI', sans-serif;
        }
        h1, h2, h3, p {
            color: #004d40;
            text-align: center;
        }
        .stButton>button {
            background-color: #00796b;
            color: white;
            border-radius: 8px;
            padding: 0.4em 1.2em;
            border: none;
            font-weight: 500;
        }
        .stButton>button:hover {
            background-color: #004d40;
        }
        .caja {
            background-color: #ffffff;
            border-left: 4px solid #00796b;
            padding: 1.5em;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-top: 1em;
        }
        .mensaje {
            background-color: #b2dfdb;
            padding: 0.8em;
            border-radius: 8px;
            text-align: center;
            font-weight: 500;
            color: #00332e;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>Sistema de Control de Voz</h1>", unsafe_allow_html=True)
st.markdown("<h3>Interacción mediante audio</h3>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    image = Image.open("voz.png")
    st.image(image, use_container_width=True)

with col2:
    st.markdown("<div class='caja'>", unsafe_allow_html=True)
    st.markdown("<p>Presiona el botón y habla claramente</p>", unsafe_allow_html=True)

    stt_button = Button(label="Iniciar Reconocimiento", width=240)

    stt_button.js_on_event("button_click", CustomJS(code="""
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onresult = function (e) {
            var value = "";
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                }
            }
            if (value != "") {
                document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
            }
        }
        recognition.start();
    """))

    result = streamlit_bokeh_events(
        stt_button,
        events="GET_TEXT",
        key="speech_control",
        refresh_on_update=False,
        override_height=75,
        debounce_time=0
    )

    st.markdown("</div>", unsafe_allow_html=True)

if result and "GET_TEXT" in result:
    text_result = result.get("GET_TEXT")
    st.markdown(f"<div class='mensaje'>{text_result}</div>", unsafe_allow_html=True)
    client1.on_publish = on_publish
    client1.connect(broker, port)
    message = json.dumps({"Act1": text_result.strip()})
    ret = client1.publish("voice_ctrl", message)

    try:
        os.mkdir("temp")
    except:
        pass

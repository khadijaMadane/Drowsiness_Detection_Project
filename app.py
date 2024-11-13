import streamlit as st

class State:
    START_DETECTION = "start_detection"
    MAIN = "main"
 


def main():
    # Conteneur principal avec disposition en ligne
    col1, col2, col3 = st.columns([2, 1, 3])

    # Colonne pour l'image
    with col1:
        st.image("sol-removebg-preview.png", width=400, caption="")
    with col2:
        st.empty()
    # Colonne pour l'interface utilisateur principale
    with col3:
        st.title("Détection de Somnolence en Temps Réel")
        st.write("Bienvenue dans l'application de détection de somnolence en temps réel.")
        st.write("Cliquez sur le bouton ci-dessous pour démarrer la détection.")

        # Bouton pour démarrer la détection
        if st.button("Démarrer la détection"):
            # Changer l'état de l'application
            st.session_state.state = State.START_DETECTION


def start_detection():
    import cv2
    import numpy as np
    import pygame
    from tensorflow.keras.models import load_model

    # Charger le modèle entraîné
    model = load_model('Model.h5')

    # Charger les classificateurs en cascade
    face_cascade = cv2.CascadeClassifier('haarcascade/haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('haarcascade/haarcascade_eye.xml')

    # Configuration de la capture vidéo
    cap = cv2.VideoCapture(0)

    # Initialisation des variables
    Score = 0
    alert_displayed = False

    # Charger le son de l'alarme
    pygame.mixer.init()
    alarm_sound = pygame.mixer.Sound('Réveillez.ogg')

    # Placeholder pour l'image finale
    output_frame = st.empty()

    # Add video stream to the sidebar
    video_placeholder = st.sidebar.empty()
    video_placeholder.image([], channels='BGR', use_column_width=True)

    # Add buttons to the sidebar
    with st.sidebar:
        st.markdown('## Controls')
        start_button = st.button('Démarrer', key='start_button', help='Cliquer pour démarrer la détection')
        stop_button = st.button('Arrêter', key='stop_button', help='Cliquer pour arrêter la détection')

    while st.session_state.state == State.START_DETECTION:
        ret, frame = cap.read()
        height, width = frame.shape[0:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
        eyes = eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=1)

        cv2.rectangle(frame, (0, height-50), (200, height), (0, 0, 0), thickness=cv2.FILLED)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, pt1=(x, y), pt2=(x+w, y+h), color=(255, 0, 0), thickness=3)

        for (ex, ey, ew, eh) in eyes:
            eye = frame[ey:ey+eh, ex:ex+ew]
            eye = cv2.resize(eye, (146, 146))
            eye = eye / 255
            eye = eye.reshape(146, 146, 3)
            eye = np.expand_dims(eye, axis=0)

            prediction = model.predict(eye)

            if prediction[0][0] > 0.30:
                cv2.putText(frame, 'fermé', (10, height-20), fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL, fontScale=1, color=(255, 255, 255),
                            thickness=1, lineType=cv2.LINE_AA)
                Score += 1
                if Score > 15 and not alert_displayed:
                    st.warning("Les yeux sont fermés !")
                    # Jouer l'alarme
                    if not pygame.mixer.get_busy():
                        alarm_sound.play()
                    alert_displayed = True

            elif prediction[0][1] > 0.90:
                cv2.putText(frame, 'ouverts', (10, height-20), fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL, fontScale=1, color=(255, 255, 255),
                            thickness=1, lineType=cv2.LINE_AA)
                Score -= 2
                if Score < 0:
                    Score = 0
                if alert_displayed:
                    st.warning("")
                    # Arrêter l'alarme
                    alarm_sound.stop()
                    alert_displayed = False

        # Mettre à jour l'image de sortie avec le frame traité
        output_frame.image(frame, channels='BGR', use_column_width=True)

        if stop_button:
            st.session_state.state = State.MAIN

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
  

    if "state" not in st.session_state:
        st.session_state.state = State.MAIN

    if st.session_state.state == State.MAIN:
        main()
    elif st.session_state.state == State.START_DETECTION:
        start_detection()

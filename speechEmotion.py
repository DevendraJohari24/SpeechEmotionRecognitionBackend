#-----------------LIBRARIES --------------------

from tensorflow import keras
import os
import pandas as pd
import numpy as np
from pydub import AudioSegment, effects
import librosa
import random
import noisereduce as nr
# -------------------------------------------------

def augumentatedAudio(rawsound, sr, max_len_audio=314818):
    normalizedsound = effects.normalize(rawsound, headroom = 5.0) 
    normal_x = np.array(normalizedsound.get_array_of_samples(), dtype = 'float32')
    xt, index = librosa.effects.trim(normal_x, top_db = 30)
    padded_x = np.pad(xt, (0, max_len_audio - len(xt)), 'constant')
    final_x = nr.reduce_noise(y=padded_x, 
                          y_noise=padded_x, 
                          sr=sr)
    return final_x

def predictLSTM(rawsound, sr, model, frame_length=2048, hop_length=512):
    test_rms = []
    test_mfcc = []
    test_zcr = []
    final_x = augumentatedAudio(rawsound=rawsound, sr=sr)
    f1 = librosa.feature.rms(y=final_x, frame_length=frame_length, hop_length=hop_length) # Energy - Root Mean Square (RMS)

    f2 = librosa.feature.zero_crossing_rate(y=final_x, frame_length=frame_length, hop_length=hop_length) # Zero Crossed Rate (ZCR)

    f3 = librosa.feature.mfcc(y=final_x, sr=sr, S=None, n_mfcc=13, hop_length = hop_length) # MFCCs
    
    test_rms.append(f1)
    test_zcr.append(f2)
    test_mfcc.append(f3)
    
    t_f_rms = np.asarray(test_rms).astype('float32')
    t_f_rms = np.swapaxes(t_f_rms,1,2)
    t_f_zcr = np.asarray(test_zcr).astype('float32')
    t_f_zcr = np.swapaxes(t_f_zcr,1,2)
    t_f_mfccs = np.asarray(test_mfcc).astype('float32')
    t_f_mfccs = np.swapaxes(t_f_mfccs,1,2)
    
    test_dim = np.concatenate((t_f_zcr, t_f_rms, t_f_mfccs), axis=2)
    predict_test = model.predict(test_dim)
    y_pred = np.argmax(predict_test, axis=1)
    y_pred = pd.Series(y_pred)
    y_pred.replace({0:'happy', 1:'sad', 2:'angry', 3:'fear', 4:'disgust', 5:'neutral', 6:'surprise', 7:'calm'}, inplace=True)
    return y_pred[0]


def getImageUrl(emotion):
    emotionImageUrl = ''
    happyImages = [
        "https://img.freepik.com/free-photo/assortment-with-happy-emotion_23-2148860256.jpg",
        "https://img.freepik.com/free-photo/volumetric-smiling-emoticon-blurred-background-generative-ai_169016-29775.jpg"
    ]

    sadImages = [
        "https://img.freepik.com/free-photo/sad-balloon-with-copy-space-blue-monday_23-2148756213.jpg",
        "https://img.freepik.com/free-photo/sad-cute-girl-sulking-feeling-regret-looking-upper-left-corner_1258-19090.jpg",
    ]

    angryImages = [
        "https://img.freepik.com/free-photo/offended-angry-woman-cross-hands-chest-frowning-sulking-insulted-standing-beige-background_1258-87274.jpg"
    ]

    fearImages = [
        "i0.wp.com/post.medicalnewstoday.com/wp-content/uploads/sites/3/2021/10/Dissecting_terror_GettyImages763291217_Header-1024x575.jpg",
    ]

    disgustImages = [
                "https://img.freepik.com/free-photo/offended-angry-woman-cross-hands-chest-frowning-sulking-insulted-standing-beige-background_1258-87274.jpg"

    ]

    neutralImages = [
        "https://img.freepik.com/free-photo/offended-angry-woman-cross-hands-chest-frowning-sulking-insulted-standing-beige-background_1258-87274.jpg"

    ]

    surpriseImages = [
        "https://img.freepik.com/free-photo/offended-angry-woman-cross-hands-chest-frowning-sulking-insulted-standing-beige-background_1258-87274.jpg"

    ]

    calmImages = [
        "https://img.freepik.com/free-photo/offended-angry-woman-cross-hands-chest-frowning-sulking-insulted-standing-beige-background_1258-87274.jpg"

    ]
    if emotion == 'happy':
        emotionImageUrl = random.choice(happyImages)
    elif emotion == 'sad':
        emotionImageUrl = random.choice(sadImages)
    elif emotion == 'angry':
        emotionImageUrl = random.choice(angryImages)
    elif emotion == 'fear':
        emotionImageUrl = random.choice(fearImages)
    elif emotion == 'disgust':
        emotionImageUrl = random.choice(disgustImages)
    elif emotion == 'neutral':
        emotionImageUrl = random.choice(neutralImages)
    elif emotion == 'surprise':
        emotionImageUrl = random.choice(surpriseImages)
    elif emotion == 'calm':
        emotionImageUrl = random.choice(calmImages)
    return emotionImageUrl

def predictEmotion(path):
    rawsound = AudioSegment.from_file(path)
    x, sr = librosa.load(path, sr = None)
    model_path = os.path.join(os.getcwd(), "LSTM_SpeechRecognition")
    model = keras.models.load_model(model_path)
    emotion = predictLSTM(rawsound=rawsound, sr=sr, model=model)
    return emotion

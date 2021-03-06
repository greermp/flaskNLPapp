# load Flask 
import flask
from flask_cors import CORS
app = flask.Flask(__name__)
CORS(app)

from flask import Flask, render_template,request, jsonify

# load model preprocessing
import numpy as np
import pandas as pd
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow.keras.models
from tensorflow.keras.models import model_from_json
from tensorflow.keras.layers import Input
import h5py

# Load pre-trained model into memory
json_file = open('model.json','r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("model.h5")
print("Loaded Model from disk")

# Helper function for tokenizing text to feed through pre-trained deep learning
def prepDataForDeepLearning(text):
    trainWordFeatures = tokenizer.texts_to_sequences(text)
    # textTokenized = pad_sequences(trainWordFeatures, 201, padding='post')
    textTokenized = pad_sequences(trainWordFeatures,maxlen=100) #pads sequences
    return textTokenized

# Load files needed to create proper matrix using tokens from training data
inputDataTrain = pd.DataFrame(pd.read_csv("train_DrugExp_Text.tsv", "\t", header=None))
trainText = [item[1] for item in inputDataTrain.values.tolist()]
trainingLabels = [0 if item[0] == -1 else 1 for item in inputDataTrain.values.tolist()]

# VOCABULARY_SIZE = 10000
VOCABULARY_SIZE = 7000
tokenizer = Tokenizer(num_words=VOCABULARY_SIZE)
tokenizer.fit_on_texts(trainText)

textTokenized = prepDataForDeepLearning(trainText)

loaded_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# # define a predict function as an endpoint 
@app.route('/', methods=['GET', 'POST'])
def predict():
    # whenever the predict method is called, we're going
    # to input the user entered text into the model
    # and return a prediction
    if request.method == 'POST':
        textData = request.form.get('text_entered')
        textDataArray = [textData]
        textTokenized = prepDataForDeepLearning(textDataArray)
        prediction = int((1-np.asscalar(loaded_model.predict(textTokenized)))*100)
        # return prediction in new page
        return render_template('prediction.html', prediction=prediction)
    else:
        return render_template("search_page.html")


# @app.route('/')
# def predict(value=None):
#     #whenever the predict method is called, we're going
#     #to input the user entered text into the model
#     #and return a prediction. 
#     #This line checks to make sure prediction is only done if the user has given a URL parameter
#     if request.args.get('text_entered'):
#         textData = request.args.get('text_entered')
#         print("text data: ", textData)
#         textDataArray = [textData]
#         print(textDataArray)
#         textTokenized = prepDataForDeepLearning(textDataArray)
#         print(textTokenized)
#         prediction = int((1-np.asscalar(loaded_model.predict(textTokenized)))*100)
#         print(prediction)
#         #return json object to parse on javascript side
#         return jsonify(prediction)

    # else:
    #     return render_template("search_page.html")   


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080)


##Libraries
    - pandas
    - numpy
    - matplotlib
    - seaborn
    - scikit-learn
    - mediapipe
    - opencv-python
    - pytorch
    - numpy
    - flask
    - flask-restful
    - flask-sqlalchemy
    - pinecone
    - boto3
    - dotenv

    ## fingerCapture.py
    - Using mediapipe the script will open the users camera and detect the users hand gestures. 
    - Capture the users hand gesture in real time and predict the letter the user is spelling. 
    - Display the predicted letter on the screen. 
    - Save the users hand gesture to a pinecone vector database. 


    ## modelTraining.py
    - Using pytorch the script will train a neural network to predict the letter the user is spelling.
    - split the model between training and evaluation sets 
    - The script will train the model on hand gestures from an zip file of classified hand gestures. 
    - Save the model to a file. 

    ## modelInference.py
    - Load the model from a file. 
    - Predict the letter the user is spelling. 
    - Display the predicted letter on the screen. 

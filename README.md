# Image-Captioning-using-an-LSTM-Encoder-Decoder-Model
Constructing a basic image captioning system using an LSTM encoder-decoder model, with a pre-trained Convolution Neural Network (CNN) trained on an object detection task to compute image embeddings. 

Components of LSTM encoder-decoder model:
* Create matrices of image representations using an off-the-shelf image encoder.
* Read and preprocess the image captions.
* Write a generator function that returns one training instance (input/output sequence pair) at a time.
* Train an LSTM language generator on the caption data.
* Write a decoder function for the language generator.
* Add the image input to write an LSTM caption generator.
* Implement beam search for the image caption generator.

The model is trained on Google's Cloud Computing Engine. 

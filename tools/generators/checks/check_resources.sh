#!/bin/sh
# Fetch each resource page, print its <title> and the heading ids / names that the topic titles refer to.
UA="Mozilla/5.0"
fetch() {
  url="$1"; shift
  echo "=================================================================="
  echo "URL: $url"
  body=$(curl -sL -A "$UA" --max-time 60 "$url")
  echo "HTTP title: $(printf '%s' "$body" | grep -o '<title>[^<]*</title>' | head -1)"
  for pat in "$@"; do
    echo "--- grep '$pat':"
    printf '%s' "$body" | grep -o -i "$pat" | sort -u | head -8
  done
  # Wikipedia licence line
  printf '%s' "$body" | grep -o 'Creative Commons Attribution-ShareAlike[^<]*' | head -1
}

fetch "https://www.3blue1brown.com/topics/neural-networks" 'But what is a neural network' 'What is backpropagation really doing' 'Backpropagation calculus' 'Chapter [0-9]'
fetch "https://neuralnetworksanddeeplearning.com/chap1.html" 'id="[^"]*perceptron[^"]*"' 'id="[^"]*sigmoid[^"]*"' 'id="[^"]*architecture[^"]*"' 'id="[^"]*learning_with_gradient_descent[^"]*"' 'id="[^"]*implementing[^"]*"' 'Creative Commons[^<]*' 'licen[sc]e[^<]*'
fetch "https://en.wikipedia.org/wiki/Multilayer_perceptron" 'id="[A-Z][^"]*"'
fetch "https://neuralnetworksanddeeplearning.com/chap2.html" 'id="[^"]*four[^"]*"' 'id="[^"]*algorithm[^"]*"' 'four fundamental equations'
fetch "https://en.wikipedia.org/wiki/Backpropagation" 'id="Overview"' 'id="Matrix_multiplication"' 'id="[A-Z][^"]*"'
fetch "https://en.wikipedia.org/wiki/Weight_initialization" 'id="Constant_initialization"' 'id="Random_initialization"' 'id="Glorot_initialization"' 'id="He_initialization"' 'id="[A-Z][^"]*"'
fetch "https://en.wikipedia.org/wiki/Vanishing_gradient_problem" 'id="[A-Z][^"]*"' 'exploding' 'clipping'
fetch "https://proceedings.mlr.press/v9/glorot10a.html" 'Copyright[^<]*' 'licen[sc]e[^<]*'
fetch "https://en.wikipedia.org/wiki/Stochastic_gradient_descent" 'id="Background"' 'id="Iterative_method"' 'id="[A-Z][^"]*"'
fetch "https://en.wikipedia.org/wiki/Training,_validation,_and_test_data_sets" 'id="[A-Z][^"]*"'
fetch "https://en.wikipedia.org/wiki/Overfitting" 'id="Machine_learning"' 'id="[A-Z][^"]*"'
fetch "https://en.wikipedia.org/wiki/Dilution_(neural_networks)" 'id="[A-Z][^"]*"' 'Redirected from[^<]*'
fetch "https://en.wikipedia.org/wiki/Dropout_(neural_networks)" 'Redirected from[^<]*'
fetch "https://en.wikipedia.org/wiki/Early_stopping" 'id="[A-Z][^"]*"' 'patience'
fetch "https://www.youtube.com/watch?v=KuXjwB4LzSA" '"title":"[^"]*"' '[0-9]:[0-9][0-9] [A-Za-z ]*'
fetch "https://en.wikipedia.org/wiki/Kernel_(image_processing)" 'id="[A-Z][^"]*"'
fetch "https://en.wikipedia.org/wiki/Convolutional_neural_network" 'id="Architecture"' 'id="[A-Z][^"]*"' 'Receptive field' 'shared weights' 'Shared weights'
fetch "https://karpathy.github.io/2019/04/25/recipe/" 'Copyright[^<]*' 'licen[sc]e[^<]*' 'overfit one batch' 'verify loss' 'one thing at a time' 'one at a time'
fetch "https://en.wikipedia.org/wiki/Rectifier_(neural_networks)" 'id="[A-Z][^"]*"' 'dying ReLU' 'Dying ReLU'

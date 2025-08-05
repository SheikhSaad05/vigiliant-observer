const text = document.getElementById("result");
const wordCount = document.getElementById("wordCount");
const charCount = document.getElementById("charCount");
const lineCount = document.getElementById("lineCount");
const mostRepeatedWord = document.getElementById("mostRepeatedWord");
const mostRepeatedWordCount = document.getElementById("mostRepeatedWordCount");

const currentText = text.value;
wordCount.innerText = countWords(currentText);
charCount.innerText = countChars(currentText);
lineCount.innerText = countLines(currentText);
let mostRepeatedWordInfo = findMostRepeatedWord(currentText);
mostRepeatedWord.innerText = mostRepeatedWordInfo.mostRepeatedWord;
mostRepeatedWordCount.innerText = mostRepeatedWordInfo.mostRepeatedWordCount;


function countWords(str) {
  str = str.trim();

  return str === ""? 0 : str.split(/\s+/).length;
}

function countChars(str) {
  return str.length;
}

function countLines(str) {
  return str.trim() === ""? 0 :str.split("\n").length;
}

function findMostRepeatedWord(str){
  let words = {};
  let result = {
    mostRepeatedWord: "",
    mostRepeatedWordCount: 0
  };

  str.match(/\w+/g).forEach(function(w){
    words[w]=(words[w]||0)+1 });

  for (var w in words) {
    if (!(words[w]<result.mostRepeatedWordCount)) {
      result.mostRepeatedWordCount = words[w];
      result.mostRepeatedWord = w;
    }
  }

  return result;
}
document.querySelectorAll('#repeat_answers_btn_choice').forEach(el=>el.addEventListener('click', function (){
  const word = document.querySelector('.train_word').textContent;
  const random_word = document.querySelector('.random_translate').dataset.word;
  const answer = eval(this.getAttribute('value').toLowerCase());
  console.log(answer && word === random_word, !answer && word !== random_word)
  if (answer && word === random_word){
    console.log('1st')
    this.classList.add('right');
  } else if (!answer && word !== random_word) {
    console.log('2nd')
    this.classList.add('right');
  } else {
    console.log('3rd')
    this.classList.add('wrong');
  }
}))

document.querySelectorAll('#quiz_answers_btn').forEach(el=>el.addEventListener('click', function () {
  const value = this.getAttribute('value');
  const word = document.querySelector('.train_word').textContent;
  console.log(word)
  if (value === word) {
    this.classList.add('right');
  } else {
    this.classList.add('wrong');
  }
}))


var songQueue = [];
var isPlaying = false;
var playBtn;
var audio;

const onPlayBtnClick = function() {
    isPlaying = !isPlaying
    if(isPlaying) {
        playBtn.classList.add('playing')
        playAudio()
    } else {
        playBtn.classList.remove('playing')
        pauseAudio()
    }
}

function playAudio() {
    audio.play();
}

function pauseAudio() {
    audio.pause();
}

window.onload = function () {
    playBtn = document.getElementById('playButton');
    playBtn.addEventListener('click', (event) => onPlayBtnClick());
    audio = document.getElementById("song");
}
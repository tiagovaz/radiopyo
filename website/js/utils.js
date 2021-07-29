var isPlaying = false;
var playBtn;
var audio;
var audioSource;
var songQueue = [];

var PLAYLIST_NO_REPEAT_LEN;

const onPlayBtnClick = function() {
    if(!isPlaying) {
        playAudio()
    } else {
        pauseAudio()
    }
}

const randomChoice = function(array) {
    // source: https://stackoverflow.com/a/4550514
    return array[Math.floor(Math.random() * array.length)];
}

const difference = function(toKeep, toRemove) {
    // source: https://stackoverflow.com/a/33034768
    return toKeep.filter(x => !toRemove.includes(x));
}

const playAudio = function() {
    isPlaying = true;
    playBtn.classList.add('playing');
    audio.play();
}

const pauseAudio = function() {
    isPlaying = false;
    playBtn.classList.remove('playing');
    audio.pause();
}

const onSongEnd = function() {
    isPlaying = false;
    chooseNextSong();
    playAudio();
}

const loadSong = function(song) {
    audioSource.src = song.PATH;
    audio.load();

    songQueue.push(song);
    songQueue = songQueue.slice(-PLAYLIST_NO_REPEAT_LEN);
    showSongMetadata(song);
}

const getRandomSong = function() {
    possibleSongs = difference(songsMetadata, songQueue);
    song = randomChoice(possibleSongs);
    return song;
}

const chooseNextSong = function() {
    nextSong = getRandomSong();
    loadSong(nextSong);
}

const showSongMetadata = function(song) {
    authorText = document.getElementById("author");
    authorText.textContent = song.ARTIST;

    durationText = document.getElementById("duration");
    durationText.textContent = song.DURATION;

    titleText = document.getElementById("title");
    titleText.textContent = song.TITLE;
}

window.onload = function () {

    PLAYLIST_NO_REPEAT_LEN = Math.floor(songsMetadata.length / 2);

    playBtn = document.getElementById('playButton');
    playBtn.addEventListener('click', (_) => onPlayBtnClick());

    nextButton = document.getElementById('nextButton');
    nextButton.addEventListener('click', (_) => onSongEnd());

    audio = document.getElementById("audio");
    audioSource = document.getElementById("audioSource");

    chooseNextSong();
    audio.onended = () => onSongEnd();
}
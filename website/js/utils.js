var isPlaying = false;
var playBtn;
var audio;
var audioSource;
var songQueue = [];
var queuePos = 0;

/**
 * Callback to handle play button click
 */
const onPlayBtnClick = function() {
    if(!isPlaying) {
        playAudio()
    } else {
        pauseAudio()
    }
}


/**
 * Callback to handle end of audio file
 */
 const onSongEnd = function() {
    queuePos += 1;
    document.getElementById("prevButton").disabled = false;
    loadSong(songQueue[queuePos % songsMetadata.length])

    if(isPlaying) {
        playAudio();
    }
}

/**
 * Callback to handle prev btn
 */
 const playPrevSong = function() {
    queuePos = Math.max(0, (queuePos - 1));

    if(queuePos === 0) {
        document.getElementById("prevButton").disabled = true;
    }

    loadSong(songQueue[queuePos % songsMetadata.length])

    if(isPlaying) {
        playAudio();
    }
}

/**
 * Shuffle an array pseudo-randomly
 * @param {Object}   array   Array to shuffle
 * @return {Object}          Shuffled array
 */
const shuffleArray = function(array) {
    // source: https://dev.to/codebubb/how-to-shuffle-an-array-in-javascript-2ikj
    return array.sort((a, b) => 0.5 - Math.random());
}


/**
 * Start a song
 */
const playAudio = function() {
    isPlaying = true;
    playBtn.classList.add('playing');
    audio.play();
}


/**
 * Pause a song
 */
const pauseAudio = function() {
    isPlaying = false;
    playBtn.classList.remove('playing');
    audio.pause();
}


/**
 * Load a song in the audio player but don't start it
 * @param {Object}  song   Metadata of the song to load
 */
const loadSong = function(song) {
    audioSource.src = song.PATH;
    audio.load();
    showSongMetadata(song);
}


/**
 * Change the UI to show what song is playing
 * @param {Object}  song   Metadata of a song
 */
const showSongMetadata = function(song) {
    authorText = document.getElementById("author");
    authorText.textContent = song.ARTIST;

    durationText = document.getElementById("duration");
    durationText.textContent = song.DURATION;

    titleText = document.getElementById("title");
    titleText.textContent = song.TITLE;
}


window.onload = function () {
    songQueue = shuffleArray(songsMetadata);

    playBtn = document.getElementById('playButton');
    playBtn.addEventListener('click', (_) => onPlayBtnClick());

    nextButton = document.getElementById('nextButton');
    nextButton.addEventListener('click', (_) => onSongEnd());

    prevButton = document.getElementById('prevButton');
    prevButton.addEventListener('click', (_) => playPrevSong());

    audio = document.getElementById("audio");
    audioSource = document.getElementById("audioSource");

    loadSong(songQueue[0]);
    audio.onended = () => onSongEnd();
}

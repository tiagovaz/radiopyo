var isPlaying = false;
var playBtn;
var audio;
var audioSource;
var songQueue = [];

var PLAYLIST_NO_REPEAT_LEN;

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
    isPlaying = false;
    chooseNextSong();
    playAudio();
}


/**
 * Choose an random element from an array
 * @param  {Object} array The array to choose from
 * @return {Object}       The chosen element from the array
 */
const randomChoice = function(array) {
    // source: https://stackoverflow.com/a/4550514
    return array[Math.floor(Math.random() * array.length)];
}


/**
 * Removes element in array that are in an other array
 * @param {Object}  toKeep   Array from which to remove elements
 * @param {Object}  toRemove Array containing elements to remove
 * @return {Object}          The array containing all elements in toKeep that are not also in toRemove
 */
const difference = function(toKeep, toRemove) {
    // source: https://stackoverflow.com/a/33034768
    return toKeep.filter(x => !toRemove.includes(x));
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

    songQueue.push(song);
    songQueue = songQueue.slice(-PLAYLIST_NO_REPEAT_LEN);
    showSongMetadata(song);
}


/**
 * Get a random song from all available songs that was not played in the last N songs
 * @return {Object} A song metadata
 */
const getRandomSong = function() {
    possibleSongs = difference(songsMetadata, songQueue);
    song = randomChoice(possibleSongs);
    return song;
}


/**
 * Get a random song and load it in the audio player
 */
const chooseNextSong = function() {
    nextSong = getRandomSong();
    loadSong(nextSong);
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
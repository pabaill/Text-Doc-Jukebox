"""
File: tdjbmenu.py
----------------
Text Doc Jukebox by Philip Baillargeon
Version: 1.0
Date: July 28th, 2021
Description:
This file creates a menu from which three sample songs may be selected.
This media player reads the custom notation akin to a piano roll, playing four tracks of audio simultaneously.
As the media plays, a playback bar and time stamp is displayed in real time.
"""

import time
import fluidsynth
import tkinter
import tkinter.font

NOTES = {'A0': 21, 'Bb0': 22, 'A#0': 22, 'B0': 23, 'C1': 24, 'C#1': 25, 'Db1': 25, 'D1': 26, 'D#1': 27, 'Eb1': 27,
         'E1': 28, 'F1': 29, 'F#1': 30, 'Gb1': 30, 'G1': 31, 'G#1': 32, 'Ab1': 32, 'A1': 33, 'A#1': 34, 'Bb1': 34,
         'B1': 35, 'C2': 36, 'C#2': 37, 'Db2': 37, 'D2': 38, 'D#2': 39, 'Eb2': 39, 'E2': 40, 'F2': 41, 'F#2': 42,
         'Gb2': 42, 'G2': 43, 'G#2': 44, 'Ab2': 44, 'A2': 45, 'A#2': 46, 'Bb2': 46, 'B2': 47, 'C3': 48, 'C#3': 49,
         'Db3': 49, 'D3': 50, 'D#3': 51, 'Eb3': 51, 'E3': 52, 'F3': 53, 'F#3': 54, 'Gb3': 54, 'G3': 55, 'G#3': 56,
         'Ab3': 56, 'A3': 57, 'A#3': 58, 'Bb3': 58, 'B3': 59, 'C4': 60, 'C#4': 61, 'Db4': 61, 'D4': 62, 'D#4': 63,
         'Eb4': 63, 'E4': 64, 'F4': 65, 'F#4': 66, 'Gb4': 66, 'G4': 67, 'G#4': 68, 'Ab4': 68, 'A4': 69, 'A#4': 70,
         'Bb4': 70, 'B4': 71, 'C5': 72, 'C#5': 73, 'Db5': 73, 'D5': 74, 'D#5': 75, 'Eb5': 75, 'E5': 76, 'F5': 77,
         'F#5': 78, 'Gb5': 78, 'G5': 79, 'G#5': 80, 'Ab5': 80, 'A5': 81, 'A#5': 82, 'Bb5': 82, 'B5': 83}
"""
NOTES is a dictionary that lists the note name as a key and the MIDI input number as a value.
This allows each note in the text file to be inputted using its universal name instead of a
numerical value
"""


def main():
    """
    A Tkinter canvas is made on which the menus are displayed. The start screen is presented and the canvas
    is continually updated until the window is closed.
    """
    canvas = make_canvas(600, 800, 'Text Doc Jukebox')
    make_start_screen(canvas)
    while True:
        canvas.update()


def play_song(file_name, canvas):
    """
    When given the appropriate text file name, the song is played from said file.
    A playback bar and time stamp is continuously updated as the song plays, both
    of which are deleted after the song ends.
    :param file_name: The name of the text file that stores note information
    :param canvas: The window on which the menus are presented.
    """
    canvas.delete('all')  # All extraneous canvas objects are deleted

    clock = 0  # Initialize counter that triggers each beat, then is reset to 0
    index = 0  # Start reading notes at index 0
    playback_time = 0  # Initialize counter that displays the current time for which the song has played
    progress_bar_length = 100  # Starting position relative to the left border of the window
    track_1 = []
    track_2 = []
    track_3 = []
    track_4 = []

    bpm = get_track_data(file_name)  # Reads the first line of the file to get bpm
    beat = round(1 / bpm * 60, 2)  # Converts beats per minute (bpm) to beats per second

    build_tracks(track_1, track_2, track_3, track_4, file_name)  # Notes are loaded from the text file to tracks

    """
    A grey playback bar is created, along with a red playback cursor and
    red playback bar that move from left to right as the song plays.
    The timestamp is initialized to include the value 0:00 and the
    length of the song.
    """

    canvas.create_rectangle(90, 150, 500, 170, fill='grey')
    progress_bar = canvas.create_rectangle(90, 150, 100, 170, fill='red')
    playback_cursor = canvas.create_oval(90, 150, 110, 170, fill='red')
    song_length = format_song_length(beat * len(track_1))
    timestamp = canvas.create_text(110, 130, text='0:00/' + song_length)
    canvas.update()

    """
    The Fluidsynth Synth is created using the DirectSound audio driver.
    FluidR3_GM is the soundfont, which stores the synthetic piano sounds.
    The synth plays on the default audio channel.
    """

    fs = fluidsynth.Synth()
    fs.start(driver='dsound')
    sfid = fs.sfload(r'C:\Users\phili\OneDrive\Desktop\CS 106A ('
                     r'Python)\PythonTheremin\venv\Lib\site-packages\fluidsynth\soundfonts\FluidR3_GM.sf2')
    fs.program_select(0, sfid, 0, 0)

    """
    A beat is given for the Synth to buffer. Then, the first note on all tracks is played.
    """

    time.sleep(beat)
    turn_on_note(fs, track_1, index)
    turn_on_note(fs, track_2, index)
    turn_on_note(fs, track_3, index)
    turn_on_note(fs, track_4, index)
    while index < len(track_1) - 1:
        if clock >= beat:  # A beat is triggered even if the clock skips the specific beat value due to rounding errors
            """
            Playback Hierarchy:
            1. The current note is turned off (if it is not a rest or hold)
            2. The note index is increased by 1
            3. The progress bar and cursor shift right proportionally to the length of the song
            4. The next note in the sequence is turned on.
            5. The clock is reset to 0
            """
            turn_off_note(fs, track_1, index)
            turn_off_note(fs, track_2, index)
            turn_off_note(fs, track_3, index)
            turn_off_note(fs, track_4, index)

            index += 1

            progress_bar_length += (400 / len(track_1))
            canvas.move(playback_cursor, 400 / len(track_1), 0)
            canvas.coords(progress_bar, 90, 150, progress_bar_length, 170)
            canvas.update()

            turn_on_note(fs, track_1, index)
            turn_on_note(fs, track_2, index)
            turn_on_note(fs, track_3, index)
            turn_on_note(fs, track_4, index)

            clock = 0

        """
        Tick Hierarchy:
        1. 1/100th of a second is taken to buffer, incrementing the clock (rounded to two places) and playback time by 1
        2. The current timestamp is deleted, and the new updated time is formatted and displayed
        3. The canvas is updated with the new timestamp.
        """

        time.sleep(.01)
        clock += .01
        playback_time += .01
        clock = round(clock, 2)
        canvas.delete(timestamp)
        timestamp = canvas.create_text(110, 130, text=format_song_length(playback_time) + '/' + song_length)
        canvas.update()

    """
    End of Song Hierarchy:
    1. Cursor snaps to end of the playback bar to correct for imprecise rounding.
    2. Progress bar moves to the end of the playback bar.
    3. Timestamp is updated to the total song length, and the window is updated.
    4. A beat is taken for the final note to play.
    5. The Fluidsynth Synth is deleted and the canvas is cleared.
    """

    canvas.coords(playback_cursor, 480, 150, 500, 170)
    progress_bar_length += 400 / len(track_1)
    canvas.coords(progress_bar, 90, 150, progress_bar_length - 10, 170)
    canvas.delete(timestamp)
    canvas.create_text(110, 130, text=song_length + '/' + song_length)
    canvas.update()
    time.sleep(beat)
    fs.delete()
    canvas.delete('all')


def make_canvas(width, height, title):
    """
    A new Tkinter window is created.
    :param width: The width of the desired window
    :param height: The height of the desired window
    :param title: The text displayed in the header of the window
    """
    top = tkinter.Tk()
    top.minsize(width=width, height=height)
    top.title(title)
    canvas = tkinter.Canvas(top, width=width + 1, height=height + 1)
    canvas.pack()
    return canvas


def make_start_screen(canvas):
    """
    The title screen is made, displaying the title of the program
    and the start button
    :param canvas: The window on which the text and button is displayed.
    """
    canvas.delete('all')
    title_font = tkinter.font.Font(family='Times', size=36)
    canvas.create_text(300, 200, text='Text Doc Jukebox', font=title_font)
    start_button = tkinter.Button(canvas, text='Start', command=lambda: make_menu_screen(canvas), padx=50, pady=20,
                                  activeforeground='blue')
    start_button.place(x=220, y=600)


def make_menu_screen(canvas):
    """
    The list of selectable songs is displayed, along with an option to return to the main menu.
    :param canvas: The window on which the buttons are displayed
    """
    canvas.delete('all')
    sb1 = tkinter.Button(canvas, text='Irish Tune', command=lambda: select_song(canvas, 'db.txt'), padx=50, pady=20)
    sb1.place(x=220, y=300)
    sb2 = tkinter.Button(canvas, text='Strauss WS', command=lambda: select_song(canvas, 'sws.txt'), padx=50, pady=20)
    sb2.place(x=220, y=450)
    sb3 = tkinter.Button(canvas, text='Never Gonna', command=lambda: select_song(canvas, 'nggyu.txt'), padx=50, pady=20)
    sb3.place(x=220, y=600)
    back_button = tkinter.Button(canvas, text='Back to Title', command=lambda:
                    [make_start_screen(canvas), delete_menu(menu_items)], padx=20, pady=10, activeforeground='red')
    back_button.place(x=10, y=10)
    menu_items = [sb1, sb2, sb3, back_button]


def delete_menu(button_list):
    """
    All buttons on the current screen are removed.
    :param button_list: The list of Tkinter buttons on the current screen
    :return:
    """
    for button in button_list:
        button.destroy()


def select_song(canvas, song_name):
    """
    The file name of the song to be played is printed to the console
    and the song is played.
    :param canvas: The window on which the song is to be played
    :param song_name: The name of the song file
    :return:
    """
    print('Now Playing: ' + song_name)
    play_song(song_name, canvas)


def build_tracks(track_1, track_2, track_3, track_4, file_name):
    """
    The note file is read, and each note is loaded in sequence on each track.
    :param track_1: A list of notes (entered empty)
    :param track_2: A list of notes (entered empty)
    :param track_3: A list of notes (entered empty)
    :param track_4: A list of notes (entered empty)
    :param file_name: The name of the text file that holds the desired song
    """
    note_file = open(file_name, 'r')
    note_file.readline()  # Buffer to eliminate bpm data

    line1 = note_file.readline().strip()
    read_note_line(track_1, line1)
    line2 = note_file.readline().strip()
    read_note_line(track_2, line2)
    line3 = note_file.readline().strip()
    read_note_line(track_3, line3)
    line4 = note_file.readline().strip()
    read_note_line(track_4, line4)

    note_file.close()


def get_track_data(file_name):
    """
    Data from the first line of the file is read (bpm)
    :param file_name: The name of the desired song file
    """
    temp_bpm = ''
    note_file = open(file_name, 'r')
    for char in note_file.readline().strip():
        if char in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            temp_bpm += char
    note_file.close()
    return int(temp_bpm)


def format_song_length(song_length):
    """
    Returns a formatted string that represents the length of a given song.
    :param song_length: The desired value (in seconds) to be formatted
    """
    spacer = ''
    minutes = 0
    sec = song_length
    while sec > 59:
        minutes += 1
        sec -= 60
    if sec < 10:
        spacer = '0'
    return str(int(minutes)) + ":" + spacer + str(int(sec))


def read_note_line(track, line):
    """
    Each line of the file is read, adding notes until the
    end of line character "|" is read.
    :param track: The given track for which notes to be loaded.
    :param line: The line from the text file from which notes are taken.
    """
    temp = ''
    is_line_finished = False
    while not is_line_finished:
        for char in line:
            if char == '|':
                is_line_finished = True
            elif char != ' ':
                temp += char
            elif temp != '' and is_line_finished is False:
                track.append(temp)
                temp = ''


def turn_off_note(fs, track, index):
    """
    If the current note is not a rest or sustain, it is turned off before
    moving to the next note in the sequence
    :param fs: The Fluidsynth Synth on which notes are played.
    :param track: The list of notes for a given line.
    :param index: The current position within the list of notes.
    """
    if track[index + 1] == 'r':
        while track[index] == 'r' or track[index] == '...':
            index -= 1
        fs.noteoff(0, NOTES[track[index]])  # If the current note is a rest, find the last valid note and turn off
        return
    should_switch_note = track[index + 1] != '...' and track[index] != 'r'
    is_valid_note = track[index] != '...' and track[index] != 'r'
    if should_switch_note and is_valid_note:
        fs.noteoff(0, NOTES[track[index]])
        # If the current note is not a rest and there are no subsequent rests or
        # sustains, turn this note off.


def turn_on_note(fs, track, index):
    """
    If a valid note is given on a track at an index, turn it on.
    :param fs: The Fluidsynth Synth on which notes are played.
    :param track: The list of notes for a given line.
    :param index: The current position within the list of notes.
    """
    if track[index] != '...' and track[index] != 'r':
        fs.noteon(0, NOTES[track[index]], 80)


if __name__ == '__main__':
    main()

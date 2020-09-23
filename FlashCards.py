import os
import sys
import shutil
import tempfile
import re
import random
import glob

import PySimpleGUI as sg
import gtts
from playsound import playsound
from googletrans import Translator as gt

def tts(text):
    tempPath = tempfile.mkdtemp()
    tempFile = os.path.join(tempPath, "tts.mp3")
    tts = gtts.gTTS(text, lang='zh-cn')
    tts.save(tempFile)
    playsound(tempFile)
    shutil.rmtree(tempPath)

def getPinyin(text):
    return gt().translate(text, dest="zh-cn").pronunciation.lower()

def readFile(fPath, cards):
    file = open(fPath, 'r')
    for line in file:
        if line.startswith('//') or line.startswith('#'):
            continue
        spline = line.strip('\n').split('\t')
        #if len(re.findall(ur'[\u4e00-\u9fff]+',spline[0])):
        if True:
            cards[spline[0]] = [spline[1], spline[2]]
    file.close()

def readCards():
    cards = {}
    path = os.path.join(os.getcwd(), '.flashcards')
    if os.path.exists(path):
        for fPath in glob.glob1(path, '*.xml'):
            if fPath.endswith('flashcards.xml'):
                continue
            readFile(fPath, cards)
        fPath = os.path.join(path, 'flashcards.xml')
        if os.path.exists(fPath):
            readFile(fPath, cards)

    return cards

def writeCards():
    path = os.path.join(os.getcwd(), '.flashcards')
    if not os.path.exist(path):
        os.mkdir(path)
    path = os.path.join(path, 'flashcards.xml')

    file = open(path, 'w')
    file.close()

def selectCard(cards, weight=None):
    table = []
    length = 0.0
    for key in cards.keys():
        table.append([key])
        if weight is None:
            table[-1].append(1)
            length += float(1)
        else:
            raise NotImplementedError

    selection = length*random.random()
    count = 0.0
    for t in table:
        count += t[1]
        if count > selection:
            return t[0]

    raise RuntimeError

def editCards(cards, bgc):
    return False

def checkAnswer(cards, hanzi, pinyin, meaning):
    checkPinyin = (cards[hanzi][0].lower() == pinyin)
    if checkPinyin:
        checkTone = True
    else:
        checkTone = False
    checkMeaning = (cards[hanzi][1].lower() == meaning)
    status = ''
    if checkPinyin:
        if checkTone:
            status += 'Correct pinyin and tone'
        else:
            status += 'Correct pinyin, incorrect tone'
    else:
        status += 'Incorrect pinyin'
    status += '\n'
    if checkMeaning:
        status += 'Correct meaning'
    else:
        status += 'Incorrect meaning'

    answer = 'Pinyin: %s\nMeaning: %s' % (cards[hanzi][0], cards[hanzi][1])

    layout = [
              [sg.Text('%s' % hanzi, key='hanzi', text_color='black', background_color='white', font='Arial 48', size=(2*len(hanzi)+1,1), justification='center')],
              [sg.Text(' %s ' % status, font='Arial 12'), sg.Text(' %s ' % answer, font='Arial 12')],
              [sg.Button('🕪 Read 🔊')]
             ]

    checkAnswerWin = sg.Window('抽认卡: ...', layout, element_justification='c', finalize=True)
    while True:
        event, values = checkAnswerWin.read()
        if event in [sg.WIN_CLOSED]:
            break
        if event == '🕪 Read 🔊':
            tts(hanzi)
    checkAnswerWin.close()

def study(cards, bgc):
    quit = False
    hanzi = ''
    layout = [
              [sg.Text('%s' % hanzi, key='hanzi', text_color='black', background_color='white', font='Arial 48', size=(5,1), justification='center')],
              [sg.Text('Pinyin:', text_color='white', background_color=bgc, font='Arial 12'), sg.InputText(size=(10,1), do_not_clear=False), sg.Text(' Meaning:', text_color='white', background_color=bgc, font='Arial 12'), sg.InputText(size=(10,1), do_not_clear=False), sg.Button('Check', bind_return_key=True), sg.Button('Back')]
             ]
    studyWin = sg.Window('抽认卡: 学习', layout, element_justification='c', finalize=True)
    while True:
        while True:
            hanzi_new = selectCard(cards)
            if hanzi != hanzi_new:
                hanzi = hanzi_new
                break
        studyWin['hanzi'].update('%s' % hanzi)
        studyWin['hanzi'].set_size(size=(2*len(hanzi)+1,1))
        event, values = studyWin.read()
        if event in [sg.WIN_CLOSED, 'Back']:
            if event in [sg.WIN_CLOSED]:
                quit = True
            break
        elif event == 'Check':
            checkAnswer(cards, hanzi, values[0].lower(), values[1].lower())

    studyWin.close()
    return quit

def gui(cards):
    quit = False
    sg.theme('Dark Red 1')
    bgc = sg.theme_background_color()
    sg.theme_text_element_background_color(color='white')
    sg.theme_input_background_color(color='white')
    sg.theme_text_color(color='black')
    bc = sg.theme_button_color()
    sg.theme_button_color(color=('black', bc[1]))
    layout = [
              [sg.Text('汉字\n抽认卡', text_color='white', background_color=bgc, font='Arial 48', justification='center')],
              [sg.Text(' Mark "马克" Wootton ', text_color='black', background_color='white', font='Arial 12', justification='right')],
              [sg.Button('Edit Cards'), sg.Button('Study'), sg.Button('Read')]
             ]
    mainWin = sg.Window('抽认卡', layout, element_justification='c')#, icon=bildsimbolo)
    while True:
        event, values = mainWin.read()
        # Fenestro fermita
        if event == sg.WIN_CLOSED:
            break
        elif event == 'Edit Cards':
            mainWin.hide()
            if editCards(cards, bgc):
                break
            mainWin.un_hide()
        elif event == 'Study':
            mainWin.hide()
            if study(cards, bgc):
                break
            mainWin.un_hide()
        elif event == 'Read':
            text = sg.popup_get_text('Enter text to read:', background_color=bgc, text_color='white')
            if text is not None:
                if len(text):
                    tts(text)

def main():
    # print(getPinyin("你好"))
    gui(cards = readCards())

if __name__ == '__main__':
    main()

import os
import sys
import shutil
import tempfile
import re
import random
import glob
import collections
import math
import platform

import PySimpleGUI as sg
import xpinyin
import gtts
from playsound import playsound
from googletrans import Translator as gt
from tkinter import Tk
# import pyperclip

try:
    sound = '🕪 Read 🔊'
    sg.popup(sound, auto_close=True, auto_close_duration=0, line_width=0, no_titlebar=True, grab_anywhere=True)
except:# _tkinter.TclError:
    sound = 'Read'

changes = False

toneDict = collections.OrderedDict()
toneDict['ia'] = ['iā', 'iá', 'iǎ', 'ià']
toneDict['ua'] = ['uā', 'uá', 'uǎ', 'uà']

toneDict['ie'] = ['iē', 'ié', 'iě', 'iè']
toneDict['ue'] = ['uē', 'ué', 'uě', 'uè']
toneDict['üe'] = ['üē', 'üé', 'üě', 'üè']
toneDict['ve'] = toneDict['üe']

toneDict['ai'] = ['āi', 'ái', 'ǎi', 'ài']
toneDict['ei'] = ['ēi', 'éi', 'ěi', 'èi']
toneDict['ui'] = ['uī', 'uí', 'uǐ', 'uì']

toneDict['ao'] = ['āo', 'áo', 'ǎo', 'ào']
toneDict['io'] = ['iō', 'ió', 'iǒ', 'iò']
toneDict['uo'] = ['uō', 'uó', 'uǒ', 'uò']

toneDict['iu'] = ['iū', 'iú', 'iǔ', 'iù']
toneDict['ou'] = ['ōu', 'óu', 'ǒu', 'òu']

toneDict['a'] = ['ā', 'á', 'ǎ', 'à']
toneDict['e'] = ['ē', 'é', 'ě', 'è']
toneDict['i'] = ['ī', 'í', 'ǐ', 'ì']
toneDict['o'] = ['ō', 'ó', 'ǒ', 'ò']
toneDict['u'] = ['ū', 'ú', 'ǔ', 'ù']
toneDict['ü'] = ['ǖ', 'ǘ', 'ǚ', 'ǜ']
toneDict['v'] = toneDict['ü']

tones = [['a', 'āáǎà'], ['e', 'ēéěè'], ['i','īíǐì'], ['o', 'ōóǒò'], ['u', 'ūúǔù'], ['ü', 'ǖǘǚǜ']]

def version():
    return '1-0'

def help():
    title = '汉字 Flashcards'
    subtitle = 'Version %s\n© Mark Wootton 2020\n' % version()
    #         ################################################################################
    hText = 'Welcome to 汉字Flashcards. You can study Chinese character\nflashcards in two modes:\n'
    hText += '- see a Chinese character and enter its pinyin and meaning\n'
    hText += '- see a definition and enter Chinese characters\n'
    hText += '\n'
    hText += 'New flash cards can be made in the “Edit Cards” menu. Click "New card"\n'
    hText += '(or press enter) to add an entry. Right click on an existing card to edit or\n'
    hText += 'delete it. Cards can be added en masse from a plain text file by clicking the\n'
    hText += '"Import" button. Input files should be of type *.txt and be structured as\n'
    hText += 'follows:\n'
    example = '汉字一	hàn zì yī	flashcard one\n'
    example += '汉字二	hàn zì èr	flashcard two\n'
    example += '汉字三	hàn zì sān	flashcard three\n'
    afterExample = 'where each column is separated by a tab.\n'

    layout = [
              [sg.Text(title, font='Arial 24')],
              [sg.Text(subtitle, font='Arial 12')],
              [sg.Text(hText, font='Arial 12')],
              [sg.Text(example, font='Courier 12')],
              [sg.Text(afterExample, font='Arial 12')],
              [sg.Button('Back')]
             ]
    helpWin = sg.Window('抽认卡: Help and Description', layout)
    while True:
        event, values = helpWin.read()
        if event == sg.WIN_CLOSED or 'Back':
            break

    helpWin.close()

def tts(text):
    try:
        tempPath = tempfile.mkdtemp()
        tempFile = os.path.join(tempPath, "tts.mp3")
        tts = gtts.gTTS(text, lang='zh-cn')
        tts.save(tempFile)
        playsound(tempFile)
        shutil.rmtree(tempPath)
    except:
        sg.popup('Error: Input could not be read. Possible causes:\n• Invalid input\n• No access to Google Translate API', title='抽认卡: Error', font='Arial 12')

def getPinyin(text):
    try:
    # if True:
        xp = xpinyin.Pinyin().get_pinyin(text, ' ', tone_marks='marks')
        gtr = gt().translate(text, dest="zh-cn").pronunciation.lower()
        if xp.strip(' ') == gtr.strip(' '):
            return xp, 'xpinyin,Google Translate', 'good'
        else:
            found = []
            sxp = xp.split(' ')
            for x in range(len(sxp)):
                gtrNew = gtr.replace(sxp[x], sxp[x].upper(), 1)
                if gtrNew != gtr:
                    found.append(x)
                gtr = gtrNew
            gFound = []
            gNot = False
            for g in gtr:
                if g == ' ':
                    continue
                if not gNot and g.lower() == g:
                    gNot = True
                    gFound.append(g)
                elif gNot and g.lower() == g:
                    gFound[-1] += g
                elif gNot and g.lower() != g:
                    gNot = False
            c = 0
            for x in range(len(sxp)):
                if x not in found:
                    sxp[x] = gFound[c]
                    c += 1
            result = sxp[0]
            for x in sxp[1:]:
                result += " %s" % x
            result = result.strip('   ').strip('  ')
            return result, 'xpinyin,Google Translate', 'reconstructed'
    except:
        return xpinyin.Pinyin().get_pinyin(text, ' ', tone_marks='marks'), 'xpinyin', 'no internet'

def getMeaning(text):
    return gt().translate(text, dest="en").text.lower(), 'Google Translate'

def pinyinNumToMark(text):
    sText = text.lower().split(' ')
    result = ''
    if len(text):
        for s in sText:
            if s[-1].isdigit():
                tone = int(s[-1])
                s = s[:-1]
                if tone < 5:
                    for r in toneDict.keys():
                        m = s.replace(r, toneDict[r][tone-1])
                        if m != s:
                            s = m
                            break
            result += '%s ' % s
        return result[:-1]
    else:
        return result

def removeTone(text):
    result = text.lower()
    for letter in tones:
        noTone = letter[0]
        for tone in letter[1]:
            result = result.replace(tone, noTone)
    return result

def checkIfHanzi(text):
    return (0 < len(re.findall(r'[\u4e00-\u9fff]+', text)))

def readFile(fPath, cards, overwrite=True):
    file = open(fPath, 'r', encoding="utf8")
    for line in file:
        line = line.strip('\ufeff').strip('\n')
        if line.startswith('//') or line.startswith('#') or not len(line):
            continue
        spline = line
        for i in range(10, 1, -1):
            spline = spline.replace(' '*i, '\t')
        spline = spline.split('\t')
        if spline[0] in cards and not overwrite:
            continue
        if checkIfHanzi(spline[0]) and len(spline) >= 3:
            cards[spline[0]] = [pinyinNumToMark(spline[1]), spline[2]]
            if len(spline) >= 4:
                cards[spline[0]].append(spline[3])
            else:
                cards[spline[0]].append(None)
    file.close()

def readCards():
    # cards = {}
    cards = collections.OrderedDict()
    path = os.path.join(os.path.split(os.path.dirname(sys.argv[0]))[0], '.flashcards')
    # path = os.path.join(os.getcwd(), '.flashcards')
    if os.path.exists(path):
        for fPath in glob.glob1(path, '*.txt'):
            if fPath == 'flashcards.txt':
                continue
            readFile(os.path.join(path, fPath), cards)
        fPath = os.path.join(path, 'flashcards.txt')
        if os.path.exists(fPath):
            readFile(fPath, cards)

    return cards

def writeCards(cards):
    # path = os.path.join(os.getcwd(), '.flashcards')
    fPath = os.path.join(os.path.split(os.path.dirname(sys.argv[0]))[0], '.flashcards')
    if not os.path.exists(fPath):
        os.mkdir(fPath)
    fPath = os.path.join(fPath, 'flashcards.txt')

    file = open(fPath, 'w', encoding="utf8")
    for hanzi in cards.keys():
        note = ''
        if cards[hanzi][2] is not None:
            note += '\t%s' % cards[hanzi][2]
        file.write("%s\t%s\t%s%s\n" % (hanzi, cards[hanzi][0], cards[hanzi][1], note))
    file.close()

def readWeights(cards, user):
    userData = False
    cardData = False
    weights = collections.OrderedDict()
    uData = {'EN->ZH' : 0, 'ZH->EN' : 0}
    fPath = os.path.join(os.path.split(os.path.dirname(sys.argv[0]))[0], '.flashcards', '%s.profile' % user)
    if os.path.exists(fPath):
        file = open(fPath, 'r', encoding="utf8")
        for line in file:
            spline = line.strip('\n').split('\t')
            if spline[0] == '~UserData':
                cardData = False
                userData = True
            elif spline[0] == '~CardData':
                cardData = True
                userData = False
            elif userData:
                if spline[0] in uData.keys():
                    try:
                        uData[spline[0]] = int(spline[1])
                    except IndexError:
                        pass
            elif cardData:
                weights[spline[0]] = int(spline[1])
        file.close()
    for hanzi in cards.keys():
        if hanzi not in weights:
            weights[hanzi] = 1

    return weights, uData

def writeWeights(user, weights, uData):
    if user is None or weights is None:
        return
    fPath = os.path.join(os.path.split(os.path.dirname(sys.argv[0]))[0], '.flashcards', '%s.profile' % user)
    file = open(fPath, 'w', encoding="utf8")
    file.write('~UserData\n%s\n' % user)
    file.write('EN->ZH\t%d\nZH->EN\t%d\n' % (uData['EN->ZH'], uData['ZH->EN']))
    file.write('~CardData\n')
    for hanzi in weights.keys():
        file.write('%s\t%d\n' % (hanzi, weights[hanzi]))
    file.close()

def selectCard(cards, weights=None):
    while True:
        table = []
        max = 0.0
        for hanzi in weights.keys():
            table.append([hanzi, 1.0/float(weights[hanzi])])
            max += table[-1][1]

        selection = max*random.random()
        count = 0.0
        for t in table:
            count += t[1]
            if count > selection:
                if t[0] in cards:
                    return t[0]
                else:
                    weights.pop(t[0])
        if not len(weights.keys()):
            break

    # for hanzi in weights.keys():
    #     count += weights[hanzi]
    #     if count > selection:
    #         return hanzi

    raise RuntimeError

def editHanzi(cards, hanzi=None):
    global changes
    edits = False
    quit = False
    warning = ''
    if hanzi is None:
        hanzi = sg.popup_get_text('Enter hanzi:', title='抽认卡', font='Arial 12')
        if hanzi is not None:
            if not checkIfHanzi(hanzi):
                hanzi = None
        if hanzi is None:
            return quit, edits
        if hanzi in cards:
            if 'No' == sg.popup('A card already exists for %s. Do you wish to edit it?' % hanzi, title='抽认卡', custom_text=('Yes', 'No'), font='Arial 12'):
                return quit, edits

    try:
        if hanzi in cards:
            dPY = cards[hanzi][0]
        else:
            dPY, source, note = getPinyin(hanzi)
    except:
        dPY = ''
    try:
        if hanzi in cards:
            dMn = cards[hanzi][1]
        else:
            dMn, source = getMeaning(hanzi)
            warning = 'Hanzi definitions provided by %s\n— trust at your own discretion!' % source
    except:
        dMn = ''
    if hanzi in cards:
        if cards[hanzi][2] is not None:
            dNt = cards[hanzi][2]
        else:
            dNt = ''
    else:
        dNt = ''
    layout = [
              [sg.Text('Hanzi:', font='Arial 14'), sg.Text('%s' % hanzi, background_color='white', text_color='black', font='KaiTi 16', size=(30,1))],
              [sg.Text('Pinyin:', font='Arial 14'), sg.InputText(default_text=dPY, size=(30,1))],
              [sg.Text('Meaning:', font='Arial 14'), sg.InputText(default_text=dMn, size=(30,1))],
              [sg.Text('Notes (optional):', font='Arial 14'), sg.InputText(default_text=dNt, size=(30,1))],
              [sg.Text(warning, font='Arial 12')],
              [sg.Button('Save', bind_return_key=True), sg.Button('Cancel')]
             ]
    editHanziWin = sg.Window('抽认卡', layout, element_justification='r', finalize=True)
    while True:
        event, values = editHanziWin.read()
        if event in [sg.WIN_CLOSED, 'Cancel']:
            if event == sg.WIN_CLOSED:
                quit = True
            break
        elif event == 'Save':
            if values[2] is not None:
                note = values[2]
                while True:
                    noteNew = note.replace('  ', ' ')
                    if note == noteNew:
                        break
                    else:
                        note = noteNew
                if note == '':
                    note = None
            else:
                note = None
            cards[hanzi] = [values[0], values[1], note]
            edits = True
            changes = True
            break
    editHanziWin.close()
    return quit, edits

def editCards(cards):
    global changes
    quit = False
    # all = ''
    cardList = []
    widest = 30
    for key in cards.keys():
        note = ''
        if cards[key][2] is not None:
            note += ' (%s)' % cards[key][2]
        line = '%s  %s  %s%s\n' % (key, cards[key][0], cards[key][1], note)
        width = math.ceil(len(line)*1.3)
        cardList.append([sg.Text(line, background_color='white', text_color='black', size=(width,1), right_click_menu=['Edit',['Edit card: %s' % key, 'Delete card: %s' % key, 'Cancel']])])
        if width > widest:
            widest = width
    layout = [
              [sg.Text("Existing cards:", font='Arial 24')], #size=(1000, 500)
              [sg.Column(cardList, background_color='white', size=(widest*6, 500), scrollable=True, vertical_scroll_only=True)],
              [sg.Button('New card', bind_return_key=True), sg.Input(key='_IMPORT_', enable_events=True, visible=False), sg.FileBrowse('Import', target='_IMPORT_', file_types=(('TXT', '.txt'), ('All files', '*')))],
              [sg.Button('Save & exit'), sg.Button('Discard changes')]
             ]
    editWin = sg.Window('抽认卡', layout, element_justification='c', finalize=True)
    while True:
        reopen = False
        event, values = editWin.read()
        if event in [sg.WIN_CLOSED, 'Discard changes']:
            quit = (event == sg.WIN_CLOSED)
            if changes:
                changes = False
                if 'Yes' == sg.popup('Are you sure you want to discard your changes?', title='抽认卡', custom_text=('Yes', 'No'), font='Arial 12'):
                    cards = readCards()
                else:
                    writeCards(cards)
            # if event == 'Discard changes':
            #     reopen = True
            break
        elif event == 'Save & exit':
            if changes:
                writeCards(cards)
                changes = False
            break
        elif event.startswith('Edit card: '):#
            hanzi = event.strip('Edit card: ')
            _, reopen = editHanzi(cards, hanzi=hanzi)
            if reopen:
                break
        elif event.startswith('Delete card: '):
            hanzi = event.strip('Delete card: ')
            if 'Yes' == sg.popup('Are you sure you want to delete the card for %s' % hanzi, title='抽认卡', custom_text=('Yes', 'No'), font='Arial 12'):
                cards.pop(hanzi)
                reopen = True
                changes = True
                break
        elif event == 'New card':
            _, reopen = editHanzi(cards)
            if reopen:
                break
        elif event == '_IMPORT_':
            readFile(values['_IMPORT_'], cards, overwrite=('Use new' == sg.popup('How do you want to handle cards found in both existing and new lists?', title='抽认卡', custom_text=('Keep old', 'Use new'), font='Arial 12')))
            reopen = True
            changes = True
            break
    editWin.close()
    return quit, reopen, cards

def updateScore(weights, hanzi, score):
    weights[hanzi] += score
    if weights[hanzi] < 1:
        weights[hanzi] = 1
    # elif weight[hanzi] > 10:
    #     weight[hanzi] = 10

def checkHanzi(cards, hanzi, pinyin, meaning):
    quit = False
    score = 0
    meaning = meaning.lower()
    checkTone = (cards[hanzi][0].lower() == pinyinNumToMark(pinyin))
    if checkTone:
        checkPinyin = True
    else:
        if removeTone(cards[hanzi][0]) == removeTone(pinyin):
            checkPinyin = True
        else:
            checkPinyin = False

    checkMeaning = (cards[hanzi][1].lower() == meaning)
    status = 'Your answer:  '
    if len(pinyin)+len(meaning):
        if len(pinyin):
            status += pinyin.lower()
            if len(meaning):
                status += ', '
        if len(meaning):
            status += '%s' % meaning
    else:
        status += 'No answer'
    status += '\n'
    if checkPinyin:
        if checkTone:
            status += 'Pinyin ✓ Tone ✓'
            score += 2
        else:
            status += 'Pinyin ✓ Tone ✗'
            score += -1
    else:
        status += 'Pinyin ✗'
        score += -2
    status += '\n'
    if checkMeaning:
        status += 'Meaning ✓'
        score += 1
    else:
        status += 'Meaning ✗'
        score += -1
    answer = 'Answer:\nPinyin:  %s\nMeaning:  %s' % (cards[hanzi][0], cards[hanzi][1])
    answerLine = [[sg.Text('%s' % answer, font='Arial 12')]]
    if cards[hanzi][2] is not None:
        answerLine.append([sg.Text('Note:  %s' % cards[hanzi][2], font='Arial 10')])

    layout = [
              [sg.Text('%s' % hanzi, key='hanzi', text_color='black', background_color='white', font='KaiTi 60', size=(2*len(hanzi)+1,1), justification='center')],
              [sg.Text('%s' % status, font='Arial 12'), sg.VSeperator(), sg.Column(answerLine)],
              [sg.Button(sound), sg.Button('Next', bind_return_key=True)]
             ]
    # if cards[hanzi][2] is not None:
    #     layout[-2].append(sg.Button('?'))
    checkHanziWin = sg.Window('抽认卡', layout, element_justification='c', finalize=True)
    while True:
        event, values = checkHanziWin.read()
        if event in [sg.WIN_CLOSED, 'Next']:
            if event == sg.WIN_CLOSED:
                quit = True
            break
        elif event == sound:
            tts(hanzi)
        # elif event == '?':
        #     sg.popup('%s: %s (%s)' % (hanzi, cards[hanzi][1], cards[hanzi][2]))
    checkHanziWin.close()
    return quit, score

# def getStudyType():
#     layout = [[sg.Button('汉字 ➡️ Pinyin & definition'), sg.Button('Definition ➡️ 汉字')]]
#     studyTypeWin = sg.Window('抽认卡: 学习什么？', layout, element_justification='c', finalize=True)
#     while True:
#         event, values = studyTypeWin.read()
#         if len(event):
#             studyTypeWin.close()
#             return event

def studyHanzi(cards, user):
    weights, uData = readWeights(cards, user)
    quit = False
    hanzi = ''
    layout = [
              [sg.Text('%s' % hanzi, key='hanzi', text_color='black', background_color='white', font='KaiTi 60', size=(5,1), justification='center')],
              [sg.Text('Pinyin:', font='Arial 12'), sg.InputText(size=(10,1), do_not_clear=False), sg.Text(' Meaning:', font='Arial 12'), sg.InputText(size=(10,1), do_not_clear=False), sg.Button('Check', bind_return_key=True), sg.Button('Back')]
             ]
    studyHanziWin = sg.Window('抽认卡: 学习汉字 — User: %s' % user, layout, element_justification='c', finalize=True)
    while True:
        while True:
            hanzi_new = selectCard(cards, weights=weights)
            if hanzi != hanzi_new:
                hanzi = hanzi_new
                break
        studyHanziWin['hanzi'].update('%s' % hanzi)
        studyHanziWin['hanzi'].set_size(size=(2*len(hanzi)+1,1))
        event, values = studyHanziWin.read()
        if event in [sg.WIN_CLOSED, 'Back']:
            if event in [sg.WIN_CLOSED]:
                quit = True
            break
        elif event == 'Check':
            uData['ZH->EN'] += 1
            studyHanziWin.hide()
            quit, score = checkHanzi(cards, hanzi, values[0], values[1])
            updateScore(weights, hanzi, score)
            if quit:
                break
            studyHanziWin.un_hide()

    studyHanziWin.close()
    writeWeights(user, weights, uData)
    return quit

def checkMeaning(cards, hanzi, input):
    quit = False
    score = 0
    top = [sg.Text('')]
    if hanzi == input:
        status = '✓'
        score += 1
    else:
        status = '✗'
        score += -1
    if cards[hanzi][2] is not None:
        note = sg.Text('%s' % cards[hanzi][2], font='Arial 10', size=(30,1), justification='center')
    else:
        note = sg.Text('', size=(30,1), font='Arial 1', justification='center')
    layout = [
              [sg.Text('%s' % cards[hanzi][0], text_color='black', background_color='white', font='Arial 12')],
              [sg.Text('%s' % hanzi, key='hanzi', text_color='black', background_color='white', font='KaiTi 60', size=(2*len(hanzi)+1,1), justification='center')],
              [sg.Text('%s' % cards[hanzi][1], font='Arial 12', size=(30,1), justification='center')],
              [note],
              [sg.Text('Your answer:  %s  %s' % (input, status), font='Arial 12', size=(30,1), justification='center')],
              [sg.Button(sound), sg.Button('Next', bind_return_key=True)]
             ]
    checkMeaningWin = sg.Window('抽认卡', layout, element_justification='c', finalize=True)
    while True:
        event, values = checkMeaningWin.read()
        if event in [sg.WIN_CLOSED, 'Next']:
            if event == sg.WIN_CLOSED:
                quit = True
            break
        elif event == sound:
            tts(hanzi)
    checkMeaningWin.close()
    return quit, score

def studyMeaning(cards, user):
    quit = False
    weights, uData = readWeights(cards, user)
    hanzi = ''
    qColumn = sg.Column([[sg.Text('', key='meaning', text_color='black', background_color='white', font='Arial 24', size=(5,1), justification='left')], [sg.Text('', key='note', text_color='black', background_color='white', font='Arial 12', size=(5,1), justification='left')]])
    aColumn = sg.Column([[sg.Text('Chinese:')],[sg.InputText(font='KaiTi 40', key='hanzi', size=(5,1), do_not_clear=False)],[sg.Button('Check', bind_return_key=True), sg.Button('Back')]])
    layout = [
              [qColumn, sg.VSeperator(), aColumn]
             ]
    studyMeaningWin = sg.Window('抽认卡: 学习意思 — User: %s' % user, layout, element_justification='c', finalize=True)
    while True:
        while True:
            hanzi_new = selectCard(cards, weights=weights)
            if hanzi != hanzi_new:
                hanzi = hanzi_new
                break
        studyMeaningWin['meaning'].update('%s' % cards[hanzi][1])
        studyMeaningWin['meaning'].set_size(size=(len(cards[hanzi][1])+1,1))
        studyMeaningWin['hanzi'].set_size(size=(2*len(hanzi)+1,1))
        studyMeaningWin['note'].set_size(size=(2*len(cards[hanzi][1])+2,1))
        if cards[hanzi][2] is not None:
            studyMeaningWin['note'].update('%s' % cards[hanzi][2], background_color='white')
        else:
            studyMeaningWin['note'].update('', background_color=sg.theme_background_color())
        event, values = studyMeaningWin.read()
        if event in [sg.WIN_CLOSED, 'Back']:
            if event in [sg.WIN_CLOSED]:
                quit = True
            break
        elif event == 'Check':
            uData['EN->ZH'] += 1
            studyMeaningWin.hide()
            quit, score = checkMeaning(cards, hanzi, values['hanzi'])
            updateScore(weights, hanzi, score)
            if quit:
                break
            studyMeaningWin.un_hide()
    studyMeaningWin.close()
    writeWeights(user, weights, uData)
    return quit

def getUsers():
    users = []
    lastUser = None
    path = os.path.join(os.path.split(os.path.dirname(sys.argv[0]))[0], '.flashcards')
    fPath = os.path.join(path, 'users')
    if os.path.exists(fPath):
        uFile = open(fPath, 'r', encoding="utf8")
        for line in uFile:
            users.append(line.strip('\n'))
            if not len(users[-1]):
                users.pop()
        if len(users):
            if users[-1] in users[:-1]:
                lastUser = users.pop()
            else:
                lastUser = users[-1]
        uFile.close()
    return users, lastUser

def updateUsers(user, users):
    if user not in users and user is not None:
        users.append(user)
    fPath = os.path.join(os.path.split(os.path.dirname(sys.argv[0]))[0], '.flashcards', 'users')
    uFile = open(fPath, 'w', encoding="utf8")
    for u in users:
        uFile.write('%s\n' % u)
    if user is not None:
        uFile.write(user)
    uFile.close()

def copyText(text):
    r = Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(text)
    r.update()
    r.destroy()

def pronunciationHelp(text):
    pinyin = getPinyin(text)[0]
    layout = [
              [sg.Text('%s' % text, font='KaiTi 20', justification='center'), sg.Text(':  %s' % pinyin, font='Arial 18', justification='center')],
              [sg.Button(sound), sg.Button('Copy to clipboard'), sg.Button('Back')]
             ]
    pronunciationHelpWin = sg.Window('抽认卡', layout, element_justification='c', finalize=True)
    read = True
    quit = False
    while True:
        if read:
            tts(text)
            read = False
        event, values = pronunciationHelpWin.read()
        if event in [sg.WIN_CLOSED, 'Back']:
            if event in [sg.WIN_CLOSED]:
                quit = True
            break
        elif event == sound:
            read = True
        if event == 'Copy to clipboard':
            copyText(pinyin)
            sg.popup('Copied "%s" to clipboard' % pinyin, title='抽认卡', font='Arial 12')

    pronunciationHelpWin.close()
    return quit

def cardScoreExtema(cards, user, mode='Best', N=5):
    weights, uData = readWeights(cards, user)
    orderedWeights = {key: value for key, value in sorted(weights.items(), key=lambda item: item[1])}
    list = []
    for hanzi in orderedWeights.keys():
        list.append([hanzi, weights[hanzi]])
    if mode == 'Worst':
        list = list[:N]
    elif mode == 'Best':
        list = list[-N:]
        list.reverse()
    else:
        raise RuntimeError

    return list

def userProfile(cards, user, users):
    quit = False
    userChange = user
    if user is None:
        sg.popup('Please select a user profile', font='Arial 12', title='抽认卡')
        return userChange, quit
    N = 10
    statCLength = math.ceil(43*N/2)
    widest = 30
    bestCards = [[sg.Text('Best %d Cards:' % N, background_color='white', text_color='black', font='Arial 12')]]
    worstCards = [[sg.Text('Worst %d Cards:' % N, background_color='white', text_color='black', font='Arial 12')]]
    bestList = cardScoreExtema(cards, user, mode='Best', N=N)
    worstList = cardScoreExtema(cards, user, mode='Worst', N=N)
    for card in bestList+worstList:
        width = math.ceil(len('%s  %d' % (card[0], card[1]))*2.6)
        if width > widest:
            widest = width
    for card in bestList:
        bestCards.append([sg.Text('%s  %d' % (card[0], card[1]), font='KaiTi 20', background_color='white', text_color='black', size=(width,1))])
    for card in worstList:
        worstCards.append([sg.Text('%s  %d' % (card[0], card[1]), font='KaiTi 20', background_color='white', text_color='black', size=(width,1))])
    best = sg.Column(bestCards, background_color='white', size=(widest*6, statCLength), scrollable=True, vertical_scroll_only=True)
    worst = sg.Column(worstCards, background_color='white', size=(widest*6, statCLength), scrollable=True, vertical_scroll_only=True)
    weights, uData = readWeights(cards, user)
    statsLayout = [
                   [sg.Text('Total cards studied: %d' % (uData['ZH->EN']+uData['EN->ZH']), font='Arial 12')],
                   [sg.Text('汉语 ➡️ En: %d' % uData['ZH->EN'], font='Arial 12'), sg.Text('En ➡️ 汉语: %d' % uData['EN->ZH'], font='Arial 12')],
                   [best, sg.VSeperator(), worst]
                  ]
    settingsLayout = [[sg.Button('Rename profile'), sg.Button('Delete profile')]]
    layout = [
              [sg.Text('User: %s' % user, font='Arial 24', key='_USER_', justification='center', size=(22,1))],#, text_color='black', background_color='white')],
              [sg.TabGroup([[sg.Tab('Statistics', statsLayout), sg.Tab('Settings', settingsLayout) ]])],
              [sg.Button('Back')]
             ]
    userProfileWin = sg.Window('抽认卡 — User Profile', layout, element_justification='c', finalize=True)
    while True:
        event, values = userProfileWin.read()
        if event in [sg.WIN_CLOSED, 'Back']:
            if event in [sg.WIN_CLOSED]:
                quit = True
            break
        elif event == 'Rename profile':
            userChange = sg.popup_get_text('Enter new name for profile "%s":' % user, title='抽认卡', font='Arial 12')
            if userChange not in users:
                weights, uData = readWeights(cards, user)
                writeWeights(userChange, weights, uData)
                path = os.path.join(os.path.split(os.path.dirname(sys.argv[0]))[0], '.flashcards')
                if os.path.exists(os.path.join(path, '%s.profile' % user)):
                    os.remove(os.path.join(path, '%s.profile' % user))
                for u in range(len(users)):
                    if users[u] == user:
                        users.pop(u)
                        break
                user = userChange
                updateUsers(user, users)
                userProfileWin['_USER_'].Update('User: %s' % user)
            else:
                sg.popup('Sorry, the username "%s" already exists.' % userChange, title='抽认卡', font='Arial 12')
        elif event == 'Delete profile':
            if 'Yes' == sg.popup('Are you sure you want to delete your profile, %s?' % user, title='抽认卡', custom_text=('Yes', 'No'), font='Arial 12'):
                path = os.path.join(os.path.join(os.path.split(os.path.dirname(sys.argv[0]))[0], '.flashcards'), '%s.profile' % user)
                if os.path.exists(path):
                    os.remove(path)
            for u in range(len(users)-1, -1, -1):
                if users[u] == user:
                    users.pop(u)
            user = None
            updateUsers(user, users)
            userChange = True
            break
    userProfileWin.close()
    return userChange, quit

def mainGUI(cards):
    quit = False
    if platform.system() == 'Windows':
        sg.SetGlobalIcon(os.path.join(os.path.split(os.path.dirname(sys.argv[0]))[0], '.icon', 'icon.ico'))
    else:
        sg.SetGlobalIcon(os.path.join(os.path.split(os.path.dirname(sys.argv[0]))[0], '.icon', 'icon.png'))
    sg.theme('Dark Red 1')
    bgc = sg.theme_background_color()
    # sg.theme_text_element_background_color(color='white')
    sg.theme_input_background_color(color='white')
    # sg.theme_text_color(color='black')
    bc = sg.theme_button_color()
    sg.theme_button_color(color=('black', bc[1]))
    users, lastUser = getUsers()
    user = lastUser
    layout = [
              [sg.Text('汉字\n抽认卡', font='Arial 48', justification='center')],
              [sg.Text(' Mark "马克" Wootton ', text_color='black', background_color='white', font='Arial 12', justification='right')],
              [sg.Button('Edit Cards'), sg.Button('Study'), sg.Button('Pronunciation')],
              [sg.Text('User:', font='Arial 12'), sg.Combo(users+['{New user}'], default_value=lastUser, key='_USER_', enable_events=True), sg.Button('Profile'), sg.Button('Help')]
             ]
    mainWin = sg.Window('抽认卡', layout, element_justification='c', finalize=True)
    while True:
        event, values = mainWin.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == 'Edit Cards':
            mainWin.hide()
            # quit, cards = editCards(cards)
            while True:
                quit, reopen, cards = editCards(cards)
                if not reopen:
                    break
            if quit:
                break
            mainWin.un_hide()
        elif event == 'Study':
            if user is None:
                sg.popup('Please select a user before beginning study session', font='Arial 12', title='抽认卡')
            else:
                mainWin.hide()
                # studyWhat = getStudyType()
                studyWhat = sg.popup('What do you want to study?', title='抽认卡: 学习什么？', custom_text=('汉字 ➡️ Pinyin & definition', 'Definition ➡️ 汉字'), font='Arial 12')
                if studyWhat == '汉字 ➡️ Pinyin & definition':
                    if studyHanzi(cards, user):
                        break
                elif studyWhat == 'Definition ➡️ 汉字':
                    if studyMeaning(cards, user):
                        break
                mainWin.un_hide()
        elif event == 'Pronunciation':
            text = sg.popup_get_text('Enter text to read:', title='抽认卡', font='Arial 12')
            if text is not None:
                if len(text):
                    # tts(text)
                    mainWin.hide()
                    if pronunciationHelp(text):
                        break
                    mainWin.un_hide()
        elif event == 'Profile':
            mainWin.hide()
            userChange, quit = userProfile(cards, user, users)
            if userChange is True:
                mainWin.FindElement('_USER_').Update('', values=['']+users+['{New user}'])
                user = None
            elif userChange != user:
                user = userChange
                mainWin.FindElement('_USER_').Update(user, values=users+['{New user}'])
            if quit:
                break
            mainWin.un_hide()
        elif event == 'Help':
            mainWin.hide()
            help()
            mainWin.un_hide()
        elif event == '_USER_':
            userInput = values['_USER_']
            if userInput == '':
                userInput = None
            if userInput == '{New user}':
                userInput = sg.popup_get_text('Enter new username:', title='抽认卡', font='Arial 12')
                if userInput is not None:
                    user = userInput
                    updateUsers(user, users)
                mainWin.FindElement('_USER_').Update(user, values=users+['{New user}'])
            else:
                user = userInput
                updateUsers(user, users)

def main():
    mainGUI(cards = readCards())

if __name__ == '__main__':
    main()

# *<img src='.icon/icon.png' width='45' title='Hanzi Flashcards'> Hanzi Flashcards*

Version 1-0<br>
© Mark Wootton 2020

## Dependencies

* [Python 3](https://www.python.org)
  * [tkinter](https://docs.python.org/3/library/tkinter.html) (often pre-installed with Python)
* The follwing third-party libaries
  * [PySimpleGUI](https://pysimplegui.readthedocs.io/en/latest/)
  * [playsound](https://pypi.org/project/playsound)
  * [xpinyin](https://pypi.org/project/xpinyin)
  * [gTTS](https://pypi.org/project/gTTS)
  * [googletrans](https://pypi.org/project/googletrans)
* Installation of the font [KaiTi](https://fontzone.net/font-download/kaiti) is also recommended, but not essential.

Additionally, a Chinese language input method (normally available as part of most operating systems) must be enabled to use the program. Tones can be marked on pinyin input using either diacritics or the [numerical system](https://resources.allsetlearning.com/pronwiki/images/8/85/4-Tones_standard_cropped.png).

## Usage

You can study Chinese character flashcards in two modes:

* see a Chinese character and enter its pinyin and meaning
* see a definition and enter Chinese characters

New flash cards can be made in the “Edit Cards” menu. Click “New card” (or press enter) to add an entry. Right click on an existing card to edit or delete it. Cards can be added en masse from a plain text file by clicking the “Import” button. Input files should be of type *.txt and be structured as follows:

```
汉字一	hàn zì yī	flashcard one
汉字二	hàn zì èr	flashcard two
汉字三	hàn zì sān	flashcard three
```

where each column is separated by a tab. Additionally, hints can be placed in an optional fourth column.

## To Do

- [ ] Add comments to code
- [ ] Add more flashcards
- [ ] Add flashcard categories
- [ ] Test quality of interface
- [ ] Bug hunting




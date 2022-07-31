import json
import re
import pandas as pd

with open("./scrabbleDefs.txt", "r") as inF:

    diceList = "AAEEGN, ELRTTY, AOOTTW, ABBJOO, EHRTVW, CIMOTU, DISTTY, EIOSST, DELRVY, ACHOPS, HIMNQU, EEINSU, EEGHNW, AFFKPS, HLNNRZ, DEILRX".split(", ")

    validLetterCombinationCounts = {}

    for dice in diceList:
        observedLetters = []

        for letter in dice:
            if letter not in observedLetters:
                if letter not in validLetterCombinationCounts:
                    validLetterCombinationCounts[letter] = 1
                else:
                    validLetterCombinationCounts[letter] += 1
                observedLetters.append(letter)

    print(json.dumps(validLetterCombinationCounts, indent=4))

    def keep_word(wordDef):
        # no long words
        if len(wordDef[0]) > 16:
            return False
        if len(wordDef[0]) <= 3:
            return False
        # no words with spaces:
        if " " in wordDef[0]:
            return False
        # no foreign words
        if re.search(r"([(][A-Za-z ]+[)])", wordDef[1]):
            return False
        # only possible words:
        # there are a max number of letters that can appear within a word
        for letter in validLetterCombinationCounts:
            if wordDef[0].count(letter) > validLetterCombinationCounts[letter]:
                return False

        return True

    scrabbleLines = [x.replace("\n", "").split("\t") for x in inF]

    print("before: ", len(scrabbleLines))

    scrabbleLines = [x for x in scrabbleLines if keep_word(x)]

    scrabbleLines = list(sorted(scrabbleLines, key=lambda x: x[0], reverse=False))

    scrabbleDF = pd.DataFrame(scrabbleLines, columns=["word", "definition"])

    scrabbleDF.to_csv('wordGridDF.csv', index=False)

    print("afterr: ", len(scrabbleLines))

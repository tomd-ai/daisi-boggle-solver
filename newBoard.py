from random import choice, shuffle
import pandas as pd

def genNewBoard():
    availableOptions = "AAEEGN, ELRTTY, AOOTTW, ABBJOO, EHRTVW, CIMOTU, DISTTY, EIOSST, DELRVY, ACHOPS, HIMNQU, EEINSU, EEGHNW, AFFKPS, HLNNRZ, DEILRX".split(", ")
    availableOptions = [ list(x) for x in availableOptions]
    shuffle(availableOptions)

    tilePlacement = pd.DataFrame(
        {
            "A": [""]*4,
            "B": [""]*4,
            "C": [""]*4,
            "D": [""]*4
        }
    )

    for col in list(tilePlacement):
        for rowInd in range(0, 4):
            diceOption = availableOptions[-1]
            tilePlacement.at[rowInd, col] = choice(diceOption)
            availableOptions.pop()

    return tilePlacement

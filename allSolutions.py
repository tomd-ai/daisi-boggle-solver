from collections import Counter
from itertools import chain
from tqdm import tqdm
import pandas as pd

class TrieNode:
    def __init__(self, text=""):
        self.text = text
        self.children = dict()
        self.is_word = False


class PrefixTree:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        current = self.root
        for i, char in enumerate(word):
            if char not in current.children:
                prefix = word[0:i+1]
                current.children[char] = TrieNode(prefix)
            current = current.children[char]
        current.is_word = True

    def find(self, word):
        current = self.root
        for char in word:
            if char not in current.children:
                return None
            current = current.children[char]

        if current.is_word:
            return current

    def __child_words_for(self, node, words):
        '''
        Private helper function. Cycles through all children
        of node recursively, adding them to words if they
        constitute whole words (as opposed to merely prefixes).
        '''
        if node.is_word:
            words.append(node.text)
        for letter in node.children:
            self.__child_words_for(node.children[letter], words)

    def starts_with(self, prefix):
        '''
        Returns a list of all words beginning with the given prefix, or
        an empty list if no words begin with that prefix.
        '''
        words = list()
        current = self.root
        for char in prefix:
            if char not in current.children:
                # Could also just return words since it's empty by default
                return list()
            current = current.children[char]

        # Step 2
        self.__child_words_for(current, words)
        return words

    def size(self, current=None):
        '''
        Returns the size of this prefix tree, defined
        as the total number of nodes in the tree.
        '''
        # By default, get the size of the whole trie, starting at the root
        if not current:
            current = self.root
        count = 1
        for letter in current.children:
            count += self.size(current.children[letter])
        return count


def gen_game_board(gameData):
    return dict(
        A1=dict(
            diceID="A1",
            letter=gameData.at[0, "A"],
            neighbours=["A2", "B1", "B2"]
        ),
        A2=dict(
            diceID="A2",
            letter=gameData.at[0, "B"],
            neighbours=["A1", "B1", "B2", "B3", "A3"]
        ),
        A3=dict(
            diceID="A3",
            letter=gameData.at[0, "C"],
            neighbours=["A2", "B2", "B3", "B4", "A4"]
        ),
        A4=dict(
            diceID="A4",
            letter=gameData.at[0, "D"],
            neighbours=["A3", "B3", "B4"]
        ),
        B1=dict(
            diceID="B1",
            letter=gameData.at[1, "A"],
            neighbours=["A1", "A2", "B2", "C2", "C1"]
        ),
        B2=dict(
            diceID="B2",
            letter=gameData.at[1, "B"],
            neighbours=["A1", "A2", "A3", "B3", "C3", "C2", "C1", "B1"]
        ),
        B3=dict(
            diceID="B3",
            letter=gameData.at[1, "C"],
            neighbours=["A2", "A3", "A4", "B2", "C2", "C3", "C4", "B4"]
        ),
        B4=dict(
            diceID="B4",
            letter=gameData.at[1, "D"],
            neighbours=["A3", "A4", "B3", "C3", "C4"]
        ),
        C1=dict(
            diceID="C1",
            letter=gameData.at[2, "A"],
            neighbours=["B1", "B2", "C2", "D2", "D1"]
        ),
        C2=dict(
            diceID="C2",
            letter=gameData.at[2, "B"],
            neighbours=["B1", "B2", "B3", "C3", "D3", "D2", "D1", "C1"]
        ),
        C3=dict(
            diceID="C3",
            letter=gameData.at[2, "C"],
            neighbours=["B2", "B3", "B4", "C4", "D4", "D3", "D2", "C2"]
        ),
        C4=dict(
            diceID="C4",
            letter=gameData.at[2, "D"],
            neighbours=["B3", "B4", "C3", "D3", "D4"]
        ),
        D1=dict(
            diceID="D1",
            letter=gameData.at[3, "A"],
            neighbours=["C1", "C2", "D2"]
        ),
        D2=dict(
            diceID="D2",
            letter=gameData.at[3, "B"],
            neighbours=["C1", "C2", "C3", "D3", "D1"]
        ),
        D3=dict(
            diceID="D3",
            letter=gameData.at[3, "C"],
            neighbours=["D2", "C2", "C3", "C4", "D4"]
        ),
        D4=dict(
            diceID="D4",
            letter=gameData.at[3, "D"],
            neighbours=["C3", "C4", "D3"]
        )
    )


def solve_wall(gameData):

    gameBoard = gen_game_board(gameData)

    allLetters = list(chain.from_iterable(gameData.values.tolist()))

    validLetters = set(allLetters)
    validLetterDistribution = Counter(allLetters)

    wordGridDF = pd.read_csv("wordgrid.csv")
    wordGridDF.fillna("", inplace=True)

    # filter the dictionary to make it a bit smaller

    def keep_word(word):
        # for the blank ones
        if not word:
            return False
        # check if there are illegal letters (less expensive than counting)
        for letter in word:
            if letter not in validLetters:
                return False
        # no illegal letters - check if its possible
        for letter in validLetterDistribution:
            if word.count(letter) > validLetterDistribution[letter]:
                return False

        return True

    # possible - contains the right distribution of letters

    wordGridDF["possibleWord"] = wordGridDF["word"].apply(keep_word)
    
    possibleWordList = wordGridDF.loc[(wordGridDF["possibleWord"] == True), :]
    # make the trie

    trie = PrefixTree()

    [trie.insert(x) for x in possibleWordList["word"]]

    def test_prefix(prefix):
        validWordList = trie.starts_with(prefix)

        if not validWordList:
            return "b", None
        if prefix in validWordList:
            if len(validWordList) > 1:
                return "c", prefix
            else:
                return "b", prefix
        else:
            return "c", None

    def score_word(word):
        if len(word) == 4:
            return 1
        if len(word) == 5:
            return 2
        if len(word) == 6:
            return 3
        if len(word) == 7:
            return 5
        else:
            return 11

    solutions = dict()

    def depth_first_search(diceID, vistitedPath, currentCombinations):
        letter = gameBoard[diceID]["letter"]
        vistitedPath.append(diceID)

        currentCombinations += letter

        testRes, wholeWord = test_prefix(currentCombinations)

        if wholeWord:
            solutions[wholeWord] = {
                "path": vistitedPath,
                "score": score_word(wholeWord)
            }

        if "b" in testRes:
            return

        current_neighbours = gameBoard[diceID]["neighbours"]

        for neighbour in current_neighbours:
            if neighbour not in vistitedPath:
                depth_first_search(neighbour, vistitedPath.copy(), currentCombinations)

    for startDice in tqdm(gameBoard):

        depth_first_search(startDice, [], "")

    orderedSolutions = []

    for solution in solutions:
        orderedSolutions.append(
            {
                "word": solution,
                "score": solutions[solution]["score"],
                "path": solutions[solution]["path"],
                "definition": possibleWordList.loc[
                    (possibleWordList["word"] == solution),
                    "definition"
                ].tolist()[0]
            }
        )

    orderedSolutions = list(sorted(orderedSolutions, key=lambda x: len(x["word"]), reverse=True))

    # print(json.dumps(orderedSolutions, indent=4))

    return orderedSolutions

# import cProfile, pstats

# if __name__ == "__main__":

#     wordGridDF = pd.read_csv("wordGridDF.csv")
#     wordGridDF.fillna("", inplace=True)

#     profiler = cProfile.Profile()
#     profiler.enable()
#     solve_wall(
#         wordGridDF,
#         gameData={
#             "A1": "N",
#             "A2": "S",
#             "A3": "S",
#             "A4": "O",
#             "B1": "F",
#             "B2": "R",
#             "B3": "N",
#             "B4": "L",
#             "C1": "E",
#             "C2": "I",
#             "C3": "J",
#             "C4": "E",
#             "D1": "L",
#             "D2": "Z",
#             "D3": "H",
#             "D4": "O"
#         }
#     )
#     profiler.disable()
#     stats = pstats.Stats(profiler).sort_stats('cumtime')
#     stats.print_stats()

#  N S S O
#  F R N L
#  E I J E
#  L Z H O

# A1 A2 A3 A4
# B1 B2 B3 B4
# C1 C2 C3 C4
# D1 D2 D3 D4
import streamlit as st
from st_aggrid import AgGrid
from packages.allSolutions import solve_wall
from packages.newBoard import genNewBoard
import pandas as pd

blankBoard = {
    'A': ["", "", "", ""],
    'B': ["", "", "", ""],
    'C': ["", "", "", ""],
    'D': ["", "", "", ""],
}

if __name__ == "__main__":
    st.set_page_config(layout = "wide")

    st.title("Boggle solver")

    st.write("Uses the power of tries to solve boggle grids.")
    st.write("Double click each cell to fill in your grid, then press solve.")
    st.write("Click the generate random board button if you just want to see it in action.")

    col1,col2,col3 = st.columns(3)
    randomBoard = col1.button(
        label="Generate random board",
    )
    clearBoard = col2.button(
        "Clear board"
    )
    solve = col3.button(
        "Solve"
    )

    if 'boardLayout' not in st.session_state:
        st.session_state['boardLayout'] = pd.DataFrame(blankBoard)
        st.session_state['reloadData'] = False
    
    if "boardAnswers" not in st.session_state:
        st.session_state['boardAnswers'] = None
        st.session_state['selectedPath'] = None

    if randomBoard:
        print("random board clicked")
        boardLayout = genNewBoard()
        st.session_state['boardLayout'] = pd.DataFrame(boardLayout)
        st.session_state['reloadData'] = True
        st.session_state['boardAnswers'] = None
        st.session_state['selectedPath'] = None

    if clearBoard:
        print("clear board clicked")
        st.session_state['boardLayout'] = pd.DataFrame(blankBoard)
        st.session_state['reloadData'] = True
        st.session_state['boardAnswers'] = None
        st.session_state['selectedPath'] = None

    if solve:
        print("solve clicked")
        allAnswers = solve_wall(st.session_state["boardLayout"])
        st.session_state['boardAnswers'] = allAnswers

    customCss = {
        '.ag-header': {
            "display": "none"
        },
        '.ag-cell': {
            'text-align': "center !important",
            'border': 'solid 1px black !important'
        }
    }

    if st.session_state["selectedPath"] is not None:
        # print(st.session_state["selectedPath"])
        for rowCol in st.session_state["selectedPath"]:
            # because the refs are transposed
            agRefRow = list("ABCD").index(rowCol[0])
            agRefCol = list("ABCD")[list("1234").index(rowCol[1])]

            customCss[f'.ag-row[row-id="{agRefRow}"] .ag-cell[col-id="{agRefCol}"]'] = {
                "background-color": "black !important",
                "color": "white !important"
            }

        st.session_state["reloadData"] = True

    grid_return = AgGrid(
        st.session_state["boardLayout"],
        editable=True,
        fit_columns_on_grid_load=True,
        theme="material",
        custom_css=customCss,
        height=200,
        reload_data=True,
        update_mode='model_changed'
    )

    new_df = grid_return['data']
    new_df = new_df.apply(lambda x: x.str.upper())

    if not st.session_state["boardLayout"].equals(new_df):
        print(st.session_state["boardLayout"])
        st.session_state["boardLayout"] = new_df
        st.experimental_rerun()

    if st.session_state['boardAnswers'] is not None:
        boardAnswers = pd.DataFrame(st.session_state['boardAnswers'])

        st.write("Select a word to display its location on the grid")
        
        def update_selected_path():
            st.session_state["selectedPath"] = boardAnswers.loc[
                boardAnswers.word == st.session_state.word
            ]["path"].iloc[0]
            st.experimental_rerun()

        word = st.selectbox(
            "Select word",
            boardAnswers["word"],
            key="word"
        )

        newPath = boardAnswers.loc[
            boardAnswers.word == word
        ]["path"].iloc[0]

        if st.session_state["selectedPath"] != newPath:
            st.session_state["selectedPath"] = newPath
            st.experimental_rerun()

        resp = AgGrid(
            boardAnswers.loc[:, ["word", "score", "definition"]],
            editable=False,
            theme="material",
            fit_columns_on_grid_load=True
        )


import pandas as pd
import os

def found_white_space(df: pd.DataFrame, white_name: any, column_name: str, percentege_or_count: bool = True):
    ''' return count if true and df if is false
    '''
    white_spaces = df[df[column_name] == white_name]
    tam_white = len(white_spaces)
    return tam_white/len(df) if (percentege_or_count) else tam_white

def get_max_values_for_groups(df: pd.DataFrame, column_group: str, target_column, ascending_order: bool = False):

    max_values = df.groupby(column_group)[target_column].max().reset_index()

    return max_values.sort_values([target_column], ascending=ascending_order)

def get_files_full_path(path):
    files_tot = []
    for p, _, files in os.walk(os.path.abspath(path)):
        for file in files:
            files_tot.append(os.path.join(p, file))

    return files_tot

def remove_white_space_by_proximity(df: pd.DataFrame):
    all_white_spaces_positions = []
    for index, val in df.iterrows():
        tam = len(df) - 1
        if val["token"] == "WHITESPACE":
            if (index == tam):
                df.at[index - 1, "duration"] = df.at[index -1, "duration"] + val["duration"]
            
            elif (index == 0):
                df.at[index + 1, "duration"] = df.at[index + 1, "duration"] + val["duration"]
            
            else:
                upper_distance = df.at[index + 1, "source_file_line"] - val["source_file_line"] + df.at[index + 1,"source_file_col"] - val["source_file_col"]
                lower_distance = df.at[index - 1,"source_file_line"] - val["source_file_line"] + df.at[index - 1,"source_file_col"] - val["source_file_col"]

                if (lower_distance > upper_distance):
                    df.at[index + 1,"duration"] = df.at[index + 1,"duration"] + val["duration"]
                else:
                    df.at[index - 1,"duration"] = df.at[index - 1,"duration"] + val["duration"]
            all_white_spaces_positions.append(index)

    df.drop(all_white_spaces_positions, axis=0, inplace = True)
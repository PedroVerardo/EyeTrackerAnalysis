import sqlite3
import pandas as pd
import utilities as ut
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from scipy.stats import gaussian_kde
import numpy as np
import json

class Question:
    def __init__(self, full_path) -> None:
        self.full_path: str = full_path
        self.question_number: str = full_path.split("\\")[-2]
        self.experiment_number: str = full_path.split("\\")[-4].split(" ")[-1]
        self.total_size: int = None
        self.white_spaces_percentage: float = None
        self.nan_percentage: float = None
        self.white_spaces_count: int = None
        self.connection: sqlite3.Connection = None
        self.data_frame: pd.DataFrame = None
        self.time_to_complete: float = None
        self.most_readed_types: dict = {}
        self.variance: float = None
        self.get_most_readed_types()
        self.smell = self.set_smell(self.question_number)
        self.most_readed_lines = None

    def connect(self):
        try:
            con = sqlite3.connect(self.full_path)
            self.connection = con
        except:
            print("Não foi possivel encontrar o database, favor verificar o caminho passado")
            print(" -> Se seu caminho estiver usando apenas uma '/' troque para '//', isso pode solucionar o problema")

    def clean_data(self):
        if self.connection == None:
            self.connect()

        elif self.data_frame is not None:
            return

        print(self.experiment_number, self.question_number)
        self.data_frame = pd.read_sql_query("SELECT * from fixation", self.connection)
        self.total_size = len(self.data_frame)
        self.white_spaces_percentage = ut.found_white_space(self.data_frame, "WHITESPACE", "token")
        self.white_spaces_count = ut.found_white_space(self.data_frame, "WHITESPACE", "token", False)
        ut.remove_white_space_by_proximity(self.data_frame)

        df_ide = pd.read_sql_query("SELECT time_stamp from ide_context", self.connection)
        
        time_difference = datetime.fromtimestamp(int(df_ide['time_stamp'].max())/1000) - datetime.fromtimestamp(int(df_ide['time_stamp'].min())/1000)
        self.time_to_complete = int(time_difference.total_seconds())

        self.variance = self.data_frame['source_file_line'].var() + self.data_frame['source_file_col'].var()

    def generate_tsv_file(self):
        if self.connection == None:
            self.connect()

        sql = "SELECT x as start_x, y as start_y, duration from fixation"
        
        df = pd.read_sql_query(sql, self.connection)
        df.to_csv(self.full_path[:-8]+"question_"+self.question_number+".tsv", sep='\t', index=False)

    def plot_most_readed_lines(self, qtd_elements: int = 5, save_plot: bool = False, save_data: bool = False):
        grouped_data = self.data_frame.groupby('source_file_line')['duration'].sum()
        top_tokens = grouped_data.nlargest(qtd_elements)
        if save_data:
            self.most_readed_lines = top_tokens
        else:
            bars = top_tokens.plot(kind='bar')
            plt.title(f"Top {qtd_elements} Most Read Lines")
            plt.xlabel('Source File Line')
            plt.ylabel('Total Duration')
            plt.xticks(rotation=30)

            for rect in bars.patches:
                height = rect.get_height()
                plt.text(rect.get_x() + rect.get_width() / 2, height, round(height, 2), ha='center', va='bottom')

            if save_plot:
                plt.savefig(f"Top {qtd_elements} Most Read Lines{self.question_number}.png")
            else:
                plt.show()

    def plot_most_readed_tokens(self, qtd_elements: int = 5, save_plot: bool = False):
        grouped_data = self.data_frame.groupby('token')['duration'].sum()
        top_tokens = grouped_data.nlargest(qtd_elements)
        bars = top_tokens.plot(kind='bar')
        plt.title(f"Top {qtd_elements} Most Read Tokens")
        plt.xlabel('Tokens')
        plt.ylabel('Total Duration')

        for rect in bars.patches:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width() / 2, height, round(height, 2), ha='center', va='bottom')

        plt.xticks(rotation=30)
        if save_plot:
            plt.savefig(f"Top {qtd_elements} Most Read Tokens{self.question_number}.png")
        else:
            plt.show()

    def plot_most_readed_programming_types(self, qtd_elements: int = 5, save_plot: bool = False):
        self.clean_data()

        areas = "our_tokenization/"+self.question_number+"_Code_Snippet.csv"

        df = pd.read_csv(areas)

        merged_data = pd.merge(self.data_frame, df, left_on='source_file_line', right_on='Linha')

        grouped_data = merged_data.groupby('Descricao')['duration'].sum().sort_values(ascending=False).head(qtd_elements)

        bars = grouped_data.plot(kind='bar')
        plt.title(f"Top {qtd_elements} Most Read Tokens")
        plt.xlabel('Tokens')
        plt.ylabel('Total Duration')

        for rect in bars.patches:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width() / 2, height, round(height, 2), ha='center', va='bottom')

        plt.xticks(rotation=30)
        if save_plot:
            plt.savefig(f"Top {qtd_elements} Most Read Tokens{self.question_number}.png")
        else:
            plt.show()

    def plot_eye_path_ide(self, save_plot: bool = False):
        if self.connection == None:
            self.connect()

        df = pd.read_sql_query("SELECT * from ide_context", self.connection)
        df = df.sort_values(by='time_stamp')

        dx = df['x'].diff().fillna(0)
        dy = df['y'].diff().fillna(0)

        plt.figure(figsize=(10, 10))
        plt.quiver(df['x'], df['y'], dx, dy, angles='xy', scale_units='xy', scale=1)
        plt.title("Sequence of Points")
        plt.xlabel('X')
        plt.ylabel('Y')
        if save_plot:
            plt.savefig(f"Question{self.question_number}_Path.png")
        else:
            plt.show()

    def get_most_readed_types(self):
        self.clean_data()

        if self.question_number == "01":
            return
        
        if len(self.most_readed_types) != 0:
            return self.most_readed_types

        areas = "our_tokenization/"+self.question_number+"_Code_Snippet.csv"

        df = pd.read_csv(areas)
        
        snippet_upper_limit = df['Linha'].max()
        snippet_lower_limit = df['Linha'].min()
        

        merged_data = pd.merge(self.data_frame, df, left_on='source_file_line', right_on='Linha')

        grouped_data = merged_data.groupby('Descricao')['duration'].sum().sort_values(ascending=False)

        self.most_readed_types = grouped_data.to_dict()

        self.most_readed_types['out'] = 0

        for index, row in self.data_frame.iterrows():
            if row['source_file_line'] > snippet_upper_limit or row['source_file_line'] < snippet_lower_limit:
                 self.most_readed_types['out'] += row['duration']
        
        return self.most_readed_types

    def get_reread_info(self):
        self.clean_data()
        ant = 0
        count = 0
        areas = "our_tokenization/"+self.question_number+"_Code_Snippet.csv"
        df = pd.read_csv(areas)
        merged_data = pd.merge(self.data_frame, df, left_on='source_file_line', right_on='Linha')
        result = {}
        for index, row in merged_data.iterrows():
            if row['source_file_line'] < ant or (row['source_file_line'] == ant and row['source_file_col'] < ant):
                if row['Descricao'] in result:
                    result[row['Descricao']] += 1
                else:
                    result[row['Descricao']] = 1
            ant = row['source_file_line']

        print(result)
        return 

    def plot_white_spaces_percentage(self, save_plot: bool = False):
        pie_data = [self.total_size, self.white_spaces_count]
        names = ["Valid values", "White spaces"]
        explode = [0.2,0]


        plt.pie(pie_data,
                labels=names,
                explode=explode,
                shadow = False,
                startangle = 30,
                autopct='%1.1f%%',
                colors = sns.color_palette('coolwarm')
                )
        
        plt.title(f"White spaces percentage in question {self.question_number}")
        plt.axis('equal')
        if save_plot:
            plt.savefig(f"pieOfwhiteIncidence_E{self.experiment_number}_Q{self.question_number}.png", dpi = 150)
        else:
            plt.show()

    def plot_eye_path_fixation(self, color: str = 'black', alpha: float = 0.5, save_plot: bool = False):
        if self.connection == None:
            self.connect()

        df = pd.read_sql_query("SELECT * from fixation", self.connection)
        df = df.sort_values(by='fixation_order_number', ascending=True)


        plt.figure(figsize=(10, 10))
        cont = 0
        for index, row in df.iterrows():
            if cont != 0 and row['fixation_start_event_time'] - (ant['fixation_start_event_time'] + ant['duration']*(10**6))  < 0:
                plt.quiver(ant['source_file_col'], ant['source_file_line'], 
                       row['source_file_col'] - ant['source_file_col'], 
                       row['source_file_line'] - ant['source_file_line'], 
                       angles='xy', scale_units='xy', scale=1, color=color, alpha=alpha)
            plt.scatter(row['source_file_col'],row['source_file_line'] , s=row['duration'], color='red', alpha=alpha)
            #plt.text(row['source_file_col'],row['source_file_line'] , row['duration'], color='white', ha='center', va='center')
            ant = row
            cont+=1
            

        
        #plt.quiver(df['source_file_line'], df['source_file_col'], dx, dy, angles='xy', scale_units='xy', scale=1, color=color,
                   #alpha=alpha)
        plt.title("Sequence of Points")
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.show()

    def get_variance(self):
        return self.variance
    
    def set_smell(self, q_number):
        with open('codes\info.json') as f:
            data = json.load(f)
            return data[q_number]["smell"]

    def get_density(self):
        data = np.vstack([self.data_frame['source_file_line'], self.data_frame['source_file_col']])

        kde = gaussian_kde(data)

        density = kde([self.data_frame['source_file_line'].max(), self.data_frame['source_file_col'].max()])

        print(density)
        
if __name__ == "__main__":
    q = Question("experimentos\\Experimento 05\\Sem Dejavu\\02\\db02.db3")
    q.clean_data()
    # q.plot_eye_path_fixation()
    # q.generate_tsv_file()
    # q.plot_most_readed_programming_types()
    # q.plot_eye_path_fixation()
    q.plot_most_readed_lines()
    print(q.get_variance())
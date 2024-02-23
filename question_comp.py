import os
from questionType import Question
import matplotlib.pyplot as plt
import numpy as np
import multimatch_gaze as m
from scipy.stats import chi2
import pandas as pd
import tqdm
import plotly.express as px
import plotly.graph_objects as go
import json

class QuestionComparision:
    def __init__(self, experiments_dir: str) -> None:
        
        self.experiments_dir = experiments_dir
        self.questions = {}
        self.list_of_fix_vectors = {}

    def get_questions_for_experiments(self) -> None:
        """This functin is very specific for the experiments directory structure.
        It's important to note that the experiments directory must have the following structure:
        experiments_dir
            experiment 1
                Sem Dejavu
                    01
                    02

        Returns:
            dict: A dict composed by the experiments as keys and the questions objects
        """        
        for experiment in os.listdir(self.experiments_dir):
            experiment_path = os.path.join(self.experiments_dir, experiment)
            if os.path.isdir(experiment_path):
                self.questions[experiment] = []
                for dejavu in os.listdir(experiment_path):
                    dejavu_path = os.path.join(experiment_path, dejavu)
                    if os.path.isdir(dejavu_path) and dejavu == "Sem Dejavu":
                        for question_dir in os.listdir(dejavu_path):
                            question_path = os.path.join(dejavu_path, question_dir)
                            if os.path.isdir(question_path):
                                for java_file in os.listdir(question_path):
                                    java_file_path = os.path.join(question_path, java_file)
                                    if java_file.endswith(".db3"):
                                        self.questions[experiment].append(Question(java_file_path))

    def generate_tsv_files(self) -> None:
        """
        Generates TSV files for each question in the self.questions.

        This method reads all .db3 files in the current directory and generates a TSV file for each one.
        Each TSV file contains the data associated with a question, with the data fields separated by tabs.

        Returns:
            None

        """
        for key in self.questions:
            for question in self.questions[key]:
                question.clean_data()
                question.generate_tsv_file()

    def plot_question_time_comparison_for_one_experiment(self, experiment: int) -> None:
        """This function plots the time spent in each question for a specific experiment.
        Args:
            experiment (int): The number of the experiment to be plotted.
        """
        if experiment < 10:
            experiment = "0" + str(experiment)
        else:
            experiment = str(experiment)

        plt.figure(figsize=(10, 5))

        for question in self.questions["Experimento "+experiment]:
            question.clean_data()
            bar = plt.bar(question.question_number, question.time_to_complete, 0.7, color='red')
            for rect in bar:
                height = rect.get_height()
                plt.text(rect.get_x() + rect.get_width() / 2, height, str(int(height)), ha='center', va='bottom')
        

        plt.title(f"Time spent in questions Experiment: {experiment}(seconds)")
        plt.xlabel('Question number')
        plt.ylabel('Time spent in seconds')

        plt.grid(visible= True, color ='grey',
        linestyle ='-.', linewidth = 0.5,
        alpha = 0.6)

        plt.show()

    def plot_question_time_comparison_for_all_experiments(self) -> None:
        """This function plots the time spent in each question for all experiments,
        in a single plot.
        """
        plt.figure(figsize=(10, 5))
        
        for experiment in self.questions:
            print(experiment)
            cont = 0
            for question in self.questions[experiment]:
                cont += 1
                print(cont)
                question.clean_data()
                bar = plt.bar(question.question_number, question.time_to_complete, 0.7, color='red')
                for rect in bar:
                    height = rect.get_height()
                    plt.text(rect.get_x() + rect.get_width() / 2, height, str(int(height)), ha='center', va='bottom')
        
        plt.title(f"Time spent in questions (seconds)")
        plt.xlabel('Question number')
        plt.ylabel('Time spent in seconds')

        plt.grid(visible= True, color ='grey',
        linestyle ='-.', linewidth = 0.5,
        alpha = 0.6)

        plt.show()

    def diff_eye_position_for_one_question(self, question_number: int) -> None:
        """This function compares the eye position for a specific question in all experiments.
        Args:
            question_number (int): The number of the question to be compared.
        """
        if question_number < 10:
            question_number = "0" + str(question_number)
        else:
            question_number = str(question_number)

        vector_list = {}
        for key in self.questions:
            for q in self.questions[key]:
                if q.question_number == question_number:
                    
                    csv_path = f"{q.full_path[:-8]}question_{q.question_number}.tsv"
                    print(csv_path)
                    try:
                        fix_vector1 = np.recfromcsv(csv_path, delimiter='\t',
                        dtype={'names': ('start_x', 'start_y', 'duration'),
                        'formats': ('f8', 'f8', 'f8')})
                        vector_list[f'{key}-{q.question_number}'] = fix_vector1

                    except:
                        print(f"{q.question_number} not found in experiment {key}")

        tam = len(vector_list.keys())
        keys = list(vector_list.keys())
        #print (tam)
        for i in range(tam - 1):
            for j in range(i+1, tam):
                key1 = keys[i]
                key2 = keys[j]

                # Get the values
                value1 = vector_list[key1]
                value2 = vector_list[key2]
                self.list_of_fix_vectors[f"{key1} x {key2}"] = m.docomparison(value1, value2, screensize=[1080, 720])
                print(self.list_of_fix_vectors)

    def plot_diff_eye_position_for_one_question(self, question_number:int, experimentA: int, experimentB: int, consider_duration: bool = False) -> None:
        """
        Plots the difference in eye position for a specific question between two experiments.

        Args:
            question_number (int): The number of the question.
            experimentA (int): The number of the first experiment.
            experimentB (int): The number of the second experiment.
            consider_duration (bool, optional): Whether to consider the duration of eye positions. Defaults to False.
        """
            
        if question_number < 10:
            question_number = "0" + str(question_number)
        else:
            question_number = str(question_number)

        if experimentA < 10:
            experimentA = "0" + str(experimentA)
        else:
            experimentA = str(experimentA)

        if experimentB < 10:
            experimentB = "0" + str(experimentB)
        else:
            experimentB = str(experimentB)

        qa = None
        qb = None
        try:
            for q in self.questions["Experimento "+experimentA]:
                if q.question_number == question_number:
                    qa = q
                    break
            if qa == None:
                print(f"Question {question_number} not found")
                return
        except:
            print(f"Experiment {experimentA}  not found")
            return
            
        try:
            for q in self.questions["Experimento "+experimentB]:
                if q.question_number == question_number:
                    qb = q
                    break
            if qb == None:
                print(f"Question {question_number} not found")
                return
        except:
            print(f"Experiment {experimentB} not found")
            return
            
        qa.clean_data()
        qb.clean_data()
        dfa = qa.data_frame
        dfb = qb.data_frame
        for index, row in dfa.iterrows():
            if consider_duration:
                s = row['duration']
            else:
                s = None
            plt.scatter(row['source_file_col'], row['source_file_line'], s=s, color='yellow', alpha=0.7)
            
        for index, row in dfb.iterrows():
            if consider_duration:
                s = row['duration']
            else:
                s = None
            plt.scatter(row['source_file_col'], row['source_file_line'], s=s, color='purple', alpha=0.7)
            
        plt.show()
    
    def plot_white_spaces_percentage(self, experiment: int) -> None:
        """
        Plots the white spaces percentage for each question in a given experiment.

        Args:
            experiment (int): The experiment number.

        Returns:
            None
        """

        if experiment < 10:
            experiment = "0" + str(experiment)
        else:
            experiment = str(experiment)

        plt.figure(figsize=(10, 5))

        for question in self.questions["Experimento "+experiment]:
            question.clean_data()
            print(question.white_spaces_count)
            plt.bar(question.question_number, question.white_spaces_count, 0.7, color='red')
            plt.bar(question.question_number, question.total_size, 0.7, color='blue', bottom=question.white_spaces_count)
        
        plt.title(f"White spaces percentage in experiment {experiment}")
        plt.xlabel('Question number')
        plt.ylabel('Dataset size')

        plt.grid(visible= True, color ='grey',
        linestyle ='-.', linewidth = 0.5,
        alpha = 0.6)

        plt.show()
    
    def plot_mean_of_most_readed_tokens(self) -> None:
        """
        Plots the total of the most readed tokens.

        This function calculates the total of the most readed tokens for each question in the experiment.
        It then plots a bar chart showing the total duration spent on each token.

        #To-do: make a mean version of this function
        # the mean not represent the total time spent in each token, because each question have different tokens

        Returns:
            None
        """
        result = {}
        for experiment in self.questions:
            for question in self.questions[experiment]:
                question.clean_data()
                for key in question.most_readed_types:
                    if key in result:
                        result[key] += question.most_readed_types[key]
                    else:
                        result[key] = question.most_readed_types[key]

        result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))
        plt.title("total time spent in each token")
        bars = plt.bar(result.keys(), result.values())

        plt.xlabel('Tokens')
        plt.ylabel('Total Duration')

        for rect in bars.patches:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width() / 2, height, round(height, 2), ha='center', va='bottom')

        plt.xticks(rotation=30)
        # Show the plot
        plt.show()

    def plot_scatter_error_and_success(self, answer_path: str = 'respostas.csv') -> None:
        """
        Plots scatter plots for error and success based on the given answer csv file.

        Args:
            answer_path (str): The path to the answer file (default is 'respostas.csv').

        Returns:
            None
        """
        result = {}

        df = pd.read_csv(answer_path)
        color = 'r'
        for experiment in self.questions:
            for question in self.questions[experiment]:
                if question.question_number != "01":   
                    if question.question_number in result:
                        result[question.question_number].append(question)
                    else:
                        result[question.question_number] = [question]

        for question in result:
            for experiment_question in tqdm.tqdm(result[question]):
                new_df = df.loc[(df['questao'] == int(experiment_question.question_number))]
                new_df = new_df.loc[(new_df['Experimento'] == int(experiment_question.experiment_number))]['acerto'].values

                if new_df[0]:
                    color = 'g'
                else:
                    color = 'r'
                for index, row in experiment_question.data_frame.iterrows():
                    plt.scatter(row['source_file_col'], row['source_file_line'], color=color, alpha=0.3,)
            plt.gca().invert_yaxis()
            plt.savefig(f'error_x_success{experiment_question.question_number}.png',dpi=400)
            plt.clf()

    def get_colors(self, smell, severity) -> tuple[int]:
        """
        Get the normalized RGB color based on the given smell and severity.

        This function is an auxiliary function used by another function.

        Args:
            smell (str): The type of smell.
            severity (str): The severity level of the smell.

        Returns:
            tuple: The normalized RGB color as a tuple of three values between 0 and 1.
        """
        if severity == "minor":
            severity = 2
        elif severity == "major":
            severity = 3
        elif severity == "critical":
            severity = 4
        else:
            severity = 1

        if smell == "data class":
            rgb_color = [0, 0, 255]
        elif smell == "feature envy":
            rgb_color = [0, 255, 0]
        elif smell == "long method":
            rgb_color = [255, 0, 0]
        normalized_rgb_color = tuple(value/severity / 255 for value in rgb_color)
        return normalized_rgb_color
    
    def generate_colors_by_question_and_severity(self, path: str, order: list[str]) -> list[tuple]:
        """This function generate a dict, reading a json, with the colors for each question, and use the severity to define 
        the tonality of the color.

        Json example:
        {
        "02": {
            "smell": "data class",
            "severity": "minor"
        },
        "03": {
            "smell": "feature envy",
            "severity": "major"
        }
        """
        result = []
        with open(path) as f:
            data = json.load(f)

        for key in order:
            key = key.split("_")[1]
            info = data[key]
            color = self.get_colors(info["smell"], info["severity"])
            result.append(color)
        print(len(result))

        return result
                    
    def boxplot_of_time_questions(self, path: str) -> None:
        """
        Generates a boxplot of the time spent to complete each question.

        Args:
            path (str): The path to the directory where the boxplot image will be saved.

        Returns:
            None
        """
        result = {}
        for experiment in self.questions:
            for question in self.questions[experiment]:
                question.clean_data()
                if question.question_number != "01":
                    if question.time_to_complete > 1500:
                        continue
                    if question.smell[:2]+"_"+question.question_number in result:
                        result[question.smell[:2]+"_"+question.question_number].append(question.time_to_complete)
                    else:
                        result[question.smell[:2]+"_"+question.question_number] = [question.time_to_complete]

        plt.xlabel('question_number')
        plt.ylabel('time spent in seconds')
        plt.title('Time per question')

        items = sorted(result.items())
        keys = [item[0] for item in items]
        values = [item[1] for item in items]

        box = plt.boxplot(values, patch_artist=True, labels=keys)

        colors = self.generate_colors_by_question_and_severity(path, keys)
        colors = colors
        colors2 = colors.copy()

        assert len(colors) == len(box['boxes']), "Mismatch between number of colors and number of boxes"

        for patch, color in zip(box['boxes'], colors):
            patch.set_facecolor(color)

        plt.savefig(f'boxplot_time_per_question.png', dpi=400)
        
    def generate_csv_for_top3_most_read_tokens(self) -> None:
        """
        Generates a CSV file('top3_most_read_tokens.csv') containing the top 3 most read tokens for each question in each experiment.

        Returns:
            None
        """
        result = {}
        for experiment in self.questions:
            result[experiment] = {}
            for question in self.questions[experiment]:
                question.clean_data()
                highest_values = sorted(question.most_readed_types.items(), key=lambda x: x[1], reverse=True)[:3]
                result[experiment][question.question_number] = highest_values

        df = pd.DataFrame(result)
        df.to_csv('top3_most_read_tokens.csv')
                    
    def plot_intereative_scatter(self, answer_path: str = 'respostas.csv') -> None:
        """
        Plots an interactive scatter plot for each question in the dataset.

        This function reads a CSV file ('respostas.csv') and iterates over the questions in the dataset.
        For each question, it retrieves the corresponding data from the CSV file and creates a scatter plot using Plotly.
        The scatter plot displays the source file column and line values, with markers colored based on the correctness of the answer.
        The scatter plot also includes additional information such as the token, syntactic category, duration, and correctness of the answer.

        Note:
        - The CSV file must have the following columns: 'questao', 'Experimento', 'acerto', 'source_file_col', 'source_file_line', 'token', 'syntactic_category', 'duration'.
        - The scatter plot is displayed using Plotly and saved as an HTML file.

        Returns:
        None
        """
        result = {}

        df = pd.read_csv(answer_path)
        color = 'r'
        for experiment in self.questions:
            for question in self.questions[experiment]:
                if question.question_number != "01":   
                    if question.question_number in result:
                        result[question.question_number].append(question)
                    else:
                        result[question.question_number] = [question]

        for question in result:
            fig = go.Figure()
            for experiment_question in tqdm.tqdm(result[question]):
                new_df = df.loc[(df['questao'] == int(experiment_question.question_number))]
                new_df = new_df.loc[(new_df['Experimento'] == int(experiment_question.experiment_number))]

                acerto = new_df['acerto'].values

                source_file_col = experiment_question.data_frame['source_file_col'].values
                source_file_line = experiment_question.data_frame['source_file_line'].values
                token = experiment_question.data_frame['token'].values
                syntactic_category = experiment_question.data_frame['syntactic_category'].values
                duration = experiment_question.data_frame['duration'].values

                text = "Token: " + token + "<br>Syntactic Category: " + syntactic_category + "<br>Duration: " + duration.astype(str) + "<br>Correct: " + acerto.astype(str) + "<extra></extra>"

                if acerto[0]:
                    color = 'rgb(0,255,0)'
                else:
                    color = 'rgb(255,0,0)'
                fig.add_trace(go.Scatter(x=source_file_col,
                                        y=source_file_line,
                                        mode='markers',
                                        marker=dict(color=color),
                                        text = text,
                                        hovertemplate='Column value: %{x}<br>Line value: %{y}<br>%{text}',))
            fig.update_yaxes(autorange="reversed")
            fig.write_html(f'error_x_success{experiment_question.question_number}.html', full_html=True, include_plotlyjs='cdn')
            fig.show()

    def get_density(self):
        pass

if __name__ == "__main__":
    experiments_dir = "C:/Users/Pedro/OneDrive/Área de Trabalho/dataAnal/experimentos"
    qc = QuestionComparision(experiments_dir)
    qc.get_questions_for_experiments()
    qc.generate_tsv_files()
    # qc.plot_white_spaces_percentage(5)
    # qc.plot_diff_eye_position_for_one_question(2,2,5, False)
    # qc.plot_diff_eye_position_for_one_question(2,2,5, True)
    # qc.diff_eye_position_for_one_question(2)
    # print(qc.list_of_fix_vectors)
    # qc.plot_mean_of_most_readed_tokens()
    # qc.plot_question_time_comparison_for_one_experiment(5)
    # qc.plot_scatter_error_and_success()
    # qc.boxplot_of_time_questions('codes/info.json')
    # qc.generate_csv_for_top3_most_read_tokens()
    # qc.plot_intereative_scatter()
    
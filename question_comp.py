import os
from questionType import Question
import matplotlib.pyplot as plt
import numpy as np
import multimatch_gaze as m

class QuestionComparision:
    def __init__(self, experiments_dir: str) -> None:
        self.experiments_dir = experiments_dir
        self.questions = {}
        self.list_of_fix_vectors = {}

    def get_questions_for_experiments(self):
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

    def generate_tsv_files(self):
        for key in self.questions:
            for question in self.questions[key]:
                question.clean_data()
                question.generate_tsv_file()

    def plot_question_time_comparison_for_one_experiment(self, experiment: int):
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

    def plot_question_time_comparison_for_all_experiments(self):
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

    def diff_eye_position_for_one_question(self, question_number: int):
        if question_number < 10:
            question_number = "0" + str(question_number)
        else:
            question_number = str(question_number)

        vector_list = []
        for key in self.questions:
            for q in self.questions[key]:
                if q.question_number == question_number:
                    
                    csv_path = f"{q.full_path[:-8]}question_{q.question_number}.tsv"
                    print(csv_path)
                    try:
                        fix_vector1 = np.recfromcsv(csv_path, delimiter='\t',
                        dtype={'names': ('start_x', 'start_y', 'duration'),
                        'formats': ('f8', 'f8', 'f8')})
                        vector_list.append(fix_vector1)
                    except:
                        print(f"{q.question_number} not found in experiment {key}")
                        
                    
                    

        tam = len(vector_list)
        print (tam)
        for i in range(tam - 1):
            for j in range(i+1, tam):
               self.list_of_fix_vectors[f"{i} - {j}"] = m.docomparison(vector_list[i], vector_list[j], screensize=[1080, 720])

    def plot_diff_eye_position_for_one_question(self, question_number:int, experimentA: int, experimentB: int, consider_duration: bool = False):   
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
            plt.scatter(row['source_file_line'], row['source_file_col'], s=s, color='yellow', alpha=0.7)
        
        for index, row in dfb.iterrows():
            if consider_duration:
                s = row['duration']
            else:
                s = None
            plt.scatter(row['source_file_line'], row['source_file_col'], s=s, color='purple', alpha=0.7)
        
        plt.show()
    
    def plot_white_spaces_percentage(self, experiment: int):
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
    
if __name__ == "__main__":
    experiments_dir = "C:/Users/Pedro/OneDrive/Área de Trabalho/dataAnal/experimentos"
    qc = QuestionComparision(experiments_dir)
    qc.get_questions_for_experiments()
    qc.generate_tsv_files()
    qc.plot_white_spaces_percentage(5)
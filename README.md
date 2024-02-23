# EyeTracker Experiment Data Visualization

This project focuses on creating a graphical visualization for eye-tracking experiment questions. One of the most used features of Python in this project is object-oriented programming (OOP). OOP allows for the creation of classes and objects, which helps in organizing and structuring the code.

To learn more about object-oriented programming in Python, you can refer to the following resources:

- [Python Documentation on Classes](https://docs.python.org/3/tutorial/classes.html)
- [Real Python's Object-Oriented Programming (OOP) in Python 3](https://realpython.com/courses/object-oriented-programming-oop-python/)
- [GeeksforGeeks' Object Oriented Programming in Python](https://www.geeksforgeeks.org/object-oriented-programming-in-python/)

1. **Class `Question` in `questionType.py`**: In this part, important information is extracted from the `.db3` files and it provides the ability to create individual plots for each question of each experiment.

2. **Plot Creation using `Question` class**: With the information extracted in the `Question` class, plots can be created. These plots can compare all the questions of a specific experiment or compare a single question across all experiments.

To access the folder `experiments/Experiment XX/No Dejavu/XX/XX.db3`, where XX represents the experiment number, refer to the code in the `Question` class.



# How to run?

To get the application up and running, you'll need to set up a virtual environment and install the necessary dependencies. Follow these steps to prepare your environment:

### Creating a Virtual Environment

A virtual environment is a self-contained directory that contains a Python installation for a particular version of Python, plus a number of additional packages. Creating a virtual environment allows you to manage dependencies for different projects separately. Here's how you can create one:

1. Open the terminal in your project directory<br>
   Obs: you can use ctrl + ' in vscode to do it
2. follow the script
   
   ```bash
   #create a venv
   python -m venv venv

   #activate the venv

   #windows
    .\venv\Scripts\activate

   #linux
    source venv/bin/activate

   #install all libarys
   pip install -r requirements.txt

3. Now you all set to star, for example of usage you can acsses the `if __name__ == __main__:` of "questionType.py" e "question_comp.py"

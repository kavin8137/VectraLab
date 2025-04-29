# Overview

I created this program to perform several statistical analysis for dataset that I have collected on my own. These analyses including the following:
* Exploring statistical summaries
* Fitting the data to a linear fit model
* Compare datasets by performing $\chi^2$ tests
* Detect any outliers with Chauvenet
* Run Student's t-tests and compare the result with the expected time:
    - Solar Time: 24h
    - Sidereal Time: 23h 56m

I have used the dataset that I have collected using basic setup on using a gnomon and a tripod for collecting the angular displacement for both solar time and sidereal time. The dataset is contained in the data folder in the repository.

The design of this program is to ease the statistical analysis when performing the analysis for both solar time and sidereal time based on the measuring design in the future. The convenient of the program serves as an imediate analysis for the result without duplicating the Python code. The program also consist options to store the results to a folder called results in the directory for the purpose on performing presentation in the future. I have used the tkinter and ttk library to help the program run smoothly.

I have also included a short demonstration video on explaning how the program works.

[Software Demo Video](http://youtube.link.goes.here)

# Data Analysis Results

* Perform the Student's t-test to determine if the result from the measurement is within confidence level and how close our data to the expected value.
    - Based on the result from the Student's t-test, we are confident that the result from the measuring data is accurate for any dataset.

* Perform Chauvenet analysis to identify if there is any existing outliers for the dataset.
    - Although performing $\chi^2$ by eye telling me that there could have some existing outlier. However, when performing the Chauvenet analysis, the data shows that the so called "outlier" by doing $\chi^2$ by eye is usuall occurance when performing the measurements.

* Explore the Chi-Squared Test to determined if any two of the dataset is correlated.
    - Based on the results from Chi-Squared Test, my conclusion of the comparison of all dataset is correlated. However, this does not conclude that the data set is directly effecting to each other.

# Development Environment

* Python 3.12.3
* Numpy
* Matplotlib
* Pandas
* Scipy
* os
* textwrap
* tkinter
* ttk
* PIL (Pillow)

# Useful Websites

* [Numpy](chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://numpy.org/doc/2.2/numpy-user.pdf)
* [Matplotlib](https://matplotlib.org/stable/users/index.html)
* [Pandas](https://pandas.pydata.org/docs/user_guide/index.html)
* [Scipy](https://docs.scipy.org/doc/scipy/tutorial/index.html#user-guide)
* [os](https://docs.python.org/3/library/os.html)
* [textwrap](https://docs.python.org/3/library/textwrap.html)
* [tkinter](https://docs.python.org/3/library/tkinter.html)
* [ttk](https://docs.python.org/3/library/tkinter.ttk.html)
* [PIL (Pillow)](https://pillow.readthedocs.io/en/stable/)
* [$\chi^2$ Test](https://en.wikipedia.org/wiki/Chi-squared_test)
* [Student t-test](https://en.wikipedia.org/wiki/Student%27s_t-test)
* [Chauvenet Criterion](https://en.wikipedia.org/wiki/Chauvenet%27s_criterion)

# Future Work

Eventhough the program perform as expected in its fuction, there are some features that needed to improve in the future:
* Re-analyze the Student's t-test and its principle. (This is because the Student's t-test is not quire plotting what I really wanted in the plot.)
* Re-analyze the principle of $\chi^2$ test. I believed I have made some mistakes in the test and I cannot spot it. However, the result from the $\chi^2$ test is interesting based on the data.
* Making the code to be generized to different set of codes. This code mainly focus on my desinated data set.
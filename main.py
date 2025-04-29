# importing libraries
import os
from data import DataStorage
from fitting import Fitting
from analysis import Analysis
from graphic import Graphic

# running the main program
# this is the main program that runs the GUI and the analysis
# it imports the DataStorage, Fitting, Analysis and Graphic classes
if __name__ == "__main__":
    base = os.getcwd()
    ds = DataStorage(
        os.path.join(base, "data", "gnomon1.csv"),
        os.path.join(base, "data", "gnomon2.csv"),
        os.path.join(base, "data", "gnomon3.csv"),
        os.path.join(base, "data", "sidereal1.csv"),
        os.path.join(base, "data", "sidereal2.csv"),
        os.path.join(base, "data", "sidereal3.csv"),
        model=Fitting()
    )
    ds.extract_data()
    ds.process_data()
    analysis = Analysis()
    app = Graphic(ds, analysis)
    app.mainloop()
# importing libraries
import pandas as pd

# declaring the DataStorage class
# this class is used to load the data from the CSV files
class DataStorage:
    def __init__(self,
                 filename1, filename2, filename3,
                 filename4, filename5, filename6,
                 model=None):
        # load all six CSVs via pandas
        self.data1 = pd.read_csv(filename1)
        self.data2 = pd.read_csv(filename2)
        self.data3 = pd.read_csv(filename3)
        self.data4 = pd.read_csv(filename4)
        self.data5 = pd.read_csv(filename5)
        self.data6 = pd.read_csv(filename6)
        self.model = model

    # this function is used to extract the data from the CSV files
    # it extracts the time and angle data from the CSV files
    def extract_data(self):
        # ─── solar ─────────────────────────────────────────────────────────
        self.time3 = self.data3['Time (s)'].to_numpy()
        self.time1 = self.data1['Time (s)'].to_numpy()
        self.time2 = self.data2['Time (s)'].to_numpy()

        self.angle1 = self.data1['Angle'].to_numpy()
        self.angle2 = self.data2['Angle'].to_numpy()
        self.angle3 = self.data3['Angle'].to_numpy()

        # ─── sidereal ──────────────────────────────────────────────────────
        self.time4 = self.data4['Time (s)'].to_numpy()
        self.time5 = self.data5['Time (s)'].to_numpy()
        self.time6 = self.data6['Time (s)'].to_numpy()

        self.angle4x = self.data4['Angle x'].to_numpy()
        self.angle4y = self.data4['Angle y'].to_numpy()
        self.angle5x = self.data5['Angle x'].to_numpy()
        self.angle5y = self.data5['Angle y'].to_numpy()
        self.angle6x = self.data6['Angle x'].to_numpy()
        self.angle6y = self.data6['Angle y'].to_numpy()

    # this function is used to process the data
    # it processes the time and angle data from the CSV files
    def process_data(self):
        # now use your fitting.py routines for solar/sidereal/time
        self.angle1 = self.model.angular_dis_solar(self.angle1)
        self.angle2 = self.model.angular_dis_solar(self.angle2)
        self.angle3 = self.model.angular_dis_solar(self.angle3)

        self.angle4 = self.model.angular_dis_sidereal(self.angle4x, self.angle4y)
        self.angle5 = self.model.angular_dis_sidereal(self.angle5x, self.angle5y)
        self.angle6 = self.model.angular_dis_sidereal(self.angle6x, self.angle6y)

        self.time1 = self.model.process_time(self.time1)
        self.time2 = self.model.process_time(self.time2)
        self.time3 = self.model.process_time(self.time3)
        self.time4 = self.model.process_time(self.time4)
        self.time5 = self.model.process_time(self.time5)
        self.time6 = self.model.process_time(self.time6)

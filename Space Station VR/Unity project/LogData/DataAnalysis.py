import neurokit2 as nk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['figure.figsize'] = [8, 5]  # Bigger images


#ecg_signal = nk.data(dataset="ecg_3000hz")['ECG']

path = r"D:\Bachelor Thesis Projects\3D Project Test Bachelor\Space station VR\Space Station VR\Unity project\LogData"

dfECG = pd.read_csv(path + "\ID0-ECG.csv")
dfECG["Clean"] = nk.ecg_clean(
    dfECG["Value"].values, sampling_rate=130,  method="neurokit")  # biosppy


peaks, info = nk.ecg_peaks(
    dfECG["Clean"].values, sampling_rate=130, method="kalidas2017", correct_artifacts=True)

hrv_time = nk.hrv_time(peaks, sampling_rate=130, show=False)

hrv_freq = nk.hrv_frequency(
    peaks, sampling_rate=130, show=False, silent=False, psd_method="lomb")  # welch

dfECG["Rate"] = nk.ecg_rate(
    peaks, sampling_rate=130, interpolation_method="cubic", desired_length=len(dfECG["Clean"].values))

dfECG["Value"].plot(label="RAW", c="k", lw=2)

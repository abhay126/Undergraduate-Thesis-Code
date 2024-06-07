import matplotlib.pyplot as plt
import pandas as pd

def generate_plot(filename = 'data.csv'):
    
    data = pd.read_csv(filename)
    
    plt.style.use('ggplot')
    plt.title("Count Rates for Ge-Doped Fiber - 2m")
    plt.plot(data['Calculated Wavelength'], data['Count Rate'], '.r-.')
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Raw Count Rate (counts/s)")
    plt.savefig(fname= '2m_ge_doped_05_03_3dBm.png')
    plt.show()

if __name__=="__main__":
    generate_plot()
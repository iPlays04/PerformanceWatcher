import psutil
import tkinter as tk
import wmi


# Globale Variablen
bgcolor = "#333446"
pricolor = "#7f8ca6"
seccolor = "#b8cfce"
hicolor = "#eaeff1"
green =  "#00ff00"
red = "#ff0000"
window_size = (320, 240)
globalfont = "Microsoft JhengHei UI"

def addgraph(canvas, x, y, percent, isTemp, name):
    if(isTemp):
        percent = percent / 120
        if(percent>1):percent=1
        print(percent)
    

    # Outline
    canvas.create_oval(x, y, x+100, y+100, fill=seccolor, outline='')

    # Hintergrund
    canvas.create_oval(x+5, y+5, x+95, y+95, fill=pricolor, outline='')

    # Genutze Leistung
    if not isTemp:
        redness = hex(int(255*percent))[2:].zfill(2)
        greenness = hex(int((1-percent)*255))[2:].zfill(2)
    else:
        redness = hex(int(255 * max(0, (percent - 0.4) / 0.6)))[2:].zfill(2)
        greenness = hex(int(255 * (1 - max(0, (percent - 0.4) / 0.6))))[2:].zfill(2)
    canvas.create_arc(x+5, y+5, x+95, y+95, start=0, extent=percent*359.99, fill=f"#{redness}{greenness}00", outline='')
    #print(f"current colour:#{redness}{greenness}00") #Testprint zur ausgabe des momentanen Farbwertes

    # Mittelkreis
    canvas.create_oval(x+35, y+35, x+65, y+65, fill=seccolor, outline='')
    if(not isTemp):
        #Anzeige
        canvas.create_text(x+50, y+50, text=f"{int(percent*100)}%", fill=bgcolor, font=(globalfont, 8))
    else:
        canvas.create_text(x+50, y+50, text=f"{int(percent*120)}°C", fill=bgcolor, font=(globalfont, 8))
    canvas.create_text(x+50, y+110, text=f"{name}", fill=hicolor, font=(globalfont, 8))

def addNoDataInfo(canvas, x,y,type):
    canvas.create_rectangle(x,y,x+110,y+120,fill='', outline=seccolor)
    canvas.create_text(x+55, y+60, text=f"NoData: {type}", fill=seccolor, font=(globalfont, 8))


def get_cpu_temp():
    try:
        w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        temperature_infos = w.Sensor()
        for sensor in temperature_infos:
            if sensor.SensorType == u'Temperature' and 'CPU' in sensor.Name:
                return sensor.Value
    except Exception as e:
        #print(f"CPU Temp error (OHM): {e}")
        print()
    return None

def get_gpu_usage():
    try:
        w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        for sensor in w.Sensor():
            # Look for GPU Core Load first
            if sensor.SensorType == "Load" and "GPU Core" in sensor.Name:
                return sensor.Value / 100  # Convert to 0-1 scale
            # Optionally: use "GPU Load" or "GPU Total Load"
            elif sensor.SensorType == "Load" and "GPU Load" in sensor.Name:
                return sensor.Value / 100
    except Exception as e:
        #print(f"GPU usage error: {e}")
        print()
    return None

def get_gpu_temperature():
    try:
        w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        sensors = w.Sensor()
        for sensor in sensors:
            if sensor.SensorType == "Temperature" and "GPU" in sensor.Name:
                return sensor.Value
    except Exception as e:
        #print(f"GPU temp error: {e}")
        print()
    return None

def get_memory_usage():
    memory = psutil.virtual_memory()
    memory_used_percentage = memory.percent / 100
    return memory_used_percentage
    

def update_graph():
    canvas.delete("all")

    #CPU-Auslastung
    cpu_percent = psutil.cpu_percent(interval=1) / 100
    addgraph(canvas, 0, 0, cpu_percent, False, "CPU-Auslastung")

    #CPU-Temperatur
    cpu_temp = get_cpu_temp()
    if cpu_temp is not None:
        addgraph(canvas, 0, 120, cpu_temp, True, "CPU-Temperatur")
    else: addNoDataInfo(canvas, 0, 120,"cputemp") 
        

    #GPU-Auslastung
    gpu_percent = get_gpu_usage()
    if gpu_percent is not None:
        addgraph(canvas, 110, 0, gpu_percent, False, "GPU-Auslastung")
    else: addNoDataInfo(canvas, 110, 0,"gpuuse")

    #GPU-Temperatur
    gpu_temperature = get_gpu_temperature()
    if gpu_temperature is not None:
        addgraph(canvas, 110, 120, gpu_temperature, True, "GPU-Temperatur")
    else: addNoDataInfo(canvas, 110, 120,"gputemp")

    #RAM-Auslastung
    ram_percent = get_memory_usage()
    addgraph(canvas, 220, 0, ram_percent, False, "RAM-Auslastung")

    root.after(1000, update_graph)  # Aktualisiere alle 1000 ms (1 Sekunde)

# Tkinter initialisieren
root = tk.Tk()
root.title("PerformanceWatcher")
root.geometry(f"{window_size[0]}x{window_size[1]}")
root.resizable(False,False)
root.attributes("-topmost", True)

root.iconphoto(False, tk.PhotoImage(file='.\\icon.png'))


canvas = tk.Canvas(root, bg=bgcolor, width=window_size[0], height=window_size[1])
canvas.pack()

update_graph()

root.mainloop()
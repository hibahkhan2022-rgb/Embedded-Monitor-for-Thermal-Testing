import os
import time
import subprocess
import numpy as np
import csv
from multiprocessing import Process, Value

def get_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return float(f.read()) / 1000.0
    except Exception:
        return 0.0

def governor_loop(shared_latency):
    os.sched_setaffinity(0, {0}) 
    current_mode = 0
    print("\n--- #Enter name of experiment ---")
    
    with open('namefile.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Elapsed", "Temp", "Latency", "Mode"])
        start_time = time.time()

        while True:
            temp = get_temp()
            lat = shared_latency.value
            elapsed = time.time() - start_time

            if temp > 70.0 and current_mode == 0:
                print(f"\n[!!!] THERMAL LIMIT REACHED ({temp:.1f}C). Switching to Mode (0 or 2).")
                subprocess.run(['sudo', 'nvpmodel', '-m', '2'], input=b"no\n", capture_output=True)
                current_mode = 2
                
            elif temp < 55.0 and current_mode != 0:
                print(f"\n[---] COOL DOWN SUCCESS ({temp:.1f}C). Restoring (0 or 2).")
                subprocess.run(['sudo', 'nvpmodel', '-m', '0'], input=b"no\n", capture_output=True)
                current_mode = 0

            writer.writerow([round(elapsed, 2), round(temp, 2), round(lat, 2), current_mode])
            file.flush()
            os.fsync(file.fileno())

            print(f"\r[GOV] Time: {elapsed:.0f}s | Temp: {temp:.1f}C | Lat: {lat:.2f}ms | Mode: {current_mode}", end="")
            time.sleep(1)

def workload_loop(shared_latency):
    os.sched_setaffinity(0, {1, 2, 3, 4, 5})
    while True:
        start = time.time()
        a = np.random.rand(4000, 4000).astype(np.float32)
        b = np.random.rand(4000, 4000).astype(np.float32)
        _ = np.dot(a, b)
        shared_latency.value = (time.time() - start) * 1000

if __name__ == "__main__":
    shared_latency = Value('d', 0.0)

    p_gov = Process(target=governor_loop, args=(shared_latency,))
    p_work1 = Process(target=workload_loop, args=(shared_latency,))
    p_work2 = Process(target=workload_loop, args=(shared_latency,))

    p_gov.start()
    p_work1.start()
    p_work2.start()

    try:
        p_gov.join()
    except KeyboardInterrupt:
        print("\nExperiment stopped by user.")
    finally:
        p_gov.terminate()
        p_work1.terminate()
        p_work2.terminate()
        print("\nHardware-in-the-Loop test complete. CSV saved.")

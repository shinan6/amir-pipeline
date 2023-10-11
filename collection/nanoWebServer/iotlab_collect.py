from flask import Flask, request, url_for, redirect, render_template
import datetime
import json
import os, signal
import time
import subprocess

MAX_SEC = 20
parID = 0
actFile = '../act_list.json'
save_path = '/mnt/usbstick/deeplens/data/'

app = Flask(__name__)

def is_file_complete(fname):
    v1_flg = os.path.isfile(fname + "_1.mp4")
    v2_flg = os.path.isfile(fname + "_2.mkv")
    pc_flg = os.path.isfile(fname + ".pcap")
    ad_flg = os.path.isfile(fname + ".wav")
    return(v1_flg and v2_flg and pc_flg and ad_flg)


@app.route("/")
def hello():
    return render_template('index.html')


@app.route('/act_log', methods=['GET', 'POST'])
def act_log():
    with open(actFile) as f:
        data = json.load(f)
    if request.method == 'POST':
        return redirect(url_for('index'))

    return render_template('act_log.html', activity=data)

@app.route("/finish")
def finish():
    return render_template('finish.html')

@app.route("/wrong")
def wrong():
    return render_template('wrong.html')

@app.route('/start_csv', methods=['POST'])
def start_csv():
    if request.method == 'POST':
        global activity
        global repetition
        global device
        global c1_f, c2_f, pcap_f, audio_f
        global path, act_id, file_str
        global proc
        activity = request.form['curr_act']
        device = request.form['curr_dev']
        repetition = request.form['curr_rep']
        now = str(int(time.time()))
        path = device.replace(' ', '_') + '/' + activity.replace(' ', '_') + '/' + parID
        if not os.path.exists(save_path + path):
            os.makedirs(save_path + path)
        act_id = activity.replace(' ', '_') + "_" + repetition + "_"
        file_str = act_id + now 
        c1_f = file_str + "_1.mp4"
        c2_f = file_str + "_2.mkv"
        pcap_f = file_str + ".pcap"
        audio_f = file_str + ".wav"
        sf = open(saveFile, "a")
        sf.write(now + ", start, "+ device +", "+ str(parID) +", "+ activity + ", " \
            + repetition + ", " + c1_f+ ", " + c2_f + \
            ", " + pcap_f+ ", " + audio_f + "\n")
        sf.close()
        proc = subprocess.Popen("./collect_wo_timeout.sh " + path + '/' + act_id, shell=True, preexec_fn=os.setsid) 
        return("OK")

@app.route('/end_csv', methods=['POST'])
def end_csv():
    if request.method == 'POST':
        now = str(int(time.time()))
        sf = open(saveFile, "a")
        sf.write(now + ", end, "+ device +", "+ str(parID) +", "+ activity + ", " \
            + repetition + ", " + c1_f+ ", " + c2_f + \
            ", " + pcap_f+ ", " + audio_f + "\n")
        sf.close()
        time.sleep(MAX_SEC)
        os.killpg(proc.pid, signal.SIGTERM)
        if not is_file_complete(save_path + path + '/' + file_str):
            sf = open(saveFile, "a")
            sf.write('not complete\n')
            sf.close()
            # return redirect(url_for('wrong'))
        return("OK")
        
@app.route('/stop_csv', methods=['POST'])
def stop_csv():
    if request.method == 'POST':
        now = str(int(time.time()))
        sf = open(saveFile, "a")
        sf.write(now + ", stop, "+ device +", "+ str(parID) +", "+ activity + ", " \
            + repetition + ", " + c1_f+ ", " + c2_f + \
            ", " + pcap_f+ ", " + audio_f + "\n")
        sf.write('bad data\n')
        sf.close()
        time.sleep(MAX_SEC)
        os.killpg(proc.pid, signal.SIGTERM)
        if not is_file_complete(save_path + path + '/' + file_str):
            sf = open(saveFile, "a")
            sf.write('not complete\n')
            sf.close()
            # return redirect(url_for('wrong'))
        return("OK")

@app.route('/data', methods = ['POST', 'GET'])
def data():
    if request.method == 'POST':
        form_data = request.form
        global parID, actFile
        global saveFile, sf
        parID = form_data['idnum']
        actFile = form_data['activity']
        saveFile = save_path + "log/log_p" + parID + "_" + str(int(time.time())) + ".csv"
        sf = open(saveFile, "a")
        sf.write("timestamp, time_type, device, ID, activity, repetition, camera1_file, camera2_file, pcap_file, audio_file\n")
        sf.close()
        return redirect(url_for('act_log'))

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=4000, debug=True)

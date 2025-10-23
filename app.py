from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

processes = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_process', methods=['POST'])
def add_process():
    data = request.get_json()
    processes.append(data)
    return jsonify({"message": "Proceso agregado", "processes": processes})


@app.route('/reset', methods=['POST'])
def reset():
    processes.clear()  # Limpia la lista original SIN crear una nueva
    return jsonify({"message": "Procesos reiniciados correctamente"})



@app.route('/run', methods=['POST'])
def run():
    data = request.get_json()
    algorithm = data.get('algorithm')
    quantum = int(data.get('quantum', 2))

    if algorithm == "RR":
        result = round_robin(processes, quantum)
    elif algorithm == "FCFS":
        result = fcfs(processes)
    elif algorithm == "SJF":
        result = sjf(processes)
    else:
        return jsonify({"error": "Algoritmo no válido"})

    return jsonify(result)


# ---------- 🔹 FCFS ----------
def fcfs(procs):
    procs_copy = [p.copy() for p in procs]
    order = sorted(procs_copy, key=lambda x: x['arrival'])
    t = 0
    execution = []
    queue_history = []

    for p in order:
        start = max(t, p['arrival'])
        finish = start + p['burst']
        t = finish
        execution.append({
            "name": p["name"],
            "start": start,
            "finish": finish,
            "waiting": start - p["arrival"],
            "turnaround": finish - p["arrival"]
        })
        queue_history.append({
            "time": t,
            "executing": p["name"],
            "queue": [x["name"] for x in order if x["arrival"] > t]
        })

    return {"execution": execution, "queue_history": queue_history}


# ---------- 🔹 SJF (No preemptive) ----------
def sjf(procs):
    procs_copy = [p.copy() for p in procs]
    queue = sorted(procs_copy, key=lambda x: x['arrival'])
    ready = []
    t = 0
    execution = []
    queue_history = []

    while queue or ready:
        # Mueve los que ya llegaron al ready
        while queue and queue[0]['arrival'] <= t:
            ready.append(queue.pop(0))

        if not ready:
            # Adelanta el tiempo al próximo proceso si no hay listos
            t = queue[0]['arrival']
            continue

        # Selecciona el de menor burst
        ready.sort(key=lambda x: x['burst'])
        p = ready.pop(0)

        start = max(t, p['arrival'])
        finish = start + p['burst']
        t = finish

        execution.append({
            "name": p["name"],
            "start": start,
            "finish": finish,
            "waiting": start - p["arrival"],
            "turnaround": finish - p["arrival"]
        })

        queue_history.append({
            "time": t,
            "executing": p["name"],
            "queue": [x['name'] for x in ready] + [x['name'] for x in queue]
        })

    return {"execution": execution, "queue_history": queue_history}


# ---------- 🔹 ROUND ROBIN ----------
def round_robin(procs, quantum):
    procs_copy = [p.copy() for p in procs]
    queue = sorted(procs_copy, key=lambda x: x['arrival'])
    t = 0
    execution = []
    queue_history = []
    ready = []
    finished = []

    while queue or ready:
        # Mueve los procesos que ya llegaron al tiempo t
        while queue and queue[0]['arrival'] <= t:
            ready.append(queue.pop(0))

        if not ready:
            # Si no hay procesos listos, avanza el tiempo
            t = queue[0]['arrival']
            continue

        p = ready.pop(0)
        start = t
        exec_time = min(p['burst'], quantum)
        finish = start + exec_time
        t = finish
        p['burst'] -= exec_time

        execution.append({
            "name": p["name"],
            "start": start,
            "finish": finish,
            "remaining": p["burst"]
        })

        # Guarda el estado de la cola en este instante
        queue_history.append({
            "time": t,
            "executing": p["name"],
            "queue": [x['name'] for x in ready] + [x['name'] for x in queue]
        })

        # Mueve procesos que llegaron durante la ejecución al ready
        while queue and queue[0]['arrival'] <= t:
            ready.append(queue.pop(0))

        if p['burst'] > 0:
            # Si no ha terminado, vuelve al final de la cola
            ready.append(p)
        else:
            # Si terminó, guárdalo con sus tiempos
            finished.append(p)

    # Calcular tiempos de espera y retorno reales
    for e in execution:
        name = e["name"]
        all_execs = [x for x in execution if x["name"] == name]
        first_start = all_execs[0]["start"]
        last_finish = all_execs[-1]["finish"]
        arrival = next(p["arrival"] for p in procs_copy if p["name"] == name)
        turnaround = last_finish - arrival
        waiting = turnaround - sum(min(x["finish"] - x["start"], quantum) for x in all_execs)
        e.update({"waiting": waiting, "turnaround": turnaround})

    return {"execution": execution, "queue_history": queue_history}



if __name__ == '__main__':
    app.run(debug=True)

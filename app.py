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
    order = sorted(procs, key=lambda x: x['arrival'])
    t = 0
    execution = []

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

    return {"execution": execution, "queue_history": []}


# ---------- 🔹 SJF ----------
def sjf(procs):
    # trabajamos sobre copias para no mutar la lista original
    procs_copy = [p.copy() for p in procs]
    # cola ordenada por llegada
    queue = sorted(procs_copy, key=lambda x: x['arrival'])
    ready = []
    t = 0
    execution = []
    queue_history = []  # opcional: puedes rellenarlo si quieres mostrar la cola en tiempo real

    while queue or ready:
        # mover los que ya llegaron a 'ready'
        while queue and queue[0]['arrival'] <= t:
            ready.append(queue.pop(0))

        if not ready:
            # si no hay listos, adelanta el reloj al siguiente arrival
            t = queue[0]['arrival']
            continue

        # seleccionar el de menor burst entre los listos
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

        # (opcional) guardar estado de la cola en este instante
        queue_history.append({
            "time": t,
            "executing": p["name"],
            "queue": [x['name'] for x in ready] + [x['name'] for x in queue]
        })

    return {"execution": execution, "queue_history": queue_history}



# ---------- 🔹 ROUND ROBIN ----------
def round_robin(procs, quantum):
    queue = sorted(procs, key=lambda x: x['arrival'])
    t = 0
    execution = []
    queue_history = []
    ready_queue = []

    while queue or ready_queue:
        # Mueve los procesos que llegan a tiempo t a la cola de listos
        while queue and queue[0]['arrival'] <= t:
            ready_queue.append(queue.pop(0))

        if not ready_queue:
            t += 1
            continue

        p = ready_queue.pop(0)
        exec_time = min(quantum, p['burst'])
        start = t
        finish = t + exec_time
        t = finish
        p['burst'] -= exec_time

        execution.append({
            "name": p["name"],
            "start": start,
            "finish": finish,
            "remaining": p['burst']
        })

        # Guarda el estado actual de la cola
        queue_history.append({
            "time": t,
            "executing": p["name"],
            "queue": [x['name'] for x in ready_queue]
        })

        if p['burst'] > 0:
            # Si no terminó, vuelve al final
            ready_queue.append(p)

    return {"execution": execution, "queue_history": queue_history}


if __name__ == '__main__':
    app.run(debug=True)

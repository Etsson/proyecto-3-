def round_robin(processes, quantum):
    # Copiar procesos para no alterar los originales
    processes = [p.copy() for p in processes]
    processes.sort(key=lambda x: x['arrival'])  # Orden por llegada

    time = 0
    queue = []
    result = []
    queue_history = []  # 👈 Guardará la cola en cada momento
    remaining = processes.copy()

    while remaining or queue:
        # Agregar a la cola los procesos que ya llegaron
        for p in remaining[:]:
            if p['arrival'] <= time:
                queue.append(p.copy())
                remaining.remove(p)

        if not queue:
            # Si la cola está vacía, avanzar el tiempo
            time = remaining[0]['arrival']
            continue

        current = queue.pop(0)
        exec_time = min(current['burst'], quantum)
        time += exec_time
        current['burst'] -= exec_time

        # Guardar el proceso ejecutado y la cola actual
        result.append({'name': current['name'], 'time': time})

        # Guardar el estado de la cola en este instante
        queue_history.append({
            'time': time,
            'executing': current['name'],
            'queue': [p['name'] for p in queue]
        })

        # Si el proceso no ha terminado, vuelve a la cola
        if current['burst'] > 0:
            current['arrival'] = time
            queue.append(current)

        # Agregar nuevos procesos que llegaron durante este quantum
        for p in remaining[:]:
            if p['arrival'] <= time:
                queue.append(p.copy())
                remaining.remove(p)

    return {'execution': result, 'queue_history': queue_history}


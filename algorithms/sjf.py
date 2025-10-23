def sjf(processes):
    processes = sorted(processes, key=lambda p: p['arrival'])
    completed = []
    current_time = 0

    while processes:
        # Filtrar procesos que ya llegaron
        available = [p for p in processes if p['arrival'] <= current_time]

        if not available:
            # Si no hay procesos disponibles, avanza el tiempo
            current_time = processes[0]['arrival']
            continue

        # Seleccionar el proceso con menor burst time
        shortest = min(available, key=lambda p: p['burst'])
        processes.remove(shortest)

        start = current_time
        finish = start + shortest['burst']
        waiting = start - shortest['arrival']
        turnaround = finish - shortest['arrival']
        current_time = finish

        completed.append({
            "name": shortest['name'],
            "arrival": shortest['arrival'],
            "burst": shortest['burst'],
            "start": start,
            "finish": finish,
            "waiting": waiting,
            "turnaround": turnaround
        })

    return completed

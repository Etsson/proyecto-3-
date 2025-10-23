def fcfs(processes):
    # Ordenar procesos según el instante de llegada
    processes = sorted(processes, key=lambda p: p['arrival'])
    current_time = 0
    result = []

    for p in processes:
        # Si el CPU está libre antes de que llegue el proceso, espera
        if current_time < p['arrival']:
            current_time = p['arrival']

        start = current_time
        finish = start + p['burst']
        waiting = start - p['arrival']
        turnaround = finish - p['arrival']
        current_time = finish

        result.append({
            "name": p['name'],
            "arrival": p['arrival'],
            "burst": p['burst'],
            "start": start,
            "finish": finish,
            "waiting": waiting,
            "turnaround": turnaround
        })

    return result

from typing import List, Dict, Any, Tuple
import heapq

def _validate(processes: List[Dict[str, Any]]) -> None:
    if not isinstance(processes, list):
        raise TypeError("processes debe ser una lista de diccionarios")
    for p in processes:
        if not all(k in p for k in ("name", "arrival", "burst")):
            raise ValueError("cada proceso debe tener 'name', 'arrival' y 'burst'")
        if p["burst"] < 0 or p["arrival"] < 0:
            raise ValueError("arrival y burst deben ser >= 0")

def _averages(completed: List[Dict[str, Any]]) -> Tuple[float, float]:
    n = len(completed)
    if n == 0:
        return 0.0, 0.0
    avg_wait = sum(p["waiting"] for p in completed) / n
    avg_turn = sum(p["turnaround"] for p in completed) / n
    return avg_wait, avg_turn

def sjf(processes: List[Dict[str, Any]], preemptive: bool = False) -> Dict[str, Any]:
    """
    Ejecuta SJF sobre la lista de procesos.
    Cada proceso: {'name': str, 'arrival': int|float, 'burst': int|float}
    Parámetros:
      preemptive: si True usa SRTF (Shortest Remaining Time First).
    Retorna:
      {'completed': [...], 'avg_waiting': float, 'avg_turnaround': float}
    """
    _validate(processes)
    # copia y ordena por arrival (estabilidad por name para desempates)
    proc_list = sorted(
        [{"name": p["name"], "arrival": float(p["arrival"]), "burst": float(p["burst"])} for p in processes],
        key=lambda x: (x["arrival"], x["name"])
    )

    completed: List[Dict[str, Any]] = []
    current_time = proc_list[0]["arrival"] if proc_list else 0.0

    if not preemptive:
        # SJF no preemptivo
        remaining = proc_list[:]  # procesos pendientes
        while remaining:
            available = [p for p in remaining if p["arrival"] <= current_time]
            if not available:
                current_time = remaining[0]["arrival"]
                continue
            # elegir menor burst, desempatar por arrival y name
            shortest = min(available, key=lambda p: (p["burst"], p["arrival"], p["name"]))
            remaining.remove(shortest)
            start = current_time
            finish = start + shortest["burst"]
            waiting = start - shortest["arrival"]
            turnaround = finish - shortest["arrival"]
            current_time = finish
            completed.append({
                "name": shortest["name"],
                "arrival": shortest["arrival"],
                "burst": shortest["burst"],
                "start": start,
                "finish": finish,
                "waiting": waiting,
                "turnaround": turnaround
            })
    else:
        # SRTF (preemptive)
        heap: List[Tuple[float, float, int, Dict[str, Any]]] = []
        idx = 0  # índice en proc_list para "arrival"
        counter = 0  # para estabilidad en heap
        # track start times (primer momento en que se ejecuta)
        started = {}
        # restantes por proceso (nombre -> remaining)
        while idx < len(proc_list) or heap:
            # añadir todos los procesos que ya han llegado
            while idx < len(proc_list) and proc_list[idx]["arrival"] <= current_time:
                p = proc_list[idx]
                heapq.heappush(heap, (p["burst"], p["arrival"], counter, {"name": p["name"], "burst": p["burst"], "arrival": p["arrival"]}))
                counter += 1
                idx += 1
            if not heap:
                # saltar al siguiente arrival si no hay procesos listos
                current_time = proc_list[idx]["arrival"]
                continue
            rem, arrival, _, proc = heapq.heappop(heap)
            name = proc["name"]
            if name not in started:
                started[name] = current_time
            # determinar tiempo hasta la próxima llegada (si existe)
            next_arrival = proc_list[idx]["arrival"] if idx < len(proc_list) else None
            if next_arrival is None:
                run_time = rem
            else:
                run_time = min(rem, next_arrival - current_time)
            # ejecutar por run_time
            current_time += run_time
            rem -= run_time
            if rem <= 1e-12:
                # completado
                finish = current_time
                burst = proc["burst"]
                turnaround = finish - proc["arrival"]
                waiting = turnaround - burst
                completed.append({
                    "name": name,
                    "arrival": proc["arrival"],
                    "burst": burst,
                    "start": started[name],
                    "finish": finish,
                    "waiting": waiting,
                    "turnaround": turnaround
                })
            else:
                # queda tiempo, reinsertar con remaining actualizado
                heapq.heappush(heap, (rem, arrival, counter, {"name": name, "burst": rem, "arrival": arrival}))
                counter += 1

    # ordenar output por start (más legible)
    completed.sort(key=lambda p: (p["start"], p["arrival"], p["name"]))
    avg_wait, avg_turn = _averages(completed)
    return {"completed": completed, "avg_waiting": avg_wait, "avg_turnaround": avg_turn}

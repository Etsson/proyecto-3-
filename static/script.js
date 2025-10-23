let processes = [];
let simulationRunning = false;
let cancelRequested = false;

// ====================================================
// 🔹 Agregar procesos
// ====================================================
async function addProcess() {
  const name = document.getElementById("name").value;
  const arrival = parseInt(document.getElementById("arrival").value);
  const burst = parseInt(document.getElementById("burst").value);

  if (!name || isNaN(arrival) || isNaN(burst)) {
    alert("Por favor completa todos los campos.");
    return;
  }

  const response = await fetch("/add_process", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, arrival, burst }),
  });

  const data = await response.json();
  processes = data.processes;
  updateTable(processes);
}

function updateTable(processes) {
  const table = document.getElementById("table");
  table.innerHTML = "<tr><th>Nombre</th><th>Llegada</th><th>CPU</th></tr>";
  processes.forEach((p) => {
    table.innerHTML += `<tr><td>${p.name}</td><td>${p.arrival}</td><td>${p.burst}</td></tr>`;
  });
}

// ====================================================
// 🔹 Ejecutar simulación
// ====================================================
async function run() {
  const algorithm = document.getElementById("algorithm").value;
  const quantum = parseInt(document.getElementById("quantum").value) || 2;

  const response = await fetch("/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      algorithm,
      quantum,
      processes: processes
    }),
  });

  const data = await response.json();

  if (!data.execution) {
    alert("Error: No se recibió información de ejecución.");
    return;
  }

  // Guardar el estado
  simulationRunning = true;
  cancelRequested = false;

  // Mostrar tablas
  mostrarResultados(data.execution);
  mostrarCola(data.queue_history);

  // 🟢 Ejecutar simulación visual paso a paso
  await simulate(data.execution);

  // Al terminar
  simulationRunning = false;
}


// ====================================================
// 🔹 Simulación visual
// ====================================================
async function simulate(execution) {
  if (!execution || execution.length === 0) return;

  const simDiv = document.getElementById("simulation");
  simDiv.innerHTML = "";

  for (let i = 0; i < execution.length; i++) {
    if (cancelRequested) break;
    const p = execution[i];

    simDiv.innerHTML = `<p>⚙️ Ejecutando: <strong>${p.name}</strong> (Inicio: ${p.start}, Fin: ${p.finish})</p>`;
    await new Promise((res) => setTimeout(res, 2000));
  }

  if (cancelRequested) {
    simDiv.innerHTML = `<p>❌ Ejecución cancelada por el usuario.</p>`;
  } else {
    simDiv.innerHTML = `<p>✅ Ejecución completada</p>`;
  }
}


// ====================================================
// 🔹 Cancelar simulación
// ====================================================
function cancelSimulation() {
  if (!simulationRunning) {
    alert("No hay ninguna simulación en curso.");
    return;
  }
  cancelRequested = true;
  simulationRunning = false;
  const simDiv = document.getElementById("simulation");
  simDiv.innerHTML = `<p>❌ Ejecución cancelada.</p>`;
}

// ====================================================
// 🔹 Limpiar tabla y reiniciar servidor
// ====================================================
async function clearTable() {
  processes = [];
  document.getElementById("table").innerHTML = "<tr><th>Nombre</th><th>Llegada</th><th>CPU</th></tr>";
  document.getElementById("simulation").innerHTML = "";
  document.getElementById("tablaResultados").innerHTML = "<tr><th>Proceso</th><th>Inicio</th><th>Fin</th></tr>";
  document.getElementById("tablaCola").innerHTML = "<tr><th>Tiempo</th><th>Ejecutando</th><th>Cola</th></tr>";

  try {
    const res = await fetch("/reset", { method: "POST" });
    const data = await res.json();
    console.log(data.message);
    alert("✅ Tabla y servidor limpiados correctamente.");
  } catch (err) {
    console.error(err);
    alert("⚠️ Error al limpiar datos.");
  }
}


async function resetAll() {
  const confirmReset = confirm("¿Seguro que deseas reiniciar todo?");
  if (!confirmReset) return;

  cancelRequested = false;
  simulationRunning = false;

  await clearTable(); // Llama a la versión mejorada que ya resetea el servidor

  alert("🔄 Todo reiniciado correctamente.");
}

// ====================================================
// 🔹 Mostrar resultados
// ====================================================
function mostrarResultados(execution) {
  const table = document.getElementById("tablaResultados");
  table.innerHTML =
    "<tr><th>Proceso</th><th>Inicio</th><th>Fin</th><th>Espera</th><th>Retorno</th></tr>";

  execution.forEach((p) => {
    table.innerHTML += `
      <tr>
        <td>${p.name}</td>
        <td>${p.start || "-"}</td>
        <td>${p.finish || "-"}</td>
        <td>${p.waiting || "-"}</td>
        <td>${p.turnaround || "-"}</td>
      </tr>`;
  });
}

// ====================================================
// 🔹 Mostrar cola del Round Robin
// ====================================================
function mostrarCola(history) {
  const colaTable = document.getElementById("tablaCola");
  colaTable.innerHTML = "<tr><th>Tiempo</th><th>Ejecutando</th><th>Cola</th></tr>";

  history.forEach((h) => {
    colaTable.innerHTML += `
      <tr>
        <td>${h.time}</td>
        <td>${h.executing}</td>
        <td>${h.queue.join(", ") || "Vacía"}</td>
      </tr>`;
  });
}
///---------------------------------------------------------------

function mostrarResultados(execution) {
  const table = document.getElementById("tablaResultados");
  table.innerHTML = "<tr><th>Proceso</th><th>Inicio</th><th>Fin</th></tr>";
  execution.forEach(p => {
    table.innerHTML += `<tr><td>${p.name}</td><td>${p.start}</td><td>${p.finish}</td></tr>`;
  });
}

function mostrarCola(history) {
  const colaTable = document.getElementById("tablaCola");
  colaTable.innerHTML = "<tr><th>Tiempo</th><th>Ejecutando</th><th>Cola</th></tr>";
  history.forEach(h => {
    colaTable.innerHTML += `
      <tr>
        <td>${h.time}</td>
        <td>${h.executing}</td>
        <td>${h.queue.join(", ") || "Vacía"}</td>
      </tr>`;
  });
}


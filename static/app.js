const rowsContainer = document.getElementById("rows");
const addButton = document.getElementById("add-row");

function addRow() {
  const row = document.createElement("tr");
  row.innerHTML = `
    <td><input type="text" name="semana[]" placeholder="Semana 1" required /></td>
    <td><input type="text" name="dia[]" placeholder="2026/03/06" pattern="\\d{4}/\\d{2}/\\d{2}" required /></td>
    <td><input type="number" name="horas[]" min="0" step="1" required /></td>
    <td><input type="text" name="observaciones[]" placeholder="Actividades realizadas" /></td>
    <td><button type="button" class="delete-row">Eliminar</button></td>
  `;

  row.querySelector(".delete-row").addEventListener("click", () => row.remove());
  rowsContainer.appendChild(row);
}

addButton.addEventListener("click", addRow);
addRow();

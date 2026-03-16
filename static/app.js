const rowsContainer = document.getElementById("rows");
const addButton = document.getElementById("add-row");

function wireDeleteButton(button) {
  button.addEventListener("click", () => {
    const row = button.closest("tr");
    if (row) {
      row.remove();
    }
  });
}

function addRow() {
  const row = document.createElement("tr");
  row.innerHTML = `
    <td><input type="text" name="semana[]" placeholder="Semana 1" required /></td>
    <td><input type="text" name="dia[]" placeholder="2026/03/06" pattern="\\d{4}/\\d{2}/\\d{2}" required /></td>
    <td><input type="number" name="horas[]" min="0" step="1" required /></td>
    <td><input type="text" name="observaciones[]" placeholder="Actividades realizadas" /></td>
    <td><button type="button" class="delete-row">Eliminar</button></td>
  `;

  wireDeleteButton(row.querySelector(".delete-row"));
  rowsContainer.appendChild(row);
}

if (rowsContainer && addButton) {
  rowsContainer.querySelectorAll(".delete-row").forEach((button) => wireDeleteButton(button));
  addButton.addEventListener("click", addRow);

  if (rowsContainer.children.length === 0) {
    addRow();
  }
}

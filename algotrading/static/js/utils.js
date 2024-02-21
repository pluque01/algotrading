function addToSelection(itemId) {
  var selectedTable = document.getElementById("selectedResults");
  var searchTable = document.getElementById("searchResults");

  var itemToAdd = searchTable.querySelector("#" + itemId);
  itemToAdd.setAttribute("onclick", "removeFromSelection(id)");
  selectedTable.appendChild(itemToAdd);
}

function removeFromSelection(itemId) {
  var selectedTable = document.getElementById("selectedResults");

  selectedTable.querySelector("#" + itemId).remove();
}

function filterResults() {
  var selectedTableRows = document
    .getElementById("selectedResults")
    .querySelectorAll("tr");
  var searchTable = document.getElementById("searchResults");
  // If the element already exists in the selected table, remove it from the search results
  selectedTableRows.forEach(function (row) {
    var id = row.getAttribute("id");
    var item = searchTable.querySelector("#" + id);
    if (item) {
      item.remove();
    }
  });
}

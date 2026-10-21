(function () {
  var KEY = "scrollY";

  try {
    var saved = sessionStorage.getItem(KEY);
    if (saved !== null) {
      sessionStorage.removeItem(KEY);
      window.scrollTo(0, parseInt(saved, 10));
    }
  } catch (e) {}

  function save() {
    try { sessionStorage.setItem(KEY, String(window.scrollY)); } catch (e) {}
  }

  document.addEventListener("click", function (event) {
    if (event.target.closest("a.edit")) save();
  });
  document.addEventListener("submit", function (event) {
    if (event.target.id === "edit-form") save();
  });
})();

(function () {
  var combo = document.querySelector(".combo");
  var input = combo.querySelector("input");
  var list = combo.querySelector(".combo-list");
  var items = Array.prototype.slice.call(list.children);
  var active = -1;

  function visible() {
    return items.filter(function (li) { return !li.hidden; });
  }

  function setActive(index) {
    var shown = visible();
    shown.forEach(function (li) { li.classList.remove("active"); });
    active = shown.length ? (index + shown.length) % shown.length : -1;
    if (active >= 0) {
      shown[active].classList.add("active");
      shown[active].scrollIntoView({ block: "nearest" });
    }
  }

  function open() {
    var query = input.value.trim().toLowerCase();
    items.forEach(function (li) {
      li.hidden = li.textContent.toLowerCase().indexOf(query) === -1;
    });
    var any = visible().length > 0;
    list.hidden = !any;
    input.setAttribute("aria-expanded", any ? "true" : "false");
    setActive(-1);
  }

  function close() {
    list.hidden = true;
    input.setAttribute("aria-expanded", "false");
  }

  input.addEventListener("focus", open);
  input.addEventListener("input", open);
  input.addEventListener("blur", close);
  input.addEventListener("keydown", function (event) {
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      if (list.hidden) open();
      setActive(active + (event.key === "ArrowDown" ? 1 : -1));
      event.preventDefault();
    } else if (event.key === "Enter" && !list.hidden && active >= 0) {
      input.value = visible()[active].textContent;
      close();
      event.preventDefault();
    } else if (event.key === "Escape") {
      close();
    }
  });
  list.addEventListener("mousedown", function (event) {
    if (event.target.tagName === "LI") {
      input.value = event.target.textContent;
      close();
      event.preventDefault();
    }
  });
})();

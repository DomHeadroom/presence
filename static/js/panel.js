function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie != "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie("csrftoken");

async function fetchWithCsrf(url, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("X-CSRFToken", csrftoken);
  options.headers = headers;

  const response = await fetch(url, options);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response;
}

const strings = {
  suffixAgo: "fa",
  suffixFromNow: "da ora",
  seconds: "meno di un minuto",
  minute: "circa un minuto",
  minutes: "%d minuti",
  hour: "circa un'ora",
  hours: "circa %d ore",
  day: "un giorno",
  days: "%d giorni",
  month: "circa un mese",
  months: "%d mesi",
  year: "circa un anno",
  years: "%d anni",
  open: "aperta",
  closed: "chiusa",
  ring: "suona",
  error: "errore",
};

function timeAgo(dateAttr) {
  const date = new Date(dateAttr);
  if (isNaN(date.getTime())) return; // Handle invalid dates

  const now = new Date();
  const isPast = date.getTime() < now.getTime();
  const diff = Math.abs(date.getTime() - now.getTime()); // Absolute difference in milliseconds
  const seconds = diff / 1000;
  const minutes = seconds / 60;
  const hours = minutes / 60;
  const days = hours / 24;
  const months = days / 30.4368; // Average days per month
  const years = days / 365.242; // Average days per year

  let timeString;
  let units;
  let unitValue;

  if (seconds < 45) {
    timeString = strings.seconds;
  } else if (seconds < 90) {
    timeString = strings.minute;
  } else if (minutes < 45) {
    units = strings.minutes;
    unitValue = Math.round(minutes);
  } else if (minutes < 90) {
    timeString = strings.hour;
  } else if (hours < 24) {
    units = strings.hours;
    unitValue = Math.round(hours);
  } else if (hours < 48) {
    timeString = strings.day;
  } else if (days < 30) {
    units = strings.days;
    unitValue = Math.floor(days);
  } else if (days < 60) {
    timeString = strings.month;
  } else if (days < 365) {
    units = strings.months;
    unitValue = Math.floor(months);
  } else if (years < 2) {
    timeString = strings.year;
  } else {
    units = strings.years;
    unitValue = Math.floor(years);
  }

  // Apply the unit value if applicable
  if (units) {
    timeString = units.replace(/%d/i, unitValue);
  }
  // Append the suffix
  const suffix = isPast ? strings.suffixAgo : strings.suffixFromNow;
  return `${timeString} ${suffix}`;
}

function setError(label_id) {
  const label = document.querySelector(label_id);
  label.classList.remove("label-default", "label-warning", "label-success");
  label.classList.add("label-danger");
  label.innerText = strings.error;
}

async function openExternal() {
  try {
    const header = await fetchWithCsrf("/gates/external/open/", { method: "POST" });
    const body = await header.json();
    if (body) waitRing(body);
  } catch (e) {
    setError("#external-status");
  }
}

async function openInternal() {
  document.getElementById("internal-button").disabled = true;
  try {
    await fetchWithCsrf("/gates/internal/open/", { method: "POST" });
  } catch (e) {
    setError("#internal-status");
    document.getElementById("internal-button").disabled = false;
  }
}

function updateLabel(label_id, state) {
  const label = document.querySelector(label_id);
  label.classList.remove(
    "label-default",
    "label-warning",
    "label-success",
    "label-danger",
  );
  label.innerText = strings[state.description];

  if (state.id == 0) label.classList.add("label-default");
  else if (state.id == 1) label.classList.add("label-success");
  else label.classList.add("label-warning");
}

function waitRing(response) {
  document.querySelector("#external-button").disabled = true;
  const endpoint = "/gates/external/" + "?req_id=" + response.req_id;
  const interval = setInterval(async function () {
    try {
      const header = await fetchWithCsrf(endpoint);
      const response = await header.json();
      updateLabel("#external-status", response);
      if (response.pending == false) clearInterval(interval);
    } catch (e) {
      setError("#external-status");
      document.querySelector("#external-button").disabled = true;
    }
  }, 1000);
}

async function update() {
  try {
    const headerGates = await fetch("/gates/");
    const bodyGates = await headerGates.json();
    for (const gate of bodyGates) {
      const [name, state] = Object.entries(gate)[0];
      const labelId = name === "internal" ? "#internal-status" : "#external-status";
      updateLabel(labelId, state);
      if (name === "internal") {
        const button = document.getElementById("internal-button");
        const allowed = button.dataset.allowed === "true";
        button.disabled = !allowed || state.id === 1;
      }
    }
  } catch (e) {
    console.error(e);
    setError("#internal-status");
    setError("#external-status");
  }

  try {
    const headerReqInternal = await fetch("/requests/internal/?limit=5");
    const bodyReqInternal = await headerReqInternal.json();
    document.querySelector("#requests").innerHTML = bodyReqInternal
      .map((resp) => {
        const user = `<div class="user">${resp.user}</div>`;
        const date = `<div class="timeago" >${timeAgo(resp.time)}</div>`;
        const entry = `<div class="entry">${user}${date}</div>`;
        return entry;
      })
      .join("");
  } catch (e) {
    console.error(e);
  }
}

window.addEventListener("load", () => {
  update();
  setInterval(update, 5000);
  document.querySelector(".navbar-toggle").onclick = () => {
    document.querySelector("#navbar").classList.toggle("collapse");
  };
});

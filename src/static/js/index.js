const setOpenHeading = () => {
  document.querySelector(".cover-heading").innerText = "Aperto";
  document.querySelector("#info").style.display = "";
};
const setClosedHeading = () => {
  document.querySelector(".cover-heading").innerText = "Chiuso";
  document.querySelector("#info").style.display = "none";
};
const setErrorHeading = () => {
  document.querySelector(".cover-heading").innerText = "Errore";
  document.querySelector("#info").style.display = "none";
};
const update = async () => {
  try {
    const header = await fetch("/gates/internal/");
    const body = await header.json();
    if (body.id == 1) setOpenHeading();
    else setClosedHeading();
  } catch (error) {
    setErrorHeading();
  }
};

window.addEventListener("load", () => {
  document.querySelector("#info").style.display = "none";
  update();
  setInterval(update, 5000);
});

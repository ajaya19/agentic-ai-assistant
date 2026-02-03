const userText = document.getElementById("userText");
const aiText = document.getElementById("aiText");
const userBox = document.getElementById("userBox");
const aiBox = document.getElementById("aiBox");
const listening = document.getElementById("listening");
const waveform = document.getElementById("waveform");
const siri = document.getElementById("siri");

function startListening() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();

  recognition.lang = "en-IN";
  recognition.start();

  listening.classList.remove("hidden");
  waveform.classList.remove("hidden");
  siri.classList.remove("hidden");

  recognition.onresult = function(event) {
    const text = event.results[0][0].transcript;

    listening.classList.add("hidden");
    waveform.classList.add("hidden");
    siri.classList.add("hidden");

    userText.innerText = text;
    userBox.classList.remove("hidden");

    fetch("/command", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ text })
    })
    .then(res => res.json())
    .then(data => {
      aiText.innerText = data.reply;
      aiBox.classList.remove("hidden");
      speak(data.reply);
    });
  };

  recognition.onerror = () => {
    listening.classList.add("hidden");
    waveform.classList.add("hidden");
    siri.classList.add("hidden");
  };
}

function speak(msg) {
  const utter = new SpeechSynthesisUtterance(msg);
  utter.lang = "en-IN";
  window.speechSynthesis.speak(utter);
}
function sendTextCommand() {
  const input = document.getElementById("textCommand");
  const text = input.value.trim();

  if (text === "") return;

  // Show user bubble
  userText.innerText = text;
  userBox.classList.remove("hidden");

  fetch("/command", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  })
  .then(res => res.json())
  .then(data => {
    aiText.innerText = data.reply;
    aiBox.classList.remove("hidden");
    speak(data.reply); // voice reply (optional)
  });

  input.value = "";
}
